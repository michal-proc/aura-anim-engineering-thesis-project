from fastapi import APIRouter
from backend.accounts.endpoints import router


def get_accounts_router() -> APIRouter:
    return router
