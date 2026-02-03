from pydantic import BaseModel, Field
from datetime import datetime

from backend.video.constants import (
    VideoFPS, VideoFormat,
    BaseGenerationModel, MotionAdapter,
)


class VideoFile(BaseModel):
    """Domain model for a generated video file"""
    job_id: str = Field(..., description="Job identifier")
    object_key: str = Field(..., description="S3 storage object key for the video file")
    duration_seconds: int = Field(..., description="Video duration in seconds")
    width: int = Field(..., description="Video width in pixels")
    height: int = Field(..., description="Video height in pixels")
    fps: VideoFPS = Field(..., description="Frames per second")
    format: VideoFormat = Field(..., description="Video file format")
    file_size_bytes: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="When the video file was created")


class VideoDownloadInfo(BaseModel):
    """Domain model for video download information"""
    job_id: str = Field(..., description="Job identifier")
    download_url: str = Field(..., description="Presigned download URL")
    expires_at: datetime = Field(..., description="When the download URL expires")
    video_file: VideoFile = Field(..., description="Video file details")


class VideoGenerationSpec(BaseModel):
    """Domain model specifying video generation parameters. It completely
    describes parameters of a video generation process from the domain layer perspective."""
    # Text parameters
    prompt: str = Field(..., description="Text prompt")
    negative_prompt: str | None = Field(None, description="Negative prompt")
    
    # Resolved video dimensions
    width: int = Field(..., description="Video width in pixels")
    height: int = Field(..., description="Video height in pixels")
    video_length: int = Field(..., description="Video duration in seconds")
    fps: VideoFPS = Field(..., description="Frames per second")
    output_format: VideoFormat = Field(..., description="Output video format")
    
    # Generation parameters
    base_model: BaseGenerationModel = Field(..., description="Base model identifier")
    motion_adapter: MotionAdapter = Field(..., description="Motion adapter identifier")
    inference_steps: int = Field(..., description="Number of inference steps")
    guidance_scale: float = Field(..., description="Guidance scale")
    seed: int = Field(..., description="Random seed")
    
    # Advanced parameters
    loras: dict | None = Field(None, description="LoRA configurations")
    additional_params: dict | None = Field(None, description="Additional generation parameters")
