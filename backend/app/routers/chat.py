"""روتر اصلی چت — قلب سیستم (POST /api/chat).

جریان (منطبق با بخش ۵ سند):
  1. یافتن/ساخت session
  2. ثبت پیام مشتری
  3. ارسال تاریخچه + System Prompt به LLM
  4. ثبت پاسخ
  5. بررسی پایان نیازسنجی → استخراج لید → امتیازدهی → اعلان به تیم
"""
import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models
from ..config import get_settings
from ..database import get_db
from ..prompts import SYSTEM_PROMPT
from ..schemas import ChatRequest, ChatResponse
from ..services import ai, intent, lead_scoring, notifications, rag

logger = logging.getLogger("far_ai.chat")
router = APIRouter(prefix="/api", tags=["chat"])

# ── Rate Limiter ساده درون‌حافظه (هر session) ─────────────────
_limits: dict[str, deque[float]] = defaultdict(deque)
_limits_lock = asyncio.Lock()


async def _rate_limited(session_id: str, limit: int, window: int = 60) -> bool:
    async with _limits_lock:
        now = time.time()
        dq = _limits[session_id]
        while dq and now - dq[0] > window:
            dq.popleft()
        if len(dq) >= limit:
            return True
        dq.append(now)
        return False


# ── کمکی‌ها ───────────────────────────────────────────────────
async def _load_history(db: AsyncSession, session_id: str) -> list[models.Message]:
    result = await db.execute(
        select(models.Message)
        .where(models.Message.session_id == session_id)
        .order_by(models.Message.id)
    )
    return list(result.scalars().all())


def _to_dict_list(history: list[models.Message]) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in history]


async def _maybe_finalize_lead(
    db: AsyncSession, session: models.Session, history: list[models.Message]
) -> None:
    """اگر لید قبلاً ثبت نشده و گفتگو به حداقل اطلاعات رسیده، لید می‌سازد."""
    settings = get_settings()

    existing = await db.execute(select(models.Lead).where(models.Lead.session_id == session.id))
    if existing.scalar_one_or_none():
        return

    user_messages = [m for m in history if m.role == "user"]
    if len(user_messages) < 3:
        return  # هنوز زود است؛ بگذارید گفتگو ادامه پیدا کند

    # تشخیص سرویس با کلمات کلیدی (کمک به استخراج)
    detected: list[str] = []
    for m in user_messages:
        for service in intent.detect_services(m.content):
            if service not in detected:
                detected.append(service)

    extracted = await ai.extract_lead(_to_dict_list(history), detected)
    if not extracted.get("ready"):
        return

    score = lead_scoring.score_lead(extracted)
    conversation = [
        {"role": m.role, "content": m.content, "at": m.created_at.isoformat() if m.created_at else None}
        for m in history
    ]

    lead = models.Lead(
        session_id=session.id,
        name=extracted.get("name"),
        phone=extracted.get("phone"),
        telegram_contact=extracted.get("telegram_contact"),
        company=extracted.get("company"),
        service=extracted.get("services") or detected or None,
        lead_score=score,
        conversation=conversation,
        status="new",
        source=session.source,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    logger.info("لید جدید ثبت شد: id=%s score=%s service=%s", lead.id, score, lead.service)

    # اعلان به تیم — بدون مسدودکردن پاسخ چت
    if lead_scoring.is_hot(score, settings.notify_score_threshold):
        payload = {
            "name": lead.name,
            "company": lead.company,
            "service": lead.service,
            "lead_score": lead.lead_score,
            "level": lead_scoring.lead_level(score),
            "phone": lead.phone,
            "telegram_contact": lead.telegram_contact,
            "created_at": lead.created_at,
            "source": lead.source,
        }
        asyncio.create_task(notifications.notify_telegram(payload))
        asyncio.create_task(notifications.notify_email(payload))


# ── اندپوینت چت ───────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)) -> ChatResponse:
    settings = get_settings()

    session_id = payload.session_id or str(uuid.uuid4())

    if await _rate_limited(session_id, settings.rate_limit_per_minute):
        raise HTTPException(status_code=429, detail="تعداد پیام‌ها بیش از حد مجاز است. کمی صبر کنید.")

    # ۱) session
    session = await db.get(models.Session, session_id)
    if session is None:
        session = models.Session(
            id=session_id,
            source=payload.source,
            telegram_id=payload.telegram_id,
            telegram_username=payload.telegram_username,
        )
        db.add(session)
        await db.commit()
    else:
        changed = False
        if payload.telegram_id and not session.telegram_id:
            session.telegram_id = payload.telegram_id
            changed = True
        if payload.telegram_username and not session.telegram_username:
            session.telegram_username = payload.telegram_username
            changed = True
        if changed:
            await db.commit()

    # ۲) تاریخچه قبلی + ثبت پیام جدید
    history = await _load_history(db, session_id)
    db.add(models.Message(session_id=session_id, role="user", content=payload.message))
    await db.commit()

    # ۳) گفتگو با مدل — System Prompt + دانش فَر (RAG) + تاریخچه
    llm_messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if settings.knowledge_enabled:
        context = rag.build_context(payload.message)
        if context:
            llm_messages.append({"role": "system", "content": context})
    tail = history[-(settings.max_history_messages * 2):]
    llm_messages.extend({"role": m.role, "content": m.content} for m in tail)
    llm_messages.append({"role": "user", "content": payload.message})

    try:
        answer = await ai.chat_completion(llm_messages)
    except Exception as exc:
        logger.error("خطای مدل: %s", exc)
        raise HTTPException(status_code=502, detail="مغز Far AI در دسترس نیست. لطفاً بعداً تلاش کنید.") from exc

    # ۴) ثبت پاسخ
    db.add(models.Message(session_id=session_id, role="assistant", content=answer))
    await db.commit()

    # ۵) بررسی نهایی‌سازی لید
    history = await _load_history(db, session_id)
    await _maybe_finalize_lead(db, session, history)

    return ChatResponse(session_id=session_id, answer=answer)
