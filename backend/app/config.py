"""مرکزی‌ترین تنظیمات Far AI — همه مقادیر حساس از .env خوانده می‌شوند."""
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── عمومی ──────────────────────────────────────────────
    app_name: str = "Far AI"
    environment: str = "development"

    # ── هوش مصنوعی ─────────────────────────────────────────
    ai_provider: str = "melious"             # gemini (رایگان) | melious (پیشنهادی) | openai
    temperature: float = 0.5                 # دما پایین = پاسخ سریع‌تر و دقیق‌تر
    max_tokens: int = 700                    # پاسخ کوتاه‌تر = سریع‌تر (برای ۲-۴ جمله کافیه)
    max_history_messages: int = 10           # تاریخچه کمتر = پردازش سریع‌تر (آخرین ۱۰ پیام)

    # تامین‌کننده Gemini — رایگان، بدون کارت (کلید از aistudio.google.com)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-flash-lite"  # سریع و موجود — سهمیه رایگان جدا از مدل‌های دیگر

    # تامین‌کننده Melious — OpenAI-compatible، مدل‌های متن‌باز اروپایی
    melious_api_key: str = ""
    melious_model: str = "deepseek-v4-flash"     # سریع و باکیفیت برای فارسی
    melious_base_url: str = "https://api.melious.ai/v1"

    # تامین‌کننده OpenAI — گزینه پولی
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7          # سازگاری با .env قدیمی (در کد استفاده نمی‌شود)

    # ── دیتابیس ────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://far:far@localhost:5432/far_ai"

    @model_validator(mode="after")
    def _normalize_db_url(self):
        """اگر کاربر آدرس دیتابیس را بدون +asyncpg وارد کرد، خودکار اصلاح شود."""
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        return self

    # ── تلگرام (بات + کانال تیم) ───────────────────────────
    telegram_bot_token: str = ""               # توکن بات اصلی Far (برای پاسخ به مشتری)
    telegram_team_chat_id: str = ""            # آیدی چت/کانال خصوصی تیم برای اعلان لید

    # ── ایمیل ──────────────────────────────────────────────
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "Far AI <no-reply@far.agency>"
    email_to: list[str] = []                   # مثال: ["team@far.agency","boss@far.agency"]

    # ── دانش (RAG) ───────────────────────────────────────────
    knowledge_enabled: bool = True             # تزریق دانش فَر به پاسخ‌ها

    # ── امنیت ──────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost", "https://far.agency"]
    rate_limit_per_minute: int = 10            # حداکثر پیام در دقیقه به ازای هر session
    admin_token: str = ""                      # اگر خالی باشد، داشبورد/آمار بدون رمز باز است (فقط توسعه)

    # ── لید ────────────────────────────────────────────────
    notify_score_threshold: int = 60           # حداقل امتیاز برای اعلان فوری به تیم


@lru_cache
def get_settings() -> Settings:
    return Settings()
