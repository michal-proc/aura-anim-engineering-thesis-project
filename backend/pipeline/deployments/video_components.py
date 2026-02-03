from ray import serve
import logging

from backend.deployment.initialization import initialize_deployment
from backend.pipeline.deployments.mixins import (
    GPUDeploymentMixin,
    CPUDeploymentMixin,
)
from backend.pipeline.schemas import (
    VideoGeneratorParams,
    FrameInterpolatorInput,
    FrameUpscalerInput,
    VideoPreprocessorInput,
    VideoPreprocessorOutput,
    VideoPostprocessorParams,

)
from backend.video.factories.services import create_video_job_service
from PIL import Image


logger = logging.getLogger(__name__)


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 1,
        "target_num_ongoing_requests_per_replica": 1,
        "metrics_interval_s": 10,
        "look_back_period_s": 30,
        "downscale_delay_s": 600,
        "upscale_delay_s": 30,
    },
    ray_actor_options={"num_gpus": 0.1, "num_cpus": 0.1}
)
class VideoGeneratorDeployment(GPUDeploymentMixin):
    """Autoscaling video generator with cancellation support"""
    
    def __init__(self):
        initialize_deployment()
        super().__init__()

        from backend.pipeline.components.video_generator import VideoGenerator
        self.generator = VideoGenerator(enable_logging=True)
        
        logger.info(f"VideoGeneratorDeployment initialized on replica {self._replica_id}")
    
    async def generate(self, params: VideoGeneratorParams, job_id: str, progress_start: int = 1, progress_end: int = 99) -> list[Image.Image]:
        """
        Generate video frames with cancellation support.
        
        Args:
            params: Video generation parameters
            job_id: Job identifier for tracking
            progress_start: Starting progress percentage for this stage
            progress_end: Ending progress percentage for this stage

        Returns:
            List of generated frames
        """
        logger.info(f"Generating frames for job {job_id} on replica {self._replica_id}")

        self.generator.set_cancellation_callback(
            lambda: self._check_job_cancelled(job_id)
        )

        last_reported_progress = [0]

        def progress_callback(current_step: int, total_steps: int):
            video_job_service = create_video_job_service()

            # Calculate progress within the range
            # current_step goes from 0 to total_steps-1
            fraction = current_step / (total_steps - 1) if total_steps > 1 else 1.0
            progress = int(progress_start + fraction * (progress_end - progress_start))

            step_message = f"Generating frames ({current_step + 1}/{total_steps})"

            if progress > last_reported_progress[0] or current_step == total_steps - 1:
                video_job_service.update_job_progress(job_id, progress, step_message)
                last_reported_progress[0] = progress
                logger.info(f"Progress update for {job_id}: {progress}% (step {current_step + 1}/{total_steps})")

        self.generator.set_progress_callback(progress_callback)

        try:
            return self._handle_gpu_operation_with_cancellation(
                job_id,
                "frame generation",
                self.generator.generate,
                params
            )
        finally:
            self.generator.set_cancellation_callback(None)
            self.generator.set_progress_callback(None)


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 5,
        "target_num_ongoing_requests_per_replica": 1,
        "metrics_interval_s": 10,
        "look_back_period_s": 30,
        "downscale_delay_s": 300,
        "upscale_delay_s": 15,
    },
    ray_actor_options={"num_gpus": 0.1, "num_cpus": 0.1}
)
class FrameInterpolatorDeployment(GPUDeploymentMixin):
    """Autoscaling frame interpolator with cancellation support"""
    
    def __init__(self):
        initialize_deployment()
        super().__init__()

        from backend.pipeline.components.frame_interpolator import FrameInterpolator
        self.interpolator = FrameInterpolator(enable_logging=True)
        
        logger.info(f"FrameInterpolatorDeployment initialized on replica {self._replica_id}")
    
    async def interpolate(self, params: FrameInterpolatorInput, job_id: str, progress_start: int = 71, progress_end: int = 85) -> list[Image.Image]:
        """Interpolate frames with cancellation support"""
        logger.info(f"Interpolating frames for job {job_id} on replica {self._replica_id}")

        self.interpolator.set_cancellation_callback(
            lambda: self._check_job_cancelled(job_id)
        )

        def progress_callback(current_frame: int, total_frames: int):
            video_job_service = create_video_job_service()

            progress = progress_start + (progress_end - progress_start) // 2
            step_message = f"Interpolating frames ({current_frame}/{total_frames})"

            video_job_service.update_job_progress(job_id, progress, step_message)
            logger.info(f"Interpolation progress for {job_id}: {progress}% (frame {current_frame}/{total_frames})")

        self.interpolator.set_progress_callback(progress_callback)

        try:
            return self._handle_gpu_operation_with_cancellation(
                job_id,
                "frame interpolation",
                self.interpolator.interpolate,
                params,
            )
        finally:
            self.interpolator.set_cancellation_callback(None)
            self.interpolator.set_progress_callback(None)


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 4,
        "target_num_ongoing_requests_per_replica": 1,
        "metrics_interval_s": 10,
        "look_back_period_s": 30,
        "downscale_delay_s": 300,
        "upscale_delay_s": 15,
    },
    ray_actor_options={"num_gpus": 0.1, "num_cpus": 0.1}
)
class FrameUpscalerDeployment(GPUDeploymentMixin):
    """Autoscaling frame upscaler with cancellation support"""
    
    def __init__(self):
        initialize_deployment()
        super().__init__()

        from backend.pipeline.components.frame_upscaler import FrameUpscaler
        self.upscaler = FrameUpscaler(enable_logging=True)
        
        logger.info(f"FrameUpscalerDeployment initialized on replica {self._replica_id}")
    
    async def upscale(self, params: FrameUpscalerInput, job_id: str, progress_start: int = 85, progress_end: int = 99) -> list[Image.Image]:
        """Upscale frames with cancellation support"""
        logger.info(f"Upscaling frames for job {job_id} on replica {self._replica_id} (progress: {progress_start}-{progress_end}%)")

        self.upscaler.set_cancellation_callback(
            lambda: self._check_job_cancelled(job_id)
        )

        def progress_callback(current_frame: int, total_frames: int):
            video_job_service = create_video_job_service()

            progress = progress_start + (progress_end - progress_start) // 2
            step_message = f"Upscaling frames ({current_frame}/{total_frames})"

            video_job_service.update_job_progress(job_id, progress, step_message)
            logger.info(f"Upscaling progress for {job_id}: {progress}% (frame {current_frame}/{total_frames})")

        self.upscaler.set_progress_callback(progress_callback)

        try:
            return self._handle_gpu_operation_with_cancellation(
                job_id,
                "frame upscaling",
                self.upscaler.upscale,
                params,
            )
        finally:
            self.upscaler.set_cancellation_callback(None)
            self.upscaler.set_progress_callback(None)


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 3,
        "target_num_ongoing_requests_per_replica": 1,
        "metrics_interval_s": 10,
        "look_back_period_s": 30,
        "downscale_delay_s": 180,
        "upscale_delay_s": 10,
    },
    ray_actor_options={"num_cpus": 0.1}
)
class VideoPreprocessorDeployment(CPUDeploymentMixin):
    """Autoscaling video preprocessor"""
    
    def __init__(self):
        initialize_deployment()
        super().__init__()

        from backend.pipeline.components.video_preprocessor import VideoPreprocessor
        self.preprocessor = VideoPreprocessor(enable_logging=True)
        
        logger.info(f"VideoPreprocessorDeployment initialized on replica {self._replica_id}")
    
    async def process(self, params: VideoPreprocessorInput, job_id: str) -> VideoPreprocessorOutput:
        """Process parameters for video generation"""
        logger.info(f"Processing parameters for job {job_id} on replica {self._replica_id}")
        
        return self._handle_cpu_operation_with_cancellation(
            job_id,
            "parameter processing",
            self.preprocessor.process,
            params,
        )


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 3,
        "target_num_ongoing_requests_per_replica": 1,
        "metrics_interval_s": 10,
        "look_back_period_s": 30,
        "downscale_delay_s": 180,
        "upscale_delay_s": 10,
    },
    ray_actor_options={"num_cpus": 0.1}
)
class VideoPostprocessorDeployment(CPUDeploymentMixin):
    """Autoscaling video postprocessor with cancellation support"""
    
    def __init__(self):
        initialize_deployment()
        super().__init__()

        from backend.pipeline.components.video_postprocessor import VideoPostprocessor
        self.postprocessor = VideoPostprocessor(enable_logging=True)
        
        logger.info(f"VideoPostprocessorDeployment initialized on replica {self._replica_id}")
    
    async def postprocess(self, params: VideoPostprocessorParams, job_id: str) -> str:
        """Postprocess the video"""
        logger.info(f"Postprocessing video for job {job_id} on replica {self._replica_id}")

        return self._handle_cpu_operation_with_cancellation(
            job_id=job_id,
            operation_name="postprocessing",
            operation_func=self.postprocessor.postprocess,
            params=params,
        )
