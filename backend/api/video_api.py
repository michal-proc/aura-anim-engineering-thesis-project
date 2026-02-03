from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from ray import serve

from backend.api.routes import (
    get_video_router,
    get_auth_router,
    get_accounts_router,
)
from backend.deployment.initialization import initialize_deployment

BASE_DIR = Path(__file__).resolve().parent.parent


def create_fastapi_app():
    fastapi_app = FastAPI(title="Text-to-Video Generation API")

    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @fastapi_app.get("/")
    async def root():
        """Root endpoint - redirect to API documentation"""
        return RedirectResponse(url="/docs")

    @fastapi_app.get("/health")
    async def health():
        """Health check endpoint for Docker healthcheck and monitoring"""
        return {"status": "healthy"}

    fastapi_app.mount(
        "/static",
        StaticFiles(directory=BASE_DIR / "static"),
        name="static",
    )

    fastapi_app.include_router(get_video_router())
    fastapi_app.include_router(get_auth_router())
    fastapi_app.include_router(get_accounts_router())
    return fastapi_app


@serve.deployment()
@serve.ingress(create_fastapi_app())
class ApiDeployment:
    def __init__(self):
        initialize_deployment()
