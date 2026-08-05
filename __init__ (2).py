"""روتر لیدها — برای داشبورد ساده (بخش ۲۶ سند) و تست."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models
from ..database import get_db
from ..schemas import LeadOut

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("", response_model=list[LeadOut])
async def list_leads(limit: int = 50, db: AsyncSession = Depends(get_db)) -> list[models.Lead]:
    result = await db.execute(
        select(models.Lead).order_by(models.Lead.created_at.desc()).limit(min(limit, 200))
    )
    return list(result.scalars().all())


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)) -> models.Lead:
    lead = await db.get(models.Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="لید پیدا نشد")
    return lead
