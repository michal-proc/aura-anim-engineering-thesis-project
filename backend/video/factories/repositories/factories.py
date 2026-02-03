from contextlib import contextmanager
from typing import Generator

from backend.video.repositories import (
    VideoDownloadRepository,
    VideoJobRepository,
    VideoGenerationRepository,
)
from backend.db.manager import get_db_manager


@contextmanager
def create_video_download_repository() -> Generator[VideoDownloadRepository, None, None]:
    """Create a video download repository with managed session"""
    with get_db_manager().get_managed_session() as session:
        yield VideoDownloadRepository(session)

@contextmanager
def create_video_job_repository() -> Generator[VideoJobRepository, None, None]:
    """Create a video job repository with managed session"""
    with get_db_manager().get_managed_session() as session:
        yield VideoJobRepository(session)

@contextmanager
def create_video_generation_repository() -> Generator[VideoGenerationRepository, None, None]:
    """Create a video generation repository with managed session"""
    with get_db_manager().get_managed_session() as session:
        yield VideoGenerationRepository(session)
