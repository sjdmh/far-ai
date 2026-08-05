"""مدل‌های ورودی/خروجی API (Pydantic)."""
from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = None          # اگر نیامد، سرور یک UUID می‌سازد
    source: str = "website"                # website | telegram
    telegram_id: str | None = None
    telegram_username: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str


class LeadOut(BaseModel):
    id: int
    session_id: str
    name: str | None
    phone: str | None
    telegram_contact: str | None
    company: str | None
    service: list | None
    lead_score: int
    status: str
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status: str
    database: str
