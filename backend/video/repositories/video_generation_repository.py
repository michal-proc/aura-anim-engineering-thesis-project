from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.video.models import VideoGenerationJobParameters


class VideoGenerationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_video_parameters(self, job_id: str) -> dict | None:
        """
        Get all fields needed to construct VideoParameters model.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Dict with video parameters or None if job not found
        """
        stmt = (
            select(
                VideoGenerationJobParameters.prompt,
                VideoGenerationJobParameters.negative_prompt,
                VideoGenerationJobParameters.width,
                VideoGenerationJobParameters.height,
                VideoGenerationJobParameters.video_length,
                VideoGenerationJobParameters.fps,
                VideoGenerationJobParameters.inference_steps,
                VideoGenerationJobParameters.guidance_scale,
                VideoGenerationJobParameters.seed,
                VideoGenerationJobParameters.base_model,
                VideoGenerationJobParameters.motion_adapter,
                VideoGenerationJobParameters.output_format,
                VideoGenerationJobParameters.loras,
            )
            .where(VideoGenerationJobParameters.job_id == job_id)
        )
        
        result = self.db.execute(stmt).first()
        if not result:
            return None
        
        return {
            "prompt": result.prompt,
            "negative_prompt": result.negative_prompt,
            "video_width": result.width,
            "video_height": result.height,
            "video_length": result.video_length,
            "fps": result.fps,
            "inference_steps": result.inference_steps,
            "guidance_scale": result.guidance_scale,
            "seed": result.seed,
            "base_model": result.base_model,
            "motion_adapter": result.motion_adapter,
            "output_format": result.output_format,
            "loras": result.loras or {},
        }
