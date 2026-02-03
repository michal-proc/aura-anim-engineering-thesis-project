import os
from typing import List

from backend.config.factories import create_config_manager
from backend.config.management.config_type import ConfigType
from backend.video.schemas.api_schemas import VideoExplore

BACKEND_URL = os.getenv("BACKEND_URL")

class VideoExploreService:
    """Service that returns a simple list of Explore videos."""

    def __init__(self):
        self.config = create_config_manager().get_config(ConfigType.VIDEO_EXPLORE)

    def get_explore_videos(self) -> List[VideoExplore]:
        base = f"{BACKEND_URL}/static/explore/"

        return [
            VideoExplore(
                name=v["name"],
                prompt=v["prompt"],
                url=base + v["file_name"]
            )
            for v in self.config.get("videos", [])
        ]
