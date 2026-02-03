import logging
import os
import imageio
import numpy as np
from typing import List
from PIL import Image
from datetime import datetime

from backend.config.management import ConfigManager
from backend.config.management.config_type import ConfigType
from backend.pipeline.schemas.component_parameters import VideoPostprocessorParams


class VideoPostprocessor:
    """
    Post-processes and saves video frames.
    
    Public Methods:
        - postprocess(params: VideoPostprocessorParams) -> str
    """
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging

        config_manager = ConfigManager(enable_logging=enable_logging)
        config = config_manager.get_config(ConfigType.VIDEO_POSTPROCESSOR)
        
        self.supported_formats = config.get("supported_formats", ['mp4', 'gif', 'avi', 'mov', 'webm'])
        self.default_format = config.get("default_format", "mp4")
        self.format_settings = config.get("format_settings", {})
        
        self._log("VideoPostprocessor initialized")
    
    def _log(self, message: str, level: int = logging.INFO) -> None:
        if self.enable_logging:
            logging.log(level, f"[VideoPostprocessor] {message}")
    
    def postprocess(self, params: VideoPostprocessorParams) -> str:
        """
        Post-process frames and save video.
        
        This method orchestrates all post-processing steps:
        1. Trim frames to target duration
        2. Crop frames to target dimensions
        3. Generate output path
        4. Save video to file
        
        Args:
            params: VideoPostprocessorParams containing all necessary parameters
            
        Returns:
            Path to saved video file
        """
        frames = params.frames
        
        if not frames:
            raise ValueError("Cannot postprocess: no frames provided")
        
        self._log(f"Starting postprocessing of {len(frames)} frames")
        
        frames = self._trim_frames(
            frames=frames,
            target_duration=params.target_duration,
            fps=params.fps
        )
  
        frames = self._crop_frames(
            frames=frames,
            target_width=params.target_width,
            target_height=params.target_height
        )
        
        output_path = self._generate_output_path(
            prompt=params.prompt,
            seed=params.seed,
            video_length=params.video_length,
            fps=params.fps,
            output_format=params.output_format,
            output_dir=params.output_dir
        )
        
        saved_path = self._save_video(
            frames=frames,
            fps=params.fps,
            output_path=output_path
        )
        
        self._log(f"Postprocessing complete: {saved_path}")
        
        return saved_path
    
    def _trim_frames(
        self, 
        frames: List[Image.Image], 
        target_duration: int, 
        fps: int
    ) -> List[Image.Image]:
        if not frames:
            return frames
        
        target_frame_count = int(target_duration * fps)
        
        if len(frames) <= target_frame_count:
            return frames
        
        trimmed = frames[:target_frame_count]
        self._log(f"Trimmed frames from {len(frames)} to {len(trimmed)}")
        
        return trimmed
    
    def _crop_frames(
        self, 
        frames: List[Image.Image], 
        target_width: int, 
        target_height: int
    ) -> List[Image.Image]:
        if not frames:
            return frames
        
        self._log(f"Cropping {len(frames)} frames to {target_width}x{target_height}")
        
        cropped_frames = []
        for frame in frames:
            current_width, current_height = frame.size
            
            if current_width == target_width and current_height == target_height:
                cropped_frames.append(frame)
                continue
            
            left = (current_width - target_width) // 2
            top = (current_height - target_height) // 2
            right = left + target_width
            bottom = top + target_height
            
            if current_width < target_width or current_height < target_height:
                new_frame = Image.new(frame.mode, (target_width, target_height), (0, 0, 0))
                paste_left = max(0, (target_width - current_width) // 2)
                paste_top = max(0, (target_height - current_height) // 2)
                new_frame.paste(frame, (paste_left, paste_top))
                cropped_frames.append(new_frame)
            else:
                cropped_frame = frame.crop((left, top, right, bottom))
                cropped_frames.append(cropped_frame)
        
        return cropped_frames
    
    def _generate_output_path(
        self,
        prompt: str,
        seed: int,
        video_length: int,
        fps: int,
        output_format: str,
        output_dir: str
    ) -> str:
        os.makedirs(output_dir, exist_ok=True)
        
        validated_format = self._validate_format(output_format)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        safe_prompt = "".join(
            c if c.isalnum() or c in (" ", "_") else "" 
            for c in prompt[:30]
        ).rstrip().replace(" ", "_") or "video"
        
        filename = (
            f"{timestamp}_{safe_prompt}_seed{seed}_"
            f"len{video_length}s_fps{fps}.{validated_format}"
        )
        
        output_path = os.path.join(output_dir, filename)
        self._log(f"Generated output path: {output_path}")
        
        return output_path
    
    def _save_video(
        self,
        frames: List[Image.Image],
        fps: int,
        output_path: str
    ) -> str:
        if not frames:
            raise ValueError("Cannot save video: no frames provided")
        
        output_format = output_path.split('.')[-1].lower()
        validated_format = self._validate_format(output_format)
        
        if validated_format != output_format:
            output_path = output_path.rsplit('.', 1)[0] + f'.{validated_format}'
            self._log(f"Changed format to {validated_format}")
        
        self._log(f"Saving {len(frames)} frames at {fps} FPS to {output_path}")
        
        format_config = self.format_settings.get(validated_format, {})
        
        try:
            if validated_format == 'gif':
                self._save_as_gif(frames, fps, output_path, format_config)
            else:
                self._save_as_video_file(frames, fps, output_path, validated_format, format_config)
            
            self._log(f"Video saved successfully")
            return output_path
        
        except Exception as e:
            self._log(f"Failed to save video: {e}", level=logging.ERROR)
            raise RuntimeError(f"Video saving failed: {e}")
    
    def _validate_format(self, output_format: str) -> str:
        """Validate and normalize output format."""
        normalized = output_format.lower().strip()
        
        if normalized not in self.supported_formats:
            self._log(
                f"Unsupported format '{normalized}', using '{self.default_format}'",
                level=logging.WARNING
            )
            return self.default_format
        
        return normalized
    
    def _save_as_gif(
        self,
        frames: List[Image.Image],
        fps: int,
        output_path: str,
        config: dict
    ) -> None:
        gif_frames = [frame.convert('RGB') for frame in frames]
        duration = int(1000 / fps)
        
        gif_frames[0].save(
            output_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=duration,
            loop=config.get('loop', 0),
            optimize=config.get('optimize', True)
        )
    
    def _save_as_video_file(
        self,
        frames: List[Image.Image],
        fps: int,
        output_path: str,
        format_name: str,
        config: dict
    ) -> None:
        frames_np = [np.array(frame.convert("RGB")) for frame in frames]

        codec = config.get('codec', 'libx264')
        quality = config.get('quality', 8)
        extra_params = config.get('extra_params', [])

        with imageio.get_writer(
            output_path,
            fps=fps,
            codec=codec,
            quality=quality,
            macro_block_size=1,
            ffmpeg_params=extra_params,
        ) as writer:
            for frame_np in frames_np:
                writer.append_data(frame_np)