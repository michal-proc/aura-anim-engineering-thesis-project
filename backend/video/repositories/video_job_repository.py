import logging
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, update, delete

from backend.video.models.models import (
    VideoGenerationJob,
    VideoGenerationJobParameters,
    VideoGenerationJobResult,
    JobStatus
)


logger = logging.getLogger(__name__)


class VideoJobRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_job_with_parameters(self, job: VideoGenerationJob, params: VideoGenerationJobParameters) -> VideoGenerationJob:
        """Create a new job with parameters"""
        self.db.add(job)
        self.db.add(params)
        self.db.flush()
        return job
    
    def get_job_by_id(self, job_id: str) -> VideoGenerationJob | None:
        """Get job by ID with all relations loaded"""
        stmt = (
            select(VideoGenerationJob)
            .options(
                selectinload(VideoGenerationJob.parameters),
                selectinload(VideoGenerationJob.result)
            )
            .where(VideoGenerationJob.job_id == job_id)
        )
        
        return self.db.execute(stmt).scalar_one_or_none()

    def update_job_status(self, job_id: str, status: JobStatus) -> bool:
        """Update job status"""
        stmt = (
            update(VideoGenerationJob)
            .where(VideoGenerationJob.job_id == job_id)
            .values(status=status)
        )
        result = self.db.execute(stmt)
        return result.rowcount > 0

    def update_video_metadata(self, job_id: str, values: dict) -> bool:
        """Update video name and/or shared flag."""
        stmt = (
            update(VideoGenerationJob)
            .where(VideoGenerationJob.job_id == job_id)
            .values(**values)
        )
        result = self.db.execute(stmt)
        return result.rowcount > 0

    def complete_job(self, job_id: str, completed_at) -> bool:
        """Mark job as completed with completion timestamp"""
        stmt = (
            update(VideoGenerationJob)
            .where(VideoGenerationJob.job_id == job_id)
            .values(
                status=JobStatus.COMPLETED,
                completed_at=completed_at
            )
        )
        result = self.db.execute(stmt)
        return result.rowcount > 0

    def update_job_progress(self, job_id: str, progress: int, step: str) -> bool:
        """Update job progress"""
        stmt = (
            update(VideoGenerationJob)
            .where(VideoGenerationJob.job_id == job_id)
            .values(
                progress_percentage=progress,
                current_step=step,
            )
        )
        result = self.db.execute(stmt)
        return result.rowcount > 0
    
    def update_error_message(self, job_id: str, error_message: str) -> bool:
        """Update error message for the job"""
        stmt = (
            update(VideoGenerationJob)
            .where(VideoGenerationJob.job_id == job_id)
            .values(error_message=error_message)
        )
        result = self.db.execute(stmt)
        return result.rowcount > 0
        
    def create_job_result(self, result: VideoGenerationJobResult) -> VideoGenerationJobResult:
        """Create job result record"""
        self.db.add(result)
        self.db.flush()
        return result

    def get_all_jobs_with_details(self, user_id: int | None = None) -> list[VideoGenerationJob]:
        """
        Get all jobs with parameters and results loaded.
        Optionally filter by user_id.

        Args:
            user_id: User ID to filter jobs

        Returns:
            List of jobs with all relations loaded
        """
        stmt = (
            select(VideoGenerationJob)
            .options(
                selectinload(VideoGenerationJob.parameters),
                selectinload(VideoGenerationJob.result)
            )
            .order_by(VideoGenerationJob.created_at.desc())
        )

        if user_id is not None:
            stmt = stmt.where(VideoGenerationJob.user_id == user_id)

        return list(self.db.execute(stmt).scalars().all())

    def get_unread_jobs_with_details(self, user_id: int) -> list[VideoGenerationJob]:
        """
        Get all unread jobs (marked_as_read=False) for a user with all relations loaded.

        Args:
            user_id: User ID to filter jobs

        Returns:
            List of unread jobs with all relations loaded, ordered by creation date (newest first)
        """
        stmt = (
            select(VideoGenerationJob)
            .options(
                selectinload(VideoGenerationJob.parameters),
                selectinload(VideoGenerationJob.result)
            )
            .where(
                VideoGenerationJob.user_id == user_id,
                VideoGenerationJob.marked_as_read == False
            )
            .order_by(VideoGenerationJob.created_at.desc())
        )

        return list(self.db.execute(stmt).scalars().all())

    def get_job_statistics(self, user_id: int) -> dict[str, int]:
        """
        Get job statistics for a user.

        Args:
            user_id: User ID to get statistics for

        Returns:
            Dictionary with job counts:
            - total_count: Total number of jobs
            - active_count: Number of pending/processing jobs
            - failed_count: Number of failed jobs
            - completed_count: Number of completed jobs
            - unread_count: Number of unread jobs
        """
        all_jobs = self.get_all_jobs_with_details(user_id)

        total_count = len(all_jobs)
        active_count = sum(1 for job in all_jobs if job.status in [JobStatus.PENDING, JobStatus.PROCESSING])
        failed_count = sum(1 for job in all_jobs if job.status == JobStatus.FAILED)
        completed_count = sum(1 for job in all_jobs if job.status == JobStatus.COMPLETED)
        unread_count = sum(1 for job in all_jobs if not job.marked_as_read)

        return {
            "total_count": total_count,
            "active_count": active_count,
            "failed_count": failed_count,
            "completed_count": completed_count,
            "unread_count": unread_count,
        }

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job and all its related data (parameters, results).
        Cascading deletes are handled by the database.

        Args:
            job_id: Job ID to delete

        Returns:
            True if job was deleted, False otherwise
        """
        stmt = delete(VideoGenerationJob).where(VideoGenerationJob.job_id == job_id)
        result = self.db.execute(stmt)
        return result.rowcount > 0
