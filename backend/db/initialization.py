import logging
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError

from backend.db.base import Base

from backend.accounts.models import *
from backend.video.models import *


logger = logging.getLogger(__name__)


def initialize_database(engine: Engine):
    """
    Initialize the database from an empty starting point.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database table: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during initialization")
        raise
