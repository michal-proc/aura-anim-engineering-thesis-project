from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from PIL import Image

class VideoParameters(BaseModel):
    """
    Complete parameters for video generation pipeline.
    This is the main input model used by the pipeline orchestrator.
    """
    prompt: str
    negative_prompt: str | None = Field(default=None, description="Negative prompt to avoid certain features")
    video_width: int = Field(default=512)
    video_height: int = Field(default=512)
    video_length: int = Field(default=4)
    fps: int = Field(default=8)
    inference_steps: int = Field(default=25)
    guidance_scale: float = Field(default=7.5)
    seed: int = Field(default=0)
    base_model: str = Field(
        default="sd15",
        description="Base model identifier - must match a key in config/components/video_generator.yaml base_models"
    )
    motion_adapter: str = Field(
        default="default",
        description="Motion adapter identifier"
    )
    loras: Optional[Dict[str, float]] = Field(default_factory=dict)
    output_format: str = Field(default="gif")

    class Config:
        populate_by_name = True


class VideoPreprocessorInput(BaseModel):
    video_width: int = Field(..., ge=8, description="Desired video width")
    video_height: int = Field(..., ge=8, description="Desired video height")
    video_length: int = Field(..., ge=1, description="Desired video length in seconds")
    target_fps: int = Field(..., ge=1, description="Target frames per second")

    class Config:
        populate_by_name = True


class VideoPreprocessorOutput(BaseModel):
    fps_factor: int = Field(..., ge=1, description="FPS interpolation factor")
    frame_scale_factor: int = Field(..., ge=1, description="Frame upscaling factor")
    adjusted_width: int = Field(..., ge=8, description="Adjusted width for generation")
    adjusted_height: int = Field(..., ge=8, description="Adjusted height for generation")
    adjusted_length: int = Field(..., ge=1, description="Adjusted length for generation")

    class Config:
        populate_by_name = True

class VideoGeneratorParams(BaseModel):
    prompt: str = Field(..., description="Text prompt for video generation")
    negative_prompt: str = Field(
        default="blurry, poor quality, bad quality, worse quality, low resolution",
        description="Negative prompt to avoid certain features"
    )
    video_width: int = Field(
        default=512, 
        ge=8,
        description="Width of generated video (will be aligned to multiple of 8)"
    )
    video_height: int = Field(
        default=512,
        ge=8, 
        description="Height of generated video (will be aligned to multiple of 8)"
    )
    video_length: int = Field(
        default=4,
        ge=1,
        description="Video length in seconds"
    )
    fps: int = Field(
        default=8,
        ge=1,
        description="Frames per second for generation"
    )
    inference_steps: int = Field(
        default=25,
        ge=1,
        le=150,
        description="Number of denoising steps"
    )
    guidance_scale: float = Field(
        default=7.5,
        ge=1.0,
        le=20.0,
        description="Classifier-free guidance scale"
    )
    seed: int = Field(
        default=0,
        ge=0,
        description="Random seed for reproducibility"
    )
    base_model: str = Field(
        default="sd15",
        description="Base model identifier - must match a key in config/components/video_generator.yaml base_models"
    )
    motion_adapter: str = Field(
        default="default",
        description="Motion adapter identifier"
    )
    loras: Dict[str, float] = Field(
        default_factory=dict,
        description="LoRA presets and their weights"
    )

    class Config:
        populate_by_name = True


class FrameInterpolatorInput(BaseModel):
    frames: List[Image.Image] = Field(..., description="Frames to interpolate between")
    fps_factor: int = Field(..., ge=1, description="FPS multiplication factor")

    class Config:
        arbitrary_types_allowed = True

class FrameUpscalerInput(BaseModel):
    frames: List[Image.Image] = Field(..., description="Frames to upscale")
    scale_factor: int = Field(..., ge=1, le=8, description="Upscaling factor (1, 2, 4, or 8)")

    class Config:
        arbitrary_types_allowed = True


class VideoPostprocessorParams(BaseModel):
    frames: List[Image.Image] = Field(
        ..., 
        description="Frames to post-process"
    )
    
    target_duration: int = Field(
        ..., 
        ge=1, 
        description="Target video duration in seconds"
    )
    fps: int = Field(
        ..., 
        ge=1, 
        description="Frames per second"
    )
    
    target_width: int = Field(
        ..., 
        ge=8, 
        description="Target video width in pixels"
    )
    target_height: int = Field(
        ..., 
        ge=8, 
        description="Target video height in pixels"
    )
    
    prompt: str = Field(
        ..., 
        description="Video prompt (used in filename)"
    )
    seed: int = Field(
        ..., 
        ge=0, 
        description="Random seed (used in filename)"
    )
    video_length: int = Field(
        ..., 
        ge=1, 
        description="Video length in seconds (used in filename)"
    )
    output_format: str = Field(
        default="mp4", 
        description="Output format (mp4, gif, avi, mov, webm)"
    )
    output_dir: str = Field(
        default="outputs", 
        description="Output directory path"
    )
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
