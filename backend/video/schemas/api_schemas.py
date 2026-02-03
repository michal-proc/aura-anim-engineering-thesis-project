from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

from backend.video.constants import (
    AspectRatio,
    ResolutionClass,
    VideoFPS,
    VideoFormat,
    BaseGenerationModel,
    MotionAdapter,
    JobStatus
)


class VideoGenerationRequest(BaseModel):
    """Request model for video generation"""

    # Text parameters
    prompt: str = Field(..., description="Text prompt")
    negative_prompt: str | None = Field(..., description="Negative prompt")

    # Video specifications
    aspect_ratio: AspectRatio = Field(..., description="Aspect ratio")
    resolution: ResolutionClass = Field(..., description="Resolution")
    video_length: int = Field(..., description="Video length in seconds")
    fps: VideoFPS = Field(..., description="Frames per second")
    output_format: VideoFormat = Field(..., description="Output format")

    # Generation parameters
    base_model: BaseGenerationModel = Field(..., description="Base model name")
    motion_adapter: MotionAdapter = Field(..., description="Motion adapter name")
    inference_steps: int = Field(default=25, description="Number of inference steps", ge=1, le=100)

    @field_validator("aspect_ratio", mode="before")
    @classmethod
    def convert_aspect_ratio(cls, v):
        """Convert list to tuple for AspectRatio enum matching"""
        if isinstance(v, list):
            return tuple(v)
        return v


class VideoGenerationResponse(BaseModel):
    """Response model for video generation"""
    job_id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job processing status")


class VideoUpdateRequest(BaseModel):
    """Request model for updating video metadata"""
    name: Optional[str] = Field(default=None, description="New video name (optional)")
    shared: Optional[bool] = Field(default=None, description="Whether the video is shared publicly (optional)")


class JobStatusResponse(BaseModel):
    """Response model for job processing status"""
    job_id: str = Field(..., description="Job ID")
    status: JobStatus = Field(..., description="Job processing status")
    progress_percentage: int = Field(..., description="Job processing progress")


class JobCancellationResponse(BaseModel):
    """Response model for job cancellation"""
    job_id: str = Field(..., description="Job ID")
    is_successful: bool = Field(..., description="Whether cancellation succeeded")


class VideoMetadata(BaseModel):
    """Video file metadata"""
    duration_seconds: int = Field(..., description="Video duration in seconds")
    width: int = Field(..., description="Video width in pixels")
    height: int = Field(..., description="Video height in pixels")
    fps: VideoFPS = Field(..., description="Frames per second")
    format: VideoFormat = Field(..., description="Video file format")
    file_size_bytes: int = Field(..., description="File size in bytes")


class VideoDownloadResponse(BaseModel):
    """Response model for downloading the generated video"""
    job_id: str = Field(..., description="Job ID")
    download_url: str = Field(..., description="Presigned download URL for the video")
    expires_at: datetime = Field(..., description="When the download URL expires")
    video_metadata: VideoMetadata = Field(..., description="Video file metadata")


class WebSocketJobUpdate(BaseModel):
    """WebSocket message for job status updates"""
    job_id: str = Field(..., description="Job identifier")
    name: str = Field(..., description="Job shorter prompt or name")
    status: JobStatus = Field(..., description="Current job status")
    progress_percentage: int = Field(..., description="Progress percentage")
    final: bool = Field(..., description="Whether this is the final message")
    timestamp: datetime = Field(..., description="Message timestamp")


class WebSocketErrorMessage(BaseModel):
    """WebSocket error message"""
    job_id: str = Field(..., description="Job identifier")
    error: str = Field(..., description="Error description")


class VideoJobParameters(BaseModel):
    """Job parameters for video list response"""
    prompt: str = Field(..., description="Text prompt")
    width: int = Field(..., description="Video width in pixels")
    height: int = Field(..., description="Video height in pixels")
    video_length: int = Field(..., description="Video length in seconds")
    fps: int = Field(..., description="Frames per second")


class VideoJobInfo(BaseModel):
    """Job information for video list response"""
    job_id: str = Field(..., description="Job ID")
    status: JobStatus = Field(..., description="Job status")
    progress_percentage: int = Field(..., description="Progress percentage")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: datetime | None = Field(None, description="Job completion timestamp")
    parameters: VideoJobParameters = Field(..., description="Job parameters")


class VideoListItem(BaseModel):
    """Single video item in the list"""
    id: str = Field(..., description="Video ID (job ID)")
    user_id: int | None = Field(None, description="User ID")
    name: str = Field(..., description="Video name (based on prompt)")
    shared: bool = Field(False, description="Whether the video is publicly shared")
    created_at: datetime = Field(..., description="Video creation timestamp")
    job: VideoJobInfo = Field(..., description="Job information")


class VideoListResponse(BaseModel):
    """Response model for GET /videos"""
    success: bool = Field(True, description="Whether the request was successful")
    data: list[VideoListItem] = Field(..., description="List of videos")


class JobParameters(BaseModel):
    """Job parameters for job list response"""
    prompt: str = Field(..., description="Text prompt")
    width: int = Field(..., description="Video width in pixels")
    height: int = Field(..., description="Video height in pixels")
    video_length: int = Field(..., description="Video length in seconds")
    fps: int = Field(..., description="Frames per second")
    output_format: str = Field(..., description="Output format")


class JobDetail(BaseModel):
    """Detailed job information"""
    job_id: str = Field(..., description="Job ID")
    status: JobStatus = Field(..., description="Job status")
    progress_percentage: int = Field(..., description="Progress percentage")
    current_step: str | None = Field(None, description="Current processing step")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: datetime | None = Field(None, description="Job completion timestamp")
    error_message: str | None = Field(None, description="Error message if failed")
    marked_as_read: bool = Field(..., description="Whether job has been marked as read")
    parameters: JobParameters = Field(..., description="Job parameters")


class JobListMeta(BaseModel):
    """Metadata for job list response"""
    total_count: int = Field(..., description="Total number of jobs")
    active_count: int = Field(..., description="Number of active jobs (pending/processing)")
    failed_count: int = Field(..., description="Number of failed jobs")
    completed_count: int = Field(..., description="Number of completed jobs")
    unread_count: int = Field(..., description="Number of unread jobs")


class JobListResponse(BaseModel):
    """Response model for GET /jobs"""
    success: bool = Field(True, description="Whether the request was successful")
    data: list[JobDetail] = Field(..., description="List of unread jobs")
    meta: JobListMeta = Field(..., description="Job statistics")


class VideoDetailResponse(BaseModel):
    """Response model for GET /videos/{video_id}"""
    success: bool = Field(True, description="Whether the request was successful")
    data: VideoListItem = Field(..., description="Video details")


class VideoDeletionResponse(BaseModel):
    """Response model for DELETE /videos/{video_id}"""
    success: bool = Field(..., description="Whether deletion was successful")
    video_id: str = Field(..., description="Deleted video ID")

class VideoExplore(BaseModel):
    """Single explore video entry. Represents a curated static video used for the Explore section."""
    name: str = Field(..., description="Video display name")
    prompt: str = Field(..., description="Prompt or descriptive text for the video")
    url: str = Field(..., description="Public URL to the video file")

class GetVideoExploreResponse(BaseModel):
    """Response model for GET /videos/explore. Returns a list of curated explore videos available for preview."""
    success: bool = Field(..., description="Whether the request was successful")
    data: list[VideoExplore] = Field(..., description="Explore video list")