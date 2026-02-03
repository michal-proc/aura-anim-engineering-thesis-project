from backend.storage.services import VideoStorageService
from backend.storage.client import MinIOClient


def create_video_storage_service() -> VideoStorageService:
    # TODO: Consider adding bucket_name to configuration.
    bucket_name = "videos"
    return VideoStorageService(MinIOClient(bucket_name=bucket_name))
