"""روتر آمار داشبورد — بخش ۲۶ سند.

- GET /api/stats : خلاصه لیدها برای داشبورد
- اگر ADMIN_TOKEN در .env تنظیم شده باشد، درخواست نیاز به هدر X-Admin-Token دارد.
"""
from collections import Counter

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models
from ..config import get_settings
from ..database import get_db
from ..services import lead_scoring

router = APIRouter(prefix="/api", tags=["stats"])


async def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if settings.admin_token and x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="دسترسی غیرمجاز")


def _lead_dict(lead: models.Lead) -> dict:
    return {
        "id": lead.id,
        "name": lead.name,
        "company": lead.company,
        "service": lead.service or [],
        "lead_score": lead.lead_score,
        "level": lead_scoring.lead_level(lead.lead_score),
        "status": lead.status,
        "source": lead.source,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
    }


@router.get("/stats", dependencies=[Depends(require_admin)])
async def stats(db: AsyncSession = Depends(get_db)) -> dict:
    settings = get_settings()

    total = (
        await db.execute(select(func.count()).select_from(models.Lead))
    ).scalar_one()
    today = (
        await db.execute(
            select(func.count())
            .select_from(models.Lead)
            .where(func.date(models.Lead.created_at) == func.current_date())
        )
    ).scalar_one()
    hot = (
        await db.execute(
            select(func.count())
            .select_from(models.Lead)
            .where(models.Lead.lead_score >= settings.notify_score_threshold)
        )
    ).scalar_one()
    avg = (
        await db.execute(select(func.avg(models.Lead.lead_score)))
    ).scalar_one() or 0

    leads = (await db.execute(select(models.Lead))).scalars().all()
    by_service: Counter = Counter()
    for lead in leads:
        for service in lead.service or []:
            by_service[service] += 1
    by_source = Counter(lead.source or "website" for lead in leads)

    recent = sorted(leads, key=lambda l: l.created_at or __import__("datetime").datetime.min, reverse=True)[:10]

    return {
        "total": total,
        "today": today,
        "hot": hot,
        "average_score": round(float(avg), 1),
        "threshold": settings.notify_score_threshold,
        "by_service": dict(by_service),
        "by_source": dict(by_source),
        "recent": [_lead_dict(l) for l in recent],
    }
