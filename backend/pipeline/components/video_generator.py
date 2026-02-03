import torch
import logging
import traceback
import gc
from typing import List, Optional, Callable, Dict, Any
from diffusers import AnimateDiffPipeline, DDIMScheduler, MotionAdapter
from PIL import Image

from backend.config.management import ConfigManager
from backend.config.management.config_type import ConfigType
from backend.pipeline.schemas.component_parameters import VideoParameters, VideoGeneratorParams
from backend.pipeline.deployments.exceptions import CancellationException


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class VideoGenerator:
    """
    Generates base video frames using AnimateDiff.
    
    Public Methods:
        - apply_defaults(params: VideoParameters) -> VideoGeneratorParams
        - generate(params: VideoGeneratorParams) -> List[Image.Image]
    """
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging

        config_manager = ConfigManager(enable_logging=enable_logging)
        config = config_manager.get_config(ConfigType.VIDEO_GENERATOR)

        self.base_models = config.get("base_models", {})
        self.motion_adapters = config.get("motion_adapters", {})
        self.lora_presets = config.get("lora_presets", {})
        self.pipeline_config = config.get("pipeline_config", {})

        self.default_fps = self.pipeline_config.get("default_fps", 8)
        self.enable_free_noise = config.get("enable_free_noise", False)
        self.free_noise_context_length = config.get("free_noise_context_length", 16)
        self.free_noise_context_stride = config.get("free_noise_context_stride", 4)
        self.dimension_alignment = config.get("dimension_alignment", 8)
        self.cancellation_check_callback: Optional[Callable[[], bool]] = None
        self.progress_callback: Optional[Callable[[int, int], None]] = None

        self._log(f"VideoGenerator initialized with {len(self.base_models)} base models")
    
    def _log(self, message: str, level: int = logging.INFO) -> None:
        if self.enable_logging:
            logging.log(level, f"[VideoGenerator] {message}")

    def set_cancellation_callback(self, callback: Callable[[], bool]) -> None:
        self.cancellation_check_callback = callback

    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        self.progress_callback = callback
    
    def generate(self, params: VideoGeneratorParams) -> List[Image.Image]:
        """
        Generate video frames.
        
        Args:
            params: Video generation parameters
            
        Returns:
            List of generated PIL Image frames
        """
        self._log(f"Generating video: {params.prompt[:50]}...")
        
        if not torch.cuda.is_available():
            self._log("CUDA not available, generation will be slow", level=logging.WARNING)
        
        if params.base_model not in self.base_models:
            raise ValueError(
                f"Invalid base_model: {params.base_model}. "
                f"Available: {list(self.base_models.keys())}"
            )
        
        try:
            pipe = self._initialize_pipeline(params)
            pipe = self._configure_scheduler(pipe, params)
            loras_to_load = self._prepare_loras_to_load(params)
            lora_names, lora_weights = self._load_loras(pipe, loras_to_load)
            pipe = self._apply_loras(pipe, lora_names, lora_weights)
            pipe = self._optimize_pipeline(pipe, params)
            
            num_frames = params.video_length * self.default_fps
            self._log(f"Generating {num_frames} frames at {self.default_fps} FPS")
            
            generated_frames = self._run_generation(pipe, params, num_frames)

            return generated_frames

        except CancellationException:
            self._log("Generation cancelled", level=logging.INFO)
            raise
        except Exception as e:
            self._log(f"Generation failed: {e}", level=logging.ERROR)
            self._log(traceback.format_exc(), level=logging.ERROR)
            raise RuntimeError(f"Video generation failed: {e}")

        finally:
            if 'pipe' in locals():
                try:
                    pipe.to('cpu')
                except Exception:
                    pass
                del pipe

            gc.collect()

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            self._log("Memory cleanup completed")
    
    def _initialize_pipeline(self, params: VideoGeneratorParams) -> AnimateDiffPipeline:
        """Initialize AnimateDiff pipeline."""
        base_model_info = self.base_models[params.base_model]

        motion_adapter_path = params.motion_adapter
        if motion_adapter_path == "default":
            motion_adapter_path = self.motion_adapters.get("default", "guoyww/animatediff-motion-adapter-v1-5-2")

        adapter = MotionAdapter.from_pretrained(
            motion_adapter_path, torch_dtype=torch.float16
        )
        
        kwargs = {
            "pretrained_model_name_or_path": base_model_info["name"],
            "motion_adapter": adapter,
            "torch_dtype": torch.float16,
        }

        if variant := base_model_info.get("variant"):
            kwargs["variant"] = variant
            
        pipe = AnimateDiffPipeline.from_pretrained(**kwargs)
        pipe = pipe.to('cpu')

        return pipe
    
    def _configure_scheduler(
        self, pipe: AnimateDiffPipeline, params: VideoGeneratorParams
    ) -> AnimateDiffPipeline:
        """Configure DDIM scheduler."""
        base_model_info = self.base_models[params.base_model]
        try:
            scheduler = DDIMScheduler.from_pretrained(
                base_model_info["name"],
                subfolder="scheduler",
                torch_dtype=torch.float16,
                clip_sample=False,
                beta_schedule="linear",
                timestep_spacing="linspace",
                steps_offset=1,
            )
            pipe.scheduler = scheduler
        except Exception as e:
            self._log(f"Failed to load DDIM scheduler: {e}", level=logging.WARNING)
        
        return pipe
    
    def _get_loras_mapping(self) -> dict[str, str]:
        return {
            preset: meta["id"]
            for preset, meta in self.lora_presets.items()
            if "id" in meta
        }
    
    def _prepare_loras_to_load(self, params: VideoGeneratorParams) -> dict[str, float]:
        short_map = self._get_loras_mapping()
        loras = {}
        
        if params.loras:
            for key, val in params.loras.items():
                if key in short_map:
                    loras[short_map[key]] = float(val)
                else:
                    self._log(f"Unknown LoRA preset: {key}", level=logging.WARNING)
        
        return loras
    
    def _load_loras(
        self, pipe: AnimateDiffPipeline, loras: dict[str, float]
    ) -> tuple[list[str], list[float]]:
        names, weights = [], []
        
        for lora_id, weight in loras.items():
            try:
                adapter_name = (
                    lora_id.replace("/", "_").replace("-", "_").replace(".", "_")
                )
                pipe.load_lora_weights(
                    lora_id, 
                    adapter_name=adapter_name, 
                    torch_dtype=torch.float16,
                )
                names.append(adapter_name)
                weights.append(weight)
                self._log(f"Loaded LoRA: {lora_id}")
            except Exception as e:
                self._log(f"Cannot load LoRA {lora_id}: {e}", level=logging.WARNING)
        
        return names, weights
    
    def _apply_loras(
        self, pipe: AnimateDiffPipeline, names: list[str], weights: list[float]
    ) -> AnimateDiffPipeline:
        if names:
            pipe.set_adapters(names, adapter_weights=weights)
            self._log(f"Applied {len(names)} LoRA adapters")
        
        return pipe
    
    def _optimize_pipeline(
        self, pipe: AnimateDiffPipeline, params: VideoGeneratorParams
    ) -> AnimateDiffPipeline:
        """Optimize pipeline for performance."""
        pipe.enable_vae_slicing()
        pipe.enable_model_cpu_offload()
        
        try:
            has_lora = False
            if hasattr(pipe.unet, 'peft_config') and pipe.unet.peft_config:
                has_lora = True
                self._log("LoRA detected, skipping FreeNoise")
            
            if not has_lora and self.enable_free_noise:
                pipe.enable_free_noise(
                    context_length=self.free_noise_context_length,
                    context_stride=self.free_noise_context_stride
                )
                self._log(f"FreeNoise enabled (context_length={self.free_noise_context_length}, context_stride={self.free_noise_context_stride})")
        except Exception as e:
            self._log(f"Failed to enable FreeNoise: {e}", level=logging.WARNING)
        
        return pipe
    
    def _progress_callback_wrapper(
        self,
        pipe: AnimateDiffPipeline,
        step_index: int,
        timestep: int,
        callback_kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Callback executed after each denoising step.
        Reports progress if callback is set.
        """
        if self.progress_callback:
            total_steps = getattr(self, '_total_inference_steps', step_index + 1)
            self.progress_callback(step_index, total_steps)

        return callback_kwargs

    def _cancellation_callback_wrapper(
        self,
        pipe: AnimateDiffPipeline,
        step_index: int,
        timestep: int,
        callback_kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Callback executed after each denoising step.
        Checks for cancellation and raises exception if needed.
        """
        if self.cancellation_check_callback and self.cancellation_check_callback():
            self._log(f"Cancellation detected at step {step_index}/{timestep}", level=logging.WARNING)
            raise CancellationException(f"Generation cancelled at denoising step {step_index}")

        return callback_kwargs

    def _combined_callback_wrapper(
        self,
        pipe: AnimateDiffPipeline,
        step_index: int,
        timestep: int,
        callback_kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Combined callback for both progress and cancellation.
        """
        callback_kwargs = self._progress_callback_wrapper(pipe, step_index, timestep, callback_kwargs)
        callback_kwargs = self._cancellation_callback_wrapper(pipe, step_index, timestep, callback_kwargs)
        return callback_kwargs

    def _run_generation(
        self,
        pipe: AnimateDiffPipeline,
        params: VideoGeneratorParams,
        num_frames: int,
    ) -> List[Image.Image]:
        """Run the actual frame generation."""
        generator = torch.Generator(device="cpu").manual_seed(params.seed)

        width = (params.video_width // self.dimension_alignment) * self.dimension_alignment
        height = (params.video_height // self.dimension_alignment) * self.dimension_alignment

        if width != params.video_width or height != params.video_height:
            self._log(
                f"Adjusted dimensions: {params.video_width}x{params.video_height} "
                f"-> {width}x{height}"
            )

        self._total_inference_steps = params.inference_steps

        callback = self._combined_callback_wrapper

        output = pipe(
            prompt=params.prompt,
            negative_prompt=params.negative_prompt,
            num_frames=num_frames,
            guidance_scale=params.guidance_scale,
            num_inference_steps=params.inference_steps,
            generator=generator,
            height=height,
            width=width,
            callback_on_step_end=callback,
        )

        return output.frames[0]