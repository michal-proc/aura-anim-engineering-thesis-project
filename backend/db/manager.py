"""Database connection management"""

import logging
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


logger = logging.getLogger(__name__)

# Global database manager instance
_database_manager = None


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, database_url: str, echo: bool = False):
        self.engine = create_engine(
            database_url,
            echo=echo,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    @contextmanager
    def get_managed_session(self) -> Generator[Session, None, None]:
        """Create a new database session with automatic transaction management."""
        session = self.session_factory()
        try:
            with session.begin():
                yield session
        finally:
            session.close()


def initialize_db_manager(database_url: str, echo: bool = False):
    """Initialize the global database manager instance"""
    global _database_manager
    _database_manager = DatabaseManager(database_url, echo)
    return _database_manager


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    if _database_manager is None:
        raise RuntimeError("DatabaseManager not initialized")
    return _database_manager
