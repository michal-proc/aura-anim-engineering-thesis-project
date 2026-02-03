"""Database models for video generation"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Float, JSON, Boolean, func, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.video.constants import JobStatus

if TYPE_CHECKING:
    from backend.accounts.models import User


class VideoGenerationJob(Base):
    """Core video generation job information"""
    
    __tablename__ = "video_generation_jobs"
    
    # Primary identification
    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Job metadata
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default=None,
        comment="Custom video name set by user"
    )
    shared: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this video is shared publicly"
    )

    # Processing status
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.PENDING,
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Progress (real-time updates tracking)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Notification tracking
    marked_as_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Relationships
    parameters: Mapped[Optional["VideoGenerationJobParameters"]] = relationship(
        "VideoGenerationJobParameters",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )
    result: Mapped[Optional["VideoGenerationJobResult"]] = relationship(
        "VideoGenerationJobResult",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<VideoGenerationJob("
            f"job_id='{self.job_id}', "
            f"status={self.status.value}, "
            f"user_id={self.user_id}, "
            f"progress={self.progress_percentage}%, "
            f"created_at={self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None}"
            f")>"
        )


class VideoGenerationJobParameters(Base):
    """Video generation parameters"""

    __tablename__ = "video_generation_job_parameters"

    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("video_generation_jobs.job_id", ondelete="CASCADE"),
        primary_key=True,
    )

    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Video specifications
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    video_length: Mapped[int] = mapped_column(Integer, nullable=False)  # seconds
    fps: Mapped[int] = mapped_column(Integer, nullable=False)

    # Generation parameters
    inference_steps: Mapped[int] = mapped_column(Integer, nullable=False)
    guidance_scale: Mapped[float] = mapped_column(Float, nullable=False)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    base_model: Mapped[str] = mapped_column(String(100), nullable=False)
    motion_adapter: Mapped[str] = mapped_column(String(200), nullable=False)
    output_format: Mapped[str] = mapped_column(String(10), nullable=False)

    # Complex parameters
    loras: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    additional_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    job: Mapped["VideoGenerationJob"] = relationship(
        "VideoGenerationJob", 
        back_populates="parameters"
    )

    def __repr__(self) -> str:
        return (
            f"<VideoGenerationJobParameters("
            f"job_id='{self.job_id}', "
            f"dimensions={self.width}x{self.height}, "
            f"duration={self.video_length}s@{self.fps}fps, "
            f"model='{self.base_model}', "
            f"steps={self.inference_steps}"
            f")>"
        )


class VideoGenerationJobResult(Base):
    """Video generation results and storage information"""

    __tablename__ = "video_generation_job_results"

    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("video_generation_jobs.job_id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Storage information
    minio_object_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    minio_bucket: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Processing timing
    generation_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    result_created_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    job: Mapped["VideoGenerationJob"] = relationship(
        "VideoGenerationJob",
        back_populates="result",
    )

    def __repr__(self) -> str:
        size_mb = f"{self.file_size_bytes / 1024 / 1024:.1f}MB" if self.file_size_bytes else "unknown"
        gen_time = f"{self.generation_time_seconds:.1f}s" if self.generation_time_seconds else "unknown"
        
        return (
            f"<VideoGenerationJobResult("
            f"job_id='{self.job_id}', "
            f"size={size_mb}, "
            f"generation_time={gen_time}, "
            f"bucket='{self.minio_bucket}'"
            f")>"
        )
