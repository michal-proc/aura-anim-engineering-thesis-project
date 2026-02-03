from contextlib import contextmanager
from typing import Generator

from backend.accounts.repositories import UserRepository
from backend.db.manager import get_db_manager


@contextmanager
def create_user_repository() -> Generator[UserRepository, None, None]:
    """Create a user repository with managed session."""
    with get_db_manager().get_managed_session() as session:
        yield UserRepository(session)
