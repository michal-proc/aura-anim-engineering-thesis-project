"""Initialization utilities for Ray Serve deployments"""

import os
import logging
from backend.db.manager import initialize_db_manager


logger = logging.getLogger(__name__)

_deployment_initialized = False


def initialize_deployment():
    """
    Initialize deployment-specific resources.
    
    This should be called in the __init__ of each Ray Serve deployment
    to initialize process-specific resources.
    """
    global _deployment_initialized
    
    if _deployment_initialized:
        logger.debug("Deployment already initialized, skipping")
        return
    
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://dev_user:dev_password@postgres-dev:5432/text_to_video_dev"
    )
    
    logger.info("Initializing deployment resources...")
    
    initialize_db_manager(database_url, echo=False)
    logger.info("DatabaseManager initialized in deployment")
    
    _deployment_initialized = True
    logger.info("Deployment initialization complete")
