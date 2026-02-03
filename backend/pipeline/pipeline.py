import logging
import os
import traceback

from ray import serve
from ray.serve.handle import DeploymentHandle

from backend.video.services.video_job_service import VideoJobService
from backend.storage.services.video_storage_service import VideoStorageService
from backend.config.management import ConfigManager, ConfigType
from backend.pipeline.schemas import (
    VideoParameters,
)
from backend.pipeline.utilities.parameter_conversion import (
    to_preprocessor_input,
    to_generator_params,
    to_interpolator_input,
    to_upscaler_input,
    to_postprocessor_params
)
from backend.deployment.initialization import initialize_deployment


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 5,
        "target_num_ongoing_requests_per_replica": 1,
        "metrics_interval_s": 10,
        "look_back_period_s": 30,
        "downscale_delay_s": 300,
        "upscale_delay_s": 30,
    },
    ray_actor_options={"num_cpus": 0.1}
)
class VideoGenerationPipeline:
    """
    Autoscaled video generation pipeline using Ray Serve deployments.
    
    This pipeline orchestrates autoscaled components for video generation,
    interpolation, upscaling, and post-processing with cancellation support.
    """

    def __init__(self, config_manager: ConfigManager,
                 generator_handle: DeploymentHandle,
                 interpolator_handle: DeploymentHandle,
                 upscaler_handle: DeploymentHandle,
                 preprocessor_handle: DeploymentHandle,
                 postprocessor_handle: DeploymentHandle):
        
        initialize_deployment()

        from backend.storage.factories import create_video_storage_service
        from backend.video.factories.services import create_video_job_service
        self.video_job_service = create_video_job_service()
        self.video_storage_service = create_video_storage_service()
        self.generator_handle = generator_handle
        self.interpolator_handle = interpolator_handle
        self.upscaler_handle = upscaler_handle
        self.preprocessor_handle = preprocessor_handle
        self.postprocessor_handle = postprocessor_handle

        config = config_manager.get_config(ConfigType.PIPELINE)
        self.logging_enabled = config.get("logging_enabled", True)
        self.output_dir = config.get("output_dir", "outputs")
        self.progress_config = config.get("progress_percentages", {})
        
        self._ensure_output_dir_exists()

    def _ensure_output_dir_exists(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)

    def _log(self, message: str, level: int = logging.INFO) -> None:
        """Log message if logging is enabled."""
        if self.logging_enabled:
            logging.log(level, f"[AutoscaledPipeline] {message}")

    def _get_param_representation(self, params_obj) -> str:
        """Helper to get a string representation of parameters for logging."""
        if hasattr(params_obj, "model_dump") and callable(getattr(params_obj, "model_dump")):
            try:
                return str(params_obj.model_dump(exclude_none=True))
            except Exception:
                return str(params_obj)
        elif hasattr(params_obj, "dict") and callable(getattr(params_obj, "dict")):
            try:
                return str(params_obj.dict(exclude_none=True))
            except Exception:
                return str(params_obj)
        return str(params_obj)

    def _calculate_progress_ranges(self, needs_interpolation: bool, needs_upscaling: bool) -> dict:
        """
        Calculate dynamic progress percentage ranges based on active pipeline stages.

        When interpolation or upscaling are skipped, their time is redistributed to generation.

        Args:
            needs_interpolation: Whether interpolation stage is active
            needs_upscaling: Whether upscaling stage is active

        Returns:
            Dictionary with start/end progress for each stage
        """

        preprocessing_pct = self.progress_config.get("preprocessing", 1)
        base_generation_pct = self.progress_config.get("generation", 70)
        base_interpolation_pct = self.progress_config.get("interpolation", 14)
        base_upscaling_pct = self.progress_config.get("upscaling", 14)
        saving_pct = self.progress_config.get("saving", 1)

        interpolation_pct = base_interpolation_pct if needs_interpolation else 0
        upscaling_pct = base_upscaling_pct if needs_upscaling else 0

        # Redistribute unused time to generation
        redistributed = (base_interpolation_pct if not needs_interpolation else 0) + (base_upscaling_pct if not needs_upscaling else 0)
        generation_pct = base_generation_pct + redistributed

        # Calculate cumulative ranges
        preprocessing_end = preprocessing_pct
        generation_start = preprocessing_end
        generation_end = generation_start + generation_pct

        interpolation_start = generation_end
        interpolation_end = interpolation_start + interpolation_pct

        upscaling_start = interpolation_end
        upscaling_end = upscaling_start + upscaling_pct

        saving_start = upscaling_end
        saving_end = saving_start + saving_pct

        return {
            "preprocessing": {"start": 0, "end": preprocessing_end},
            "generation": {"start": generation_start, "end": generation_end},
            "interpolation": {"start": interpolation_start, "end": interpolation_end},
            "upscaling": {"start": upscaling_start, "end": upscaling_end},
            "saving": {"start": saving_start, "end": saving_end},
        }

    async def generate_video(self, params: VideoParameters, job_id: str) -> None:
        """
        Generate video asynchronously using autoscaled deployments.

        Args:
            params: Generation parameters
            job_id: Unique job identifier
        """
        local_video_path = None

        try:
            if not self.video_job_service.mark_job_as_processing(job_id):
                return

            local_video_path = await self._execute_video_generation(params, job_id)

            if local_video_path is None:
                self._log(f"Job {job_id} was cancelled during generation", level=logging.INFO)
                return

            if not local_video_path or not os.path.exists(local_video_path):
                raise RuntimeError("Video generation failed - no output file produced")

            self.video_job_service.update_job_progress(job_id, 95, "Uploading to storage")

            object_key, file_size = self.video_storage_service.upload_video(local_video_path, job_id)
            bucket_name = self.video_storage_service.get_bucket_name()
            self.video_job_service.save_generation_result(job_id, object_key, bucket_name, file_size)

            self.video_job_service.update_job_progress(job_id, 100, "Completed")
            self.video_job_service.mark_job_as_completed(job_id)

            self._log(f"Job {job_id} completed successfully. Video uploaded to {bucket_name}/{object_key}")

        except Exception as e:
            if self.video_job_service.is_job_cancelled(job_id):
                self._log(f"Job {job_id} was cancelled", level=logging.INFO)
            else:
                self._log(f"Job {job_id} failed: {str(e)}", level=logging.ERROR)
                self._log(f"Job {job_id} traceback: {traceback.format_exc()}", level=logging.ERROR)
                self.video_job_service.mark_job_as_failed(job_id)
                self.video_job_service.update_error_message(job_id, str(e))

        finally:
            if local_video_path and os.path.exists(local_video_path):
                try:
                    self.video_storage_service.cleanup_local_file(local_video_path)
                except Exception as e:
                    self._log(f"Error cleaning up file {local_video_path}: {e}", level=logging.WARNING)

    async def _execute_video_generation(self, params: VideoParameters, job_id: str) -> str:
        """
        Execute the video generation workflow using autoscaled deployment components.

        This method coordinates the flow of data between components:
        1. Preprocess parameters
        2. Generate base frames
        3. Interpolate frames (if needed)
        4. Upscale frames (if needed)
        5. Post-process and save video

        Args:
            params: Video generation parameters
            job_id: Job identifier for progress tracking

        Returns:
            Path to generated video file
        """
        self._log(f"Job {job_id}: Starting video generation")

        # Step 1: Preprocess parameters
        self.video_job_service.update_job_progress(job_id, 1, "Processing parameters")

        preprocessor_input = to_preprocessor_input(params)

        preprocessor_output = await self.preprocessor_handle.process.remote(
            preprocessor_input, job_id
        )

        if preprocessor_output is None:
            self._log(f"Job {job_id}: Preprocessing was cancelled")
            return None

        needs_interpolation = preprocessor_output.fps_factor > 1
        needs_upscaling = preprocessor_output.frame_scale_factor > 1
        progress_ranges = self._calculate_progress_ranges(needs_interpolation, needs_upscaling)

        self._log(f"Job {job_id}: Progress ranges - Generation: {progress_ranges['generation']['start']}-{progress_ranges['generation']['end']}%, "
                  f"Interpolation: {progress_ranges['interpolation']['start']}-{progress_ranges['interpolation']['end']}%, "
                  f"Upscaling: {progress_ranges['upscaling']['start']}-{progress_ranges['upscaling']['end']}%")

        # Step 2: Generate base frames
        generation_params = to_generator_params(params, preprocessor_output)

        base_frames = await self.generator_handle.generate.remote(
            generation_params,
            job_id,
            progress_ranges['generation']['start'],
            progress_ranges['generation']['end']
        )

        if base_frames is None:
            self._log(f"Job {job_id}: Generation was cancelled")
            return None

        if not base_frames:
            raise RuntimeError("Video generation failed: No frames were generated by the core generator")

        self._log(f"Job {job_id}: Generated {len(base_frames)} base frames at 8 FPS")

        processed_frames = base_frames

        # Step 3: Frame interpolation (if needed)
        if needs_interpolation:
            self.video_job_service.update_job_progress(
                job_id,
                progress_ranges['interpolation']['start'],
                "Starting frame interpolation"
            )
            self._log(f"Job {job_id}: Starting frame interpolation - factor {preprocessor_output.fps_factor}x")

            interpolator_input = to_interpolator_input(
                processed_frames,
                preprocessor_output.fps_factor
            )

            processed_frames = await self.interpolator_handle.interpolate.remote(
                interpolator_input,
                job_id,
                progress_ranges['interpolation']['start'],
                progress_ranges['interpolation']['end']
            )

            if processed_frames is None:
                self._log(f"Job {job_id}: Interpolation was cancelled")
                return None

            self._log(f"Job {job_id}: Interpolated to {len(processed_frames)} frames")
        else:
            self._log(f"Job {job_id}: Skipping frame interpolation (fps_factor is 1)")

        # Step 4: Frame upscaling (if needed)
        if needs_upscaling:
            self.video_job_service.update_job_progress(
                job_id,
                progress_ranges['upscaling']['start'],
                "Starting frame upscaling"
            )
            self._log(f"Job {job_id}: Starting frame upscaling - factor {preprocessor_output.frame_scale_factor}x")

            upscaler_input = to_upscaler_input(
                processed_frames,
                preprocessor_output.frame_scale_factor
            )

            processed_frames = await self.upscaler_handle.upscale.remote(
                upscaler_input,
                job_id,
                progress_ranges['upscaling']['start'],
                progress_ranges['upscaling']['end']
            )

            if processed_frames is None:
                self._log(f"Job {job_id}: Upscaling was cancelled")
                return None

            if processed_frames and base_frames:
                original_size = f"{base_frames[0].width}x{base_frames[0].height}"
                upscaled_size = f"{processed_frames[0].width}x{processed_frames[0].height}"
                self._log(f"Job {job_id}: Upscaled from {original_size} to {upscaled_size}")
        else:
            self._log(f"Job {job_id}: Skipping frame upscaling (frame_scale_factor is 1)")

        if not processed_frames:
            raise RuntimeError("Video generation failed: No frames available for saving")

        # Step 5: Post-process and save video
        self.video_job_service.update_job_progress(
            job_id,
            progress_ranges['saving']['start'],
            "Post-processing and saving video"
        )

        final_fps = 8 * preprocessor_output.fps_factor

        postprocessor_params = to_postprocessor_params(
            processed_frames,
            params,
            final_fps,
            self.output_dir
        )

        final_output_path = await self.postprocessor_handle.postprocess.remote(
            postprocessor_params, job_id
        )

        if final_output_path is None:
            self._log(f"Job {job_id}: Postprocessing was cancelled")
            return None

        self._log(f"Job {job_id}: Video saved to: {final_output_path}")
        return final_output_path
