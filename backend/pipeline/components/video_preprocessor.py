import logging
import numpy as np

from backend.config.management import ConfigManager
from backend.config.management.config_type import ConfigType
from backend.pipeline.schemas.component_parameters import (
    VideoPreprocessorInput,
    VideoPreprocessorOutput
)


class VideoPreprocessor:
    """
    Preprocesses video parameters before generation.
    Calculates scaling factors and adjusted dimensions.
    
    Public Methods:
        - process(input_params: VideoPreprocessorInput) -> VideoPreprocessorOutput
    """
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging

        config_manager = ConfigManager(enable_logging=enable_logging)
        config = config_manager.get_config(ConfigType.VIDEO_PREPROCESSOR)

        self.base_generation_fps = config.get("default_fps", 8)
        self.dimension_alignment = config.get("dimension_alignment", 8)
        self.max_generation_dimension = config.get("max_generation_dimension", 1024)
        self.min_dimension = config.get("min_dimension", 8)
        self.extra_generation_seconds = config.get("extra_generation_seconds", 1)
        
        self._log("VideoPreprocessor initialized")
    
    def _log(self, message: str, level: int = logging.INFO) -> None:
        if self.enable_logging:
            logging.log(level, f"[VideoPreprocessor] {message}")
    
    def process(self, input_params: VideoPreprocessorInput) -> VideoPreprocessorOutput:
        """
        Process video parameters and calculate adjustments.
        
        Args:
            input_params: Input parameters with dimensions and FPS
            
        Returns:
            VideoPreprocessorOutput with calculated factors and adjusted dimensions
        """
        self._log(
            f"Processing: {input_params.video_width}x{input_params.video_height}, "
            f"{input_params.video_length}s @ {input_params.target_fps}fps"
        )
        
        fps_factor = self._calculate_fps_factor(input_params.target_fps)
        frame_scale_factor = self._calculate_frame_scale_factor(
            input_params.video_width, 
            input_params.video_height
        )
        
        adjusted_width, adjusted_height = self._adjust_dimensions_for_generation(
            input_params.video_width, 
            input_params.video_height, 
            frame_scale_factor
        )
        
        adjusted_length = self._add_extra_generation_time(
            input_params.video_length, 
            fps_factor
        )
        
        self._log(
            f"Calculated - FPS: {fps_factor}x, Scale: {frame_scale_factor}x, "
            f"Dims: {adjusted_width}x{adjusted_height}, Length: {adjusted_length}s"
        )
        
        return VideoPreprocessorOutput(
            fps_factor=fps_factor,
            frame_scale_factor=frame_scale_factor,
            adjusted_width=adjusted_width,
            adjusted_height=adjusted_height,
            adjusted_length=adjusted_length
        )
    
    def _calculate_fps_factor(self, target_fps: int) -> int:
        if target_fps <= self.base_generation_fps:
            return 1
        
        fps_factor = target_fps // self.base_generation_fps
        return max(1, fps_factor)
    
    def _calculate_frame_scale_factor(self, width: int, height: int) -> int:
        max_dim = max(width, height)
        
        if max_dim <= self.max_generation_dimension:
            return 1
        
        scale = max_dim / self.max_generation_dimension
        factor = self._round_to_power_of_2(int(np.ceil(scale)))
        
        return factor
    
    def _round_to_power_of_2(self, n: int) -> int:
        if n <= 0:
            return 1
        
        power = 1
        while power * 2 < n and power * 2 > 0:
            power *= 2
        
        if abs(n - power) < abs(n - (power * 2)) or power * 2 <= 0:
            return power
        else:
            return power * 2
    
    def _adjust_dimensions_for_generation(
        self, 
        width: int, 
        height: int, 
        scale_factor: int
    ) -> tuple[int, int]:
        scaled_width = width // scale_factor
        scaled_height = height // scale_factor
        
        adjusted_width = (scaled_width // self.dimension_alignment) * self.dimension_alignment
        adjusted_height = (scaled_height // self.dimension_alignment) * self.dimension_alignment
        
        adjusted_width = max(self.min_dimension, adjusted_width)
        adjusted_height = max(self.min_dimension, adjusted_height)
        
        self._log(
            f"Dimension adjustment: {width}x{height} -> {scaled_width}x{scaled_height} "
            f"-> {adjusted_width}x{adjusted_height} (scale factor: {scale_factor})"
        )
        
        return adjusted_width, adjusted_height
    
    def _add_extra_generation_time(self, video_length: int, fps_factor: int) -> int:
        """Add extra seconds for generation to ensure interpolator has enough frames."""
        if fps_factor > 1:
            extended_length = video_length + self.extra_generation_seconds
            
            self._log(
                f"Extended generation length: {video_length}s + {self.extra_generation_seconds}s "
                f"= {extended_length}s (for interpolation)"
            )
            
            return extended_length
        
        return video_length