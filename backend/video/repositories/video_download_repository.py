from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.video.models import VideoGenerationJobParameters, VideoGenerationJobResult


class VideoDownloadRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_video_file_info(self, job_id: str) -> dict | None:
        """
        Get specific fields needed to construct VideoFile domain object.

        Returns:
            Dict with video file information or None
        """
        stmt = (
            select(
                VideoGenerationJobParameters.width,
                VideoGenerationJobParameters.height,
                VideoGenerationJobParameters.video_length,
                VideoGenerationJobParameters.fps,
                VideoGenerationJobParameters.output_format,
                VideoGenerationJobResult.minio_object_key,
                VideoGenerationJobResult.file_size_bytes,
                VideoGenerationJobResult.result_created_at,
            )
            .join(VideoGenerationJobResult, VideoGenerationJobParameters.job_id == VideoGenerationJobResult.job_id)
            .where(VideoGenerationJobParameters.job_id == job_id)
        )

        result = self.db.execute(stmt).first()
        if not result:
            return None
        
        return {
            "job_id": job_id,
            "object_key": result.minio_object_key,
            "duration_seconds": result.video_length,
            "width": result.width,
            "height": result.height,
            "fps": result.fps,
            "format": result.output_format,
            "file_size_bytes": result.file_size_bytes,
            "created_at": result.result_created_at,
        }
