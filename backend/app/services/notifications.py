"""اعلان به تیم: تلگرام + ایمیل — منطبق با بخش ۸ سند.

هر دو تابع بی‌ضرر (no-op) هستند اگر تنظیمات مربوطه پر نشده باشد،
بنابراین در محیط توسعه بدون خطا کار می‌کنند.
"""
import asyncio
import logging

import httpx

from ..config import get_settings

logger = logging.getLogger("far_ai.notifications")

TEAM_MESSAGE_TEMPLATE = """🔥 لید جدید فَر

👤 نام: {name}
🏢 شرکت: {company}
🎯 خدمت: {service}
📊 امتیاز: {score}٪ — {level}
📱 تماس: {contact}
🕐 زمان: {created_at}
🛰 منبع: {source}
"""


def _format_service(service: list | None) -> str:
    if not service:
        return "نامشخص"
    return "، ".join(service)


def _build_payload(lead: dict) -> dict:
    return {
        "name": lead.get("name") or "نامشخص",
        "company": lead.get("company") or "—",
        "service": _format_service(lead.get("service")),
        "score": lead.get("lead_score", 0),
        "level": lead.get("level", ""),
        "contact": lead.get("phone") or lead.get("telegram_contact") or "—",
        "created_at": str(lead.get("created_at", "")),
        "source": lead.get("source", "website"),
    }


async def notify_telegram(lead: dict) -> bool:
    """ارسال پیام لید به کانال/چت تیم با Bot API (مستقل از بات aiogram)."""
    settings = get_settings()
    if not (settings.telegram_bot_token and settings.telegram_team_chat_id):
        logger.info("اعلان تلگرام غیرفعال است (تنظیمات تیم کامل نیست).")
        return False

    payload = _build_payload(lead)
    text = TEAM_MESSAGE_TEMPLATE.format(**payload)
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                url,
                json={"chat_id": settings.telegram_team_chat_id, "text": text},
            )
        return resp.status_code == 200
    except Exception as exc:  # pragma: no cover
        logger.warning("ارسال اعلان تلگرام ناموفق: %s", exc)
        return False


async def notify_email(lead: dict) -> bool:
    """ارسال ایمیل لید به تیم (SMPT با TLS). در thread اجرا می‌شود تا async را نبندد."""
    settings = get_settings()
    if not settings.email_to or not settings.smtp_host or not settings.smtp_user:
        logger.info("اعلان ایمیل غیرفعال است (تنظیمات SMTP کامل نیست).")
        return False

    payload = _build_payload(lead)
    subject = f"لید جدید Far AI — {payload['name']} — {payload['service']}"
    body = "\n".join(
        [
            "لید جدید از Far AI",
            "------------------",
            f"نام: {payload['name']}",
            f"شرکت: {payload['company']}",
            f"خدمت: {payload['service']}",
            f"امتیاز: {payload['score']}٪ — {payload['level']}",
            f"تماس: {payload['contact']}",
            f"زمان: {payload['created_at']}",
            f"منبع: {payload['source']}",
        ]
    )

    try:
        await asyncio.to_thread(_send_smtp, subject, body, settings)
        return True
    except Exception as exc:  # pragma: no cover
        logger.warning("ارسال ایمیل ناموفق: %s", exc)
        return False


def _send_smtp(subject: str, body: str, settings) -> None:  # pragma: no cover
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = settings.email_from
    message["To"] = ", ".join(settings.email_to)
    message.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.email_from, settings.email_to, message.as_string())
