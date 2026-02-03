from datetime import datetime, timedelta

from backend.video.schemas import VideoDownloadInfo, VideoFile
from backend.storage.services.video_storage_service import VideoStorageService
from backend.video.services.video_job_service import VideoJobService
from backend.video.factories.repositories import create_video_download_repository


class VideoDownloadService:
    """Retrieves generated video details."""
    
    URL_EXPIRATION_IN_HOURS = 2

    def __init__(self, video_storage_service: VideoStorageService, video_job_service: VideoJobService):
        self.video_storage_service = video_storage_service
        self.video_job_service = video_job_service

    def get_download_info(self, job_id: str) -> VideoDownloadInfo | None:
        """
        Get download information for a completed video generation job.

        Args:
            job_id: Job identifier
        
            Returns:
                VideoDownloadInfo if job is completed, None otherwise
        """
        if not self.video_job_service.is_job_completed(job_id):
            return None
        
        # Retrieve generation info from the database
        with create_video_download_repository() as video_download_repository:
            video_info = video_download_repository.get_video_file_info(job_id)

            if not video_info:
                return None
            
            video_file = VideoFile(**video_info)

        # Generate a download URL and compute expiration date
        download_url = self.video_storage_service.get_download_url(
            video_file.object_key,
            self.URL_EXPIRATION_IN_HOURS,
        )
        expires_at = datetime.now() + timedelta(hours=self.URL_EXPIRATION_IN_HOURS)

        return VideoDownloadInfo(
            job_id=job_id,
            download_url=download_url,
            expires_at=expires_at,
            video_file=video_file,
        )
