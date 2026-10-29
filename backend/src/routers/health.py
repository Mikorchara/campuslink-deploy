from fastapi import APIRouter
from sqlalchemy import text

from src.dependencies.auth import DatabaseSession
from src.schemas.common import ApiResponse, success


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=ApiResponse[dict[str, str]])
def health_check(db: DatabaseSession) -> ApiResponse[dict[str, str]]:
    db.execute(text("SELECT 1"))
    return success({"status": "ok", "database": "connected"})

