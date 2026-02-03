"""Video job processing business logic"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from backend.video.factories.repositories import create_video_job_repository
from backend.video.models.models import (
    VideoGenerationJob,
    VideoGenerationJobParameters,
    VideoGenerationJobResult,
)
from backend.video.constants import JobStatus
from backend.video.schemas import VideoGenerationSpec
from backend.video.schemas.api_schemas import (
    VideoListItem,
    VideoJobInfo,
    VideoJobParameters,
    JobDetail,
    JobParameters,
    JobListMeta,
)

logger = logging.getLogger(__name__)


class VideoJobService:
    """Manages video generation job processing parameters and progress info."""

    def create_job(self, spec: VideoGenerationSpec, user_id: int | None = None) -> str:
        """
        Create a new video generation job.
        
        Args:
            spec: Complete specification for video generation
            
        Returns:
            job_id: UUID string of the created job
            
        Raises:
            RuntimeError: If job creation fails
        """
        try:
            job_id = str(uuid.uuid4())

            # Set default video name
            video_name = spec.prompt
            if len(video_name) > 50:
                video_name = video_name[:47] + "..."

            # Create main job record
            job = VideoGenerationJob(
                job_id=job_id,
                name=video_name,
                user_id=user_id,
                status=JobStatus.PENDING,
                progress_percentage=0,
            )

            # Create parameters record
            params = VideoGenerationJobParameters(
                job_id=job_id,
                prompt=spec.prompt,
                negative_prompt=spec.negative_prompt,
                width=spec.width,
                height=spec.height,
                video_length=spec.video_length,
                fps=spec.fps.value,
                inference_steps=spec.inference_steps,
                guidance_scale=spec.guidance_scale,
                seed=spec.seed,
                base_model=spec.base_model.value,
                motion_adapter=spec.motion_adapter.value,
                output_format=spec.output_format.value,
                loras=spec.loras,
                additional_params=spec.additional_params,
            )

            with create_video_job_repository() as video_job_repository:
                video_job_repository.create_job_with_parameters(job, params)

            logger.info(f"Created job {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            raise RuntimeError(f"Failed to create job: {e}")

    def update_video(
            self,
            job_id: str,
            user_id: int,
            name: Optional[str] = None,
            shared: Optional[bool] = None,
    ) -> VideoListItem | None:
        """
        Update video metadata (name, shared) for a given user.

        Args:
            job_id: Video ID (job ID)
            user_id: Owner user ID
            name: New name, or None to leave unchanged
            shared: New shared flag, or None to leave unchanged

        Returns:
            Updated VideoListItem if video exists and belongs to user, otherwise None.
        """
        try:
            with create_video_job_repository() as video_job_repository:
                job = video_job_repository.get_job_by_id(job_id)

                if not job or job.user_id != user_id:
                    return None

                if not job.parameters:
                    return None

                values = {}
                if name is not None:
                    values["name"] = name
                if shared is not None:
                    values["shared"] = shared

                video_job_repository.update_video_metadata(job_id, values)

                return self._convert_job_to_video_list_item(job)
        except Exception as e:
            logger.error(f"Failed to update video {job_id}: {e}")
            raise

    def get_job_status(self, job_id: str) -> tuple[str, JobStatus, int] | None:
        """
        Get job status.
        
        Args:
            job_id: Job UUID string
            
        Returns:
            A tuple of job status and progress percentage or None if not found.
        """
        try:
            with create_video_job_repository() as video_job_repository:
                job = video_job_repository.get_job_by_id(job_id)

                if not job:
                    return None

                return (job.name, job.status, job.progress_percentage)
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            raise

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job if it's not already completed.
        
        Args:
            job_id: Job UUID string
            
        Returns:
            True if successfully cancelled, False otherwise
        """
        try:
            with create_video_job_repository() as video_job_repository:
                job = video_job_repository.get_job_by_id(job_id)

                if not job:
                    logger.warning(f"Job {job_id} not found")
                    return False
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                    logger.warning(f"Cannot cancel job {job_id}: already in terminal state {job.status}")
                    return False

                success = video_job_repository.update_job_status(job_id, JobStatus.CANCELLED)

                if success:
                    logger.info(f"Marked job {job_id} as cancelled in database")

                return success
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False

    def is_job_cancelled(self, job_id: str) -> bool:
        """
        Check if job is cancelled.

        Args:
            job_id: Job UUID string

        Returns:
            False if job not found or not cancelled, True if cancelled
        """
        try:
            with create_video_job_repository() as video_job_repository:
                job = video_job_repository.get_job_by_id(job_id)

                if not job:
                    logger.warning(f"Job {job_id} not found when checking cancellation status")
                    return False

                return job.status == JobStatus.CANCELLED
        except Exception as e:
            logger.error(f"Failed to check if job {job_id} is cancelled: {e}")
            return False

    def is_job_completed(self, job_id: str) -> bool:
        """
        Check if job is completed.

        Args:
            job_id: Job UUID string

        Returns:
            False if job not found or not completed, True if completed
        """
        try:
            with create_video_job_repository() as video_job_repository:
                job = video_job_repository.get_job_by_id(job_id)

                if not job:
                    logger.warning(f"Job {job_id} not found when checking completion status")
                    return False

                return job.status == JobStatus.COMPLETED
        except Exception as e:
            logger.error(f"Failed to check if job {job_id} is completed: {e}")
            return False

    def mark_job_as_processing(self, job_id: str) -> bool:
        """
        Change the status of the job to PROCESSING.

        Args:
            job_id: Job UUID string

        Returns:
            True if the job is found and marked, False otherwise
        """
        try:
            with create_video_job_repository() as video_job_repository:
                return video_job_repository.update_job_status(job_id, JobStatus.PROCESSING)
        except Exception as e:
            logger.error(f"Failed to mark the job {job_id} as processing: {e}")
            return False

    def mark_job_as_failed(self, job_id: str) -> bool:
        """
        Change the status of the job to FAILED.

        Args:
            job_id: Job UUID string

        Returns:
            True if the job is found and marked, False otherwise
        """
        try:
            with create_video_job_repository() as video_job_repository:
                return video_job_repository.update_job_status(job_id, JobStatus.FAILED)
        except Exception as e:
            logger.error(f"Failed to mark the job {job_id} as failed: {e}")
            return False

    def mark_job_as_completed(self, job_id: str) -> bool:
        """
        Change the status of the job to COMPLETED.

        Args:
            job_id: Job UUID string

        Returns:
            True if the job is found and marked, False otherwise
        """
        try:
            completed_at = datetime.now(timezone.utc)
            with create_video_job_repository() as video_job_repository:
                return video_job_repository.complete_job(job_id, completed_at)
        except Exception as e:
            logger.error(f"Failed to mark the job {job_id} as completed: {e}")
            return False

    def mark_job_as_cancelled(self, job_id: str) -> bool:
        """
        Change the status of the job to CANCELLED.

        Args:
            job_id: Job UUID string

        Returns:
            True if the job is found and marked, False otherwise
        """
        try:
            with create_video_job_repository() as video_job_repository:
                return video_job_repository.update_job_status(job_id, JobStatus.CANCELLED)
        except Exception as e:
            logger.error(f"Failed to mark the job {job_id} as cancelled: {e}")
            return False

    def update_job_progress(self, job_id: str, progress: int, step: str) -> bool:
        """
        Update the progress of the video generation job.

        Args:
            job_id: Job UUID string
            progress: Current progress as percentage
            step: Current step in processing

        Returns:
            True if the job is found and updated, False otherwise
        """
        if progress < 0 or progress > 100:
            raise ValueError("progress is represented as percentage of completion")

        try:
            with create_video_job_repository() as video_job_repository:
                return video_job_repository.update_job_progress(job_id, progress, step)
        except Exception as e:
            logger.error(f"Failed to update progress for the job {job_id}: {e}")
            return False

    def update_error_message(self, job_id: str, error_message: str) -> bool:
        """
        Update the error message for the video generation job.

        Args:
            job_id: Job UUID string
            error_message: Error message of the generation failure

        Returns:
            True if the error message is updated, False otherwise
        """
        try:
            with create_video_job_repository() as video_job_repository:
                return video_job_repository.update_error_message(job_id, error_message)
        except Exception as e:
            logger.error(f"Failed to update error message for the job {job_id}: {e}")
            return False

    def save_generation_result(self, job_id: str, object_key: str, bucket: str, file_size_bytes: int) -> bool:
        try:
            creation_timestamp = datetime.now(timezone.utc)
            job_result = VideoGenerationJobResult(
                job_id=job_id,
                minio_object_key=object_key,
                minio_bucket=bucket,
                file_size_bytes=file_size_bytes,
                result_created_at=creation_timestamp,
            )

            with create_video_job_repository() as video_job_repository:
                video_job_repository.create_job_result(job_result)
        except Exception as e:
            logger.error(f"Failed to save storage info for the job {job_id}: {e}")
            return False

        return True

    def get_all_videos(self, user_id: int | None = None) -> list[VideoListItem]:
        """
        Get all videos with job details.

        Args:
            user_id: User ID to filter videos

        Returns:
            List of video items with job information
        """
        try:
            with create_video_job_repository() as video_job_repository:
                jobs = video_job_repository.get_all_jobs_with_details(user_id)

                video_list = []
                for job in jobs:
                    if not job.parameters:
                        continue

                    video_item = self._convert_job_to_video_list_item(job)
                    video_list.append(video_item)

                return video_list
        except Exception as e:
            raise

    def get_unread_jobs(self, user_id: int) -> tuple[list[JobDetail], JobListMeta]:
        """
        Get all unread jobs for a user with metadata.

        Args:
            user_id: User ID to filter jobs

        Returns:
            Tuple of (list of unread jobs, metadata)
        """
        try:
            with create_video_job_repository() as video_job_repository:
                unread_jobs = video_job_repository.get_unread_jobs_with_details(user_id)
                statistics = video_job_repository.get_job_statistics(user_id)

                job_details = []
                for job in unread_jobs:
                    if not job.parameters:
                        continue

                    job_detail = self._convert_job_to_job_detail(job)
                    job_details.append(job_detail)

                meta = JobListMeta(
                    total_count=statistics["total_count"],
                    active_count=statistics["active_count"],
                    failed_count=statistics["failed_count"],
                    completed_count=statistics["completed_count"],
                    unread_count=statistics["unread_count"],
                )

                return job_details, meta
        except Exception as e:
            logger.error(f"Failed to get unread jobs for user {user_id}: {e}")
            raise

    def get_video_detail(self, video_id: str, user_id: int) -> VideoListItem | None:
        """
        Get detailed information about a specific video.

        Args:
            video_id: Video ID (job ID)
            user_id: User ID for authorization

        Returns:
            VideoListItem if video exists and belongs to user, None otherwise
        """
        try:
            with create_video_job_repository() as video_job_repository:
                job = video_job_repository.get_job_by_id(video_id)

                if not job or job.user_id != user_id:
                    return None

                if not job.parameters:
                    return None

                return self._convert_job_to_video_list_item(job)
        except Exception as e:
            logger.error(f"Failed to get video detail for {video_id}: {e}")
            raise

    def get_shared_video_detail(self, video_id: str) -> VideoListItem | None:
        """
        Get detailed information about a specific video.

        Args:
            video_id: Video ID (job ID)

        Returns:
            VideoListItem if video exists and belongs to user, None otherwise
        """
        try:
            with create_video_job_repository() as video_job_repository:
                job = video_job_repository.get_job_by_id(video_id)

                if not job or job.shared is not True:
                    return None

                if not job.parameters:
                    return None

                return self._convert_job_to_video_list_item(job)
        except Exception as e:
            logger.error(f"Failed to get video detail for {video_id}: {e}")
            raise

    def delete_video(self, video_id: str, user_id: int) -> bool:
        """
        Delete a video.

        Args:
            video_id: Video ID (job ID)
            user_id: User ID for authorization

        Returns:
            True if video was deleted, False if not found or unauthorized
        """
        try:
            with create_video_job_repository() as video_job_repository:
                job = video_job_repository.get_job_by_id(video_id)

                if not job or job.user_id != user_id:
                    logger.warning(f"Video {video_id} not found or unauthorized for user {user_id}")
                    return False

                success = video_job_repository.delete_job(video_id)

                if success:
                    logger.info(f"Deleted video {video_id}")

                return success
        except Exception as e:
            logger.error(f"Failed to delete video {video_id}: {e}")
            return False

    def _convert_job_to_job_detail(self, job: VideoGenerationJob) -> JobDetail:
        """
        Convert a VideoGenerationJob to a JobDetail.

        Args:
            job: Database job model

        Returns:
            JobDetail for API response
        """
        job_params = JobParameters(
            prompt=job.parameters.prompt,
            width=job.parameters.width,
            height=job.parameters.height,
            video_length=job.parameters.video_length,
            fps=job.parameters.fps,
            output_format=job.parameters.output_format,
        )

        return JobDetail(
            job_id=job.job_id,
            status=job.status,
            progress_percentage=job.progress_percentage,
            current_step=job.current_step,
            created_at=job.created_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            marked_as_read=job.marked_as_read,
            parameters=job_params,
        )

    def _convert_job_to_video_list_item(self, job: VideoGenerationJob) -> VideoListItem:
        """
        Convert a VideoGenerationJob to a VideoListItem.

        Args:
            job: Database job model

        Returns:
            VideoListItem for API response
        """

        job_params = VideoJobParameters(
            prompt=job.parameters.prompt,
            width=job.parameters.width,
            height=job.parameters.height,
            video_length=job.parameters.video_length,
            fps=job.parameters.fps,
        )

        job_info = VideoJobInfo(
            job_id=job.job_id,
            status=job.status,
            progress_percentage=job.progress_percentage,
            created_at=job.created_at,
            completed_at=job.completed_at,
            parameters=job_params,
        )

        return VideoListItem(
            id=job.job_id,
            user_id=job.user_id,
            name=job.name,
            shared=job.shared,
            created_at=job.created_at,
            job=job_info,
        )
