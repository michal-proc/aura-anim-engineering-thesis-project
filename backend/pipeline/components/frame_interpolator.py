import torch
import logging
import traceback
import gc
import numpy as np
from PIL import Image
from typing import List, Optional, Callable
import os
import requests
from tqdm import tqdm

from backend.config.management import ConfigManager
from backend.config.management.config_type import ConfigType
from backend.pipeline.schemas.component_parameters import FrameInterpolatorInput
from backend.pipeline.deployments.exceptions import CancellationException


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class FrameInterpolator:
    """
    Interpolates frames to increase FPS using FILM model.
    
    Public Methods:
        - interpolate(input_params: FrameInterpolatorInput) -> List[Image.Image]
    """
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging

        config_manager = ConfigManager(enable_logging=enable_logging)
        config = config_manager.get_config(ConfigType.FRAME_INTERPOLATOR)

        self.model_path = config.get("model_path", "weights/film_net_fp16.pt")
        self.model_download_url = config.get("model_download_url")
        self.default_fps_factor = config.get("default_fps_factor", 2)
        self.device = config.get("device") or ("cuda" if torch.cuda.is_available() else "cpu")

        self.model = None
        self._load_model()

        self.cancellation_check_callback: Optional[Callable[[], bool]] = None
        self.progress_callback: Optional[Callable[[int, int], None]] = None

        self._log("FrameInterpolator initialized")

    def _log(self, message: str, level: int = logging.INFO) -> None:
        if self.enable_logging:
            logging.log(level, f"[FrameInterpolator] {message}")

    def set_cancellation_callback(self, callback: Callable[[], bool]) -> None:
        self.cancellation_check_callback = callback

    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        self.progress_callback = callback
    
    def _load_model(self):
        """Load the FILM interpolation model."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        if not os.path.exists(self.model_path):
            if self.model_download_url:
                self._download_file(self.model_download_url, self.model_path)
            else:
                raise FileNotFoundError(
                    f"Model not found at {self.model_path} and no download URL configured"
                )
        
        try:
            self.model = torch.jit.load(self.model_path, map_location="cpu")
            self.model.eval().to(device=self.device, dtype=torch.float16)
            self._log(f"Model loaded on {self.device}")
        except Exception as e:
            self._log(f"Error loading model: {e}", level=logging.ERROR)
            raise
    
    def _download_file(self, url: str, save_path: str):
        """Download a file from URL."""
        try:
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
                    desc="Downloading FILM model"
                ):
                    f.write(data)
            
            self._log(f"Downloaded model to {save_path}")
        except Exception as e:
            self._log(f"Error downloading file: {e}", level=logging.ERROR)
            if os.path.exists(save_path):
                os.remove(save_path)
            raise
    
    def interpolate(self, input_params: FrameInterpolatorInput) -> List[Image.Image]:
        """
        Interpolate frames to increase FPS.
        
        Args:
            input_params: Input parameters with frames and fps_factor
            
        Returns:
            Interpolated frames
        """
        frames = input_params.frames
        fps_factor = input_params.fps_factor
        
        if not frames or fps_factor < 2 or len(frames) < 2:
            self._log("Skipping interpolation")
            return frames
        
        self._log(f"Interpolating {len(frames)} frames with factor {fps_factor}")
        
        try:
            interpolated_frames = []
            interpolated_frames.append(frames[0])

            total_frame_pairs = len(frames) - 1
            midpoint = total_frame_pairs // 2
            progress_reported = False

            with torch.no_grad():
                for i in range(len(frames) - 1):
                    if self.cancellation_check_callback and self.cancellation_check_callback():
                        self._log(f"Cancellation detected at frame {i}/{len(frames)-1}", level=logging.WARNING)
                        raise CancellationException(f"Interpolation cancelled at frame pair {i}")

                    if self.progress_callback and i == midpoint and not progress_reported:
                        self.progress_callback(i, total_frame_pairs)
                        progress_reported = True

                    frame1, frame2 = frames[i], frames[i + 1]

                    frame1_tensor, frame2_tensor = self._preprocess_frames(frame1, frame2)

                    for j in range(1, fps_factor):
                        time_step = j / fps_factor
                        dt = torch.full(
                            (1, 1), time_step, device=self.device, dtype=torch.float16
                        )

                        intermediate_tensor = self.model(frame1_tensor, frame2_tensor, dt)
                        intermediate_frame = self._postprocess_frame(intermediate_tensor)
                        interpolated_frames.append(intermediate_frame)

                    if i < len(frames) - 2:
                        interpolated_frames.append(frame2)
            
            interpolated_frames.append(frames[-1])

            self._log(f"Interpolation complete: {len(interpolated_frames)} frames")
            return interpolated_frames

        except CancellationException:
            self._log("Interpolation cancelled", level=logging.INFO)
            raise
        except Exception as e:
            self._log(f"Error during interpolation: {e}", level=logging.ERROR)
            self._log(traceback.format_exc(), level=logging.ERROR)
            return frames

        finally:
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    def _preprocess_frames(
        self, img1: Image.Image, img2: Image.Image
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Preprocess frames for model input."""
        if img1.size != img2.size:
            img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
        
        if img1.mode != "RGB":
            img1 = img1.convert("RGB")
        if img2.mode != "RGB":
            img2 = img2.convert("RGB")
        
        img1_np = np.array(img1).astype(np.float32) / 255.0
        img2_np = np.array(img2).astype(np.float32) / 255.0
        
        img1_tensor = torch.from_numpy(img1_np).permute(2, 0, 1).unsqueeze(0)
        img2_tensor = torch.from_numpy(img2_np).permute(2, 0, 1).unsqueeze(0)
        
        img1_tensor = img1_tensor.to(device=self.device, dtype=torch.float16)
        img2_tensor = img2_tensor.to(device=self.device, dtype=torch.float16)
        
        return img1_tensor, img2_tensor
    
    def _postprocess_frame(self, tensor: torch.Tensor) -> Image.Image:
        """Convert model output to PIL Image."""
        with torch.no_grad():
            frame = tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
        
        frame = np.clip(frame * 255.0, 0, 255).astype(np.uint8)
        return Image.fromarray(frame)