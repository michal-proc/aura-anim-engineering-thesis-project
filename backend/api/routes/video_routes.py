from fastapi import APIRouter
from backend.video.endpoints import router


def get_video_router() -> APIRouter:
    return router
