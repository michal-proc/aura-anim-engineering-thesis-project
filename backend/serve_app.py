"""Ray Serve application entrypoint"""

import ray
from ray import serve
import time
import signal
import sys
import os
import logging

from backend.pipeline import VideoGenerationPipeline
from backend.pipeline.deployments import (
    VideoGeneratorDeployment,
    VideoPreprocessorDeployment,
    VideoPostprocessorDeployment,
    FrameInterpolatorDeployment,
    FrameUpscalerDeployment,
)
from backend.config.factories import create_config_manager
from backend.api import ApiDeployment
from backend.db.manager import initialize_db_manager
from backend.db.initialization import initialize_database


logger = logging.getLogger(__name__)


def initialize_app_database():
    """Initialize database tables"""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://dev_user:dev_password@postgres-dev:5432/text_to_video_dev"
    )

    logger.info("Initializing database tables...")
    db_manager = initialize_db_manager(database_url, echo=False)
    initialize_database(db_manager.engine)
    logger.info("Database initialization complete!")


def create_pipeline_app():
    """Create the ingress deployment for the pipeline"""
    pipeline_app = VideoGenerationPipeline.bind(
        create_config_manager(),
        VideoGeneratorDeployment.bind(),
        FrameInterpolatorDeployment.bind(),
        FrameUpscalerDeployment.bind(),
        VideoPreprocessorDeployment.bind(),
        VideoPostprocessorDeployment.bind(),
    )

    return pipeline_app


def create_api_app():
    """Create the ingress deployment for the video API"""
    api_app = ApiDeployment.bind()

    return api_app


def signal_handler(signum, frame):
    """
    Handle shutdown signals gracefully.
    """
    serve.shutdown()
    ray.shutdown()

    print("Application shutdown complete.")
    sys.exit(0)


if __name__ == "__main__":
    initialize_app_database()
    
    # Initialize ray and configure it so that it's accessible outside of the container
    ray.init()
    serve.start(detached=True, http_options={"host": "0.0.0.0"})

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start Ray Serve with the deployment

    # route_prefix=None specifies that the pipeline will not be exposed over HTTP
    serve.run(create_pipeline_app(), name="pipeline_app", route_prefix=None)
    serve.run(create_api_app(), name="api_app", route_prefix="/")

    print("Ray Serve application is running. Press Ctrl+C to stop.")
    print("Application is ready at http://0.0.0.0:8000/")

    # Keep the container running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        serve.shutdown()
        ray.shutdown()
