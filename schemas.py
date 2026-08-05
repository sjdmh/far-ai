"""روتر سلامت و خانه."""
from fastapi import APIRouter
from sqlalchemy import text

from ..config import get_settings
from ..database import engine
from ..schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/")
async def root() -> dict:
    return {
        "app": get_settings().app_name,
        "status": "Far AI is running 🚀",
        "docs": "/docs",
    }


@router.get("/health", response_model=HealthOut)
async def health() -> HealthOut:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return HealthOut(status="ok" if db_status == "ok" else "degraded", database=db_status)
