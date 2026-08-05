"""لایه اتصال به مدل هوش مصنوعی.

دو تامین‌کننده پشتیبانی می‌شود (متغیر AI_PROVIDER در .env):
- gemini : Google Gemini — سطح رایگان دارد، بدون کارت بانکی (پیشنهادی برای پروژه فَر)
- openai : مدل‌های OpenAI — نیاز به کارت/اعتبار دارد

تغییر تامین‌کننده فقط با عوض کردن AI_PROVIDER و کلید مربوطه انجام می‌شود؛
بقیه سیستم هیچ تغییری نمی‌کند.
"""
import asyncio
import json
import logging

from ..config import get_settings
from ..prompts import EXTRACTION_PROMPT

logger = logging.getLogger("far_ai.ai")

try:  # pragma: no cover
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover
    AsyncOpenAI = None

_openai_client = None
_gemini_client = None


# ═══ OpenAI ═══════════════════════════════════════════════════
def _get_openai_client() -> "AsyncOpenAI":
    global _openai_client
    if AsyncOpenAI is None:  # pragma: no cover
        raise RuntimeError("کتابخانه openai نصب نیست. دستور: pip install openai")
    settings = get_settings()
    if not settings.openai_api_key:  # pragma: no cover
        raise RuntimeError("OPENAI_API_KEY در .env تنظیم نشده است.")
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _openai_client


async def _openai_completion(messages: list[dict], *, json_mode: bool = False) -> str:
    settings = get_settings()
    client = _get_openai_client()

    kwargs: dict = {
        "model": settings.openai_model,
        "messages": messages,
        "temperature": settings.temperature,
        "max_tokens": 700,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = await client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


# ═══ Gemini (SDK رسمی google-genai) ══════════════════════════
def _get_gemini_client():
    """کلاینت Gemini را با کلید تنظیم‌شده برمی‌گرداند (lazy)."""
    global _gemini_client
    try:
        from google import genai
    except ImportError:  # pragma: no cover
        raise RuntimeError("کتابخانه google-genai نصب نیست. دستور: pip install google-genai")
    settings = get_settings()
    if not settings.gemini_api_key:  # pragma: no cover
        raise RuntimeError("GEMINI_API_KEY در .env تنظیم نشده است.")
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=settings.gemini_api_key)
    return _gemini_client


def _to_gemini_messages(messages: list[dict]) -> tuple[str, list[dict]]:
    """پرامپت‌های سیستم را جدا و بقیه را به فرمت Gemini تبدیل می‌کند."""
    system = "\n".join(m["content"] for m in messages if m["role"] == "system")
    contents: list[dict] = []
    for m in messages:
        if m["role"] == "system":
            continue
        g_role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": g_role, "parts": [{"text": m["content"]}]})
    return system, contents


async def _gemini_completion(messages: list[dict], *, json_mode: bool = False) -> str:
    from google.genai import types as genai_types

    settings = get_settings()
    client = _get_gemini_client()
    system, contents = _to_gemini_messages(messages)

    config = genai_types.GenerateContentConfig(
        system_instruction=system or None,
        temperature=settings.temperature,
        max_output_tokens=700,
        response_mime_type="application/json" if json_mode else "text/plain",
    )

    # یک بار تلاش مجدد روی خطای ظرفیت (429)
    for attempt in range(2):
        try:
            response = await client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
                config=config,
            )
            return (response.text or "").strip()
        except Exception as exc:  # pragma: no cover
            if attempt == 0 and "429" in str(exc):
                await asyncio.sleep(2)
                continue
            raise


# ═══ انتخاب تامین‌کننده ══════════════════════════════════════
async def chat_completion(messages: list[dict], *, json_mode: bool = False) -> str:
    """یک round-trip با مدل فعال (بر اساس AI_PROVIDER در .env)."""
    settings = get_settings()
    if settings.ai_provider == "gemini":
        return await _gemini_completion(messages, json_mode=json_mode)
    return await _openai_completion(messages, json_mode=json_mode)


async def extract_lead(history: list[dict], detected_services: list[str]) -> dict:
    """از تاریخچه گفتگو اطلاعات لید را به‌صورت JSON ساخت‌یافته برمی‌گرداند."""
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in history)
    user_content = (
        EXTRACTION_PROMPT
        + "\n\nخدماتِ تشخیص‌داده‌شده از متن (می‌تواند خالی باشد): "
        + json.dumps(detected_services, ensure_ascii=False)
        + "\n\nمکالمه:\n"
        + transcript
    )

    try:
        raw = await chat_completion(
            [
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": user_content},
            ],
            json_mode=True,
        )
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}
        return data
    except Exception as exc:  # pragma: no cover - خطای مدل نباید گفتگو را از کار بیندازد
        logger.warning("استخراج لید ناموفق بود: %s", exc)
        return {}
