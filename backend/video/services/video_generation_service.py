"""Business logic for invoking the video generation pipeline"""

import logging
from ray.serve.handle import DeploymentHandle

from backend.video.factories.repositories import create_video_generation_repository
from backend.pipeline.schemas import VideoParameters


logger = logging.getLogger(__name__)


class VideoGenerationService:
    """Invokes video generation pipeline."""
    
    def __init__(self, video_generator: DeploymentHandle):
        self.video_generator = video_generator
    
    async def schedule_generation(self, job_id: str) -> None:
        """
        Triggers video generation pipeline and registers task for cancellation.

        Args:
            job_id: Job UUID
        """
        try:
            logger.info(f"Scheduling video generation for job {job_id}")

            with create_video_generation_repository() as video_generation_repository:
                retrieved_generation_params = video_generation_repository.get_video_parameters(job_id)

                if not retrieved_generation_params:
                    logger.error("Video generation parameters could not be retrieved")
                    raise RuntimeError("could not retrieve video generation parameters from the database")
                          
            video_generation_params = VideoParameters(**retrieved_generation_params)

            self.video_generator.generate_video.remote(video_generation_params, job_id)

            logger.info(f"Video generation was triggered for job {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger video generation for job {job_id}: {e}")
            raise
