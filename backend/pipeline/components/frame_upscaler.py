import torch
import logging
import traceback
import gc
from PIL import Image
from typing import List, Optional, Callable
import os
import requests
from tqdm import tqdm
import subprocess
import sys
import importlib.util

from backend.config.management import ConfigManager
from backend.config.management.config_type import ConfigType
from backend.pipeline.schemas.component_parameters import FrameUpscalerInput
from backend.pipeline.deployments.exceptions import CancellationException


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class FrameUpscaler:
    """
    Upscales frames using RealESRGAN.
    
    Public Methods:
        - upscale(input_params: FrameUpscalerInput) -> List[Image.Image]
    """
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging

        config_manager = ConfigManager(enable_logging=enable_logging)
        config = config_manager.get_config(ConfigType.FRAME_UPSCALER)

        self.device = config.get("device") or ("cuda" if torch.cuda.is_available() else "cpu")
        self.supported_scales = config.get("supported_scales", [2, 4, 8])
        self.model_path = config.get("model_path", "weights/RealESRGAN")
        self.weights_paths = config.get("weights_paths", {})
        self.weights_download_urls = config.get("weights_download_urls", {})
        self.model_download_url = config.get("model_download_url")

        self.models = {}
        self._setup_realesrgan()

        self.cancellation_check_callback: Optional[Callable[[], bool]] = None
        self.progress_callback: Optional[Callable[[int, int], None]] = None

        self._log("FrameUpscaler initialized")

    def _log(self, message: str, level: int = logging.INFO) -> None:
        if self.enable_logging:
            logging.log(level, f"[FrameUpscaler] {message}")

    def set_cancellation_callback(self, callback: Callable[[], bool]) -> None:
        self.cancellation_check_callback = callback

    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        self.progress_callback = callback
    
    def _setup_realesrgan(self):
        """Setup RealESRGAN repository."""
        if not os.path.exists(self.model_path):
            try:
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                subprocess.run(
                    ["git", "clone", self.model_download_url, self.model_path], 
                    check=True
                )
                self._log(f"Cloned RealESRGAN to {self.model_path}")
            except Exception as e:
                self._log(f"Error cloning RealESRGAN: {e}", level=logging.ERROR)
                raise
        
        if self.model_path not in sys.path:
            sys.path.append(os.path.abspath(self.model_path))
        
        init_file = os.path.join(self.model_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Auto-created by FrameUpscaler")
        
        self._patch_huggingface_hub()
    
    def _patch_huggingface_hub(self):
        """Patch model.py for newer huggingface_hub versions."""
        model_file = os.path.join(self.model_path, "RealESRGAN", "model.py")
        if os.path.exists(model_file):
            with open(model_file, "r") as f:
                model_code = f.read()
            
            if "from huggingface_hub import hf_hub_url, cached_download" in model_code:
                patched_code = model_code.replace(
                    "from huggingface_hub import hf_hub_url, cached_download",
                    "from huggingface_hub import hf_hub_download",
                )
                patched_code = patched_code.replace(
                    "cached_download(hf_hub_url(repo_id, filename))",
                    "hf_hub_download(repo_id=repo_id, filename=filename)",
                )
                
                with open(model_file, "w") as f:
                    f.write(patched_code)
                
                self._log("Patched huggingface_hub imports")
    
    def _download_file(self, url: str, save_path: str):
        """Download a file from URL."""
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024
            
            with open(save_path, "wb") as f:
                for data in tqdm(
                    response.iter_content(block_size),
                    total=total_size // block_size,
                    unit="KB",
                    unit_scale=True,
                    desc=f"Downloading RealESRGAN weights"
                ):
                    f.write(data)
            
            self._log(f"Downloaded weights to {save_path}")
        except Exception as e:
            self._log(f"Error downloading file: {e}", level=logging.ERROR)
            if os.path.exists(save_path):
                os.remove(save_path)
            raise
    
    def _get_model(self, scale_factor: int):
        """Get or load RealESRGAN model for scale factor."""
        if scale_factor not in self.supported_scales:
            closest_scale = min(
                self.supported_scales, key=lambda x: abs(x - scale_factor)
            )
            self._log(
                f"Scale {scale_factor} not supported, using {closest_scale}",
                level=logging.WARNING
            )
            scale_factor = closest_scale
        
        if scale_factor in self.models:
            return self.models[scale_factor]
        
        try:
            if importlib.util.find_spec("RealESRGAN") is None:
                realesrgan_py_path = os.path.join(self.model_path, "RealESRGAN.py")
                if not os.path.exists(realesrgan_py_path):
                    raise ImportError(f"Could not find RealESRGAN.py in {self.model_path}")
                
                spec = importlib.util.spec_from_file_location(
                    "RealESRGAN", realesrgan_py_path
                )
                realesrgan_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(realesrgan_module)
                RealESRGAN = realesrgan_module.RealESRGAN
            else:
                from RealESRGAN import RealESRGAN
        
        except Exception as e:
            self._log(f"Error importing RealESRGAN: {e}", level=logging.ERROR)
            raise
        
        try:
            weights_path = self.weights_paths.get(scale_factor)
            model = RealESRGAN(self.device, scale=scale_factor)
            
            if not os.path.exists(weights_path):
                download_url = self.weights_download_urls.get(scale_factor)
                if download_url:
                    self._download_file(download_url, weights_path)
                else:
                    raise ValueError(f"No download URL for scale factor {scale_factor}")
            
            model.load_weights(weights_path, download=False)
            self.models[scale_factor] = model
            self._log(f"Loaded RealESRGAN model for scale {scale_factor}x")
            
            return model
        
        except Exception as e:
            self._log(f"Error loading model: {e}", level=logging.ERROR)
            raise
    
    def upscale(self, input_params: FrameUpscalerInput) -> List[Image.Image]:
        """
        Upscale frames to increase resolution.
        
        Args:
            input_params: Input parameters with frames and scale_factor
            
        Returns:
            Upscaled frames
        """
        frames = input_params.frames
        scale_factor = input_params.scale_factor
        
        if not frames or scale_factor == 1:
            self._log("Skipping upscaling")
            return frames
        
        self._log(f"Upscaling {len(frames)} frames with factor {scale_factor}x")
        
        try:
            model = self._get_model(scale_factor)
            upscaled_frames = []

            total_frames = len(frames)
            midpoint = total_frames // 2
            progress_reported = False

            for i, frame in enumerate(frames):
                if self.cancellation_check_callback and self.cancellation_check_callback():
                    self._log(f"Cancellation detected at frame {i}/{len(frames)}", level=logging.WARNING)
                    raise CancellationException(f"Upscaling cancelled at frame {i}")

                if self.progress_callback and i == midpoint and not progress_reported:
                    self.progress_callback(i, total_frames)
                    progress_reported = True

                if frame.mode != "RGB":
                    frame = frame.convert("RGB")

                upscaled_frame = model.predict(frame)
                upscaled_frames.append(upscaled_frame)

                if (i + 1) % 10 == 0:
                    self._log(f"Upscaled {i + 1}/{len(frames)} frames")
            
            self._log(f"Upscaling complete: {len(upscaled_frames)} frames")
            return upscaled_frames

        except CancellationException:
            self._log("Upscaling cancelled", level=logging.INFO)
            raise
        except Exception as e:
            self._log(f"Error during upscaling: {e}", level=logging.ERROR)
            self._log(traceback.format_exc(), level=logging.ERROR)
            return frames

        finally:
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()