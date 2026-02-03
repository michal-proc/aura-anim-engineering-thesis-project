from .video_routes import get_video_router
from .auth_routes import get_auth_router
from .accounts_routes import get_accounts_router


__all__ = [
    "get_video_router",
    "get_auth_router",
    "get_accounts_router",
]
