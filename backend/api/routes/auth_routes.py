from fastapi import APIRouter
from backend.auth.endpoints import router


def get_auth_router() -> APIRouter:
    return router
