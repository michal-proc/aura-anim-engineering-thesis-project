import logging
import os

from backend.storage.client import MinIOClient


logger = logging.getLogger(__name__)


class VideoStorageService:
    """Handles video storage and retrieval from object storage"""
    
    def __init__(self, minio_client: MinIOClient):
        self.minio_client = minio_client
    
    def generate_object_key(self, job_id: str, file_extension: str) -> str:
        """
        Generate a unique object key for video storage.
        Args:
            job_id: Job identifier
            file_extension: File extension
            
        Returns:
            Object key for MinIO storage
        """
        return f"{job_id}/{job_id}{file_extension}"
    
    def upload_video(self, local_video_path: str, job_id: str) -> tuple[str, int]:
        """
        Upload video to MinIO storage.
        
        Args:
            local_video_path: Path to local video file
            job_id: Job identifier for generating object key
            
        Returns:
            Tuple of (object_key, file_size_bytes)
            
        Raises:
            Exception: If upload fails
        """
        try:
            file_extension = os.path.splitext(local_video_path)[1]
            object_key = self.generate_object_key(job_id, file_extension)
            
            self.minio_client.upload_file(local_video_path, object_key)
            
            file_size = os.path.getsize(local_video_path)
            
            logger.info(f"Video uploaded successfully: {object_key} ({file_size} bytes)")
            return object_key, file_size
            
        except Exception as e:
            logger.error(f"Failed to upload video for job {job_id}: {e}")
            raise
    
    def get_download_url(self, object_key: str, expires_hours: int = 1) -> str:
        """
        Get presigned download URL for a video.
        
        Args:
            object_key: MinIO object key
            expires_hours: URL expiration time in hours
            
        Returns:
            Presigned download URL
            
        Raises:
            Exception: If URL generation fails
        """
        try:
            return self.minio_client.get_presigned_url(object_key, expires_hours=expires_hours)
        except Exception as e:
            logger.error(f"Failed to generate download URL for {object_key}: {e}")
            raise
    
    def cleanup_local_file(self, file_path: str) -> bool:
        """
        Clean up local video file after upload.
        
        Args:
            file_path: Path to local file
            
        Returns:
            True if cleaned up successfully, False otherwise
        """
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up local file: {file_path}")
                return True
            return True  # File doesn't exist, consider it cleaned
        except Exception as e:
            logger.warning(f"Failed to clean up local file {file_path}: {e}")
            return False
    
    def get_bucket_name(self) -> str:
        """Get the bucket name used by this storage service."""
        return self.minio_client.bucket_name
    
    def check_connection(self) -> bool:
        """Test MinIO connection."""
        try:
            return self.minio_client.check_connection()
        except Exception as e:
            logger.error(f"MinIO connection check failed: {e}")
            return False

    def stream_video(self, object_key: str):
        """
        Stream video file from MinIO.

        Args:
            object_key: MinIO object key

        Returns:
            HTTPResponse object for streaming

        Raises:
            Exception: If streaming fails
        """
        try:
            return self.minio_client.get_object(object_key)
        except Exception as e:
            logger.error(f"Failed to stream video from {object_key}: {e}")
            raise
