"""Far AI — نقطه ورود برنامه FastAPI."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import Base, engine
from .routers import chat, health, leads, stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("far_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # برای MVP جدول‌ها خودکار ساخته می‌شوند (بعداً الیمیت/میگریشن اضافه می‌شود)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Far AI شروع به کار کرد 🚀")
    yield
    await engine.dispose()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="دستیار هوشمند آژانس فَر — نسخه ۱",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(leads.router)
app.include_router(stats.router)

# داشبورد ساده — آدرس: /dashboard
_static_dir = Path(__file__).resolve().parent / "static"
app.mount("/dashboard", StaticFiles(directory=str(_static_dir), html=True), name="dashboard")
