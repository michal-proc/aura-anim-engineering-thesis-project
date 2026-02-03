from ray import serve

from backend.video.services import (
    VideoGenerationService,
    VideoJobService,
    VideoDownloadService,
    VideoExploreService
)
from backend.storage.factories import create_video_storage_service


def create_video_generation_service() -> VideoGenerationService:
    return VideoGenerationService(serve.get_deployment_handle(deployment_name="VideoGenerationPipeline", app_name="pipeline_app"))


def create_video_job_service() -> VideoJobService:
    return VideoJobService()


def create_video_download_service() -> VideoDownloadService:
    return VideoDownloadService(
        create_video_storage_service(),
        create_video_job_service(),
    )

def create_video_explore_service() -> VideoExploreService:
    return VideoExploreService()
