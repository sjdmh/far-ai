# ── Far AI — نمونه فایل تنظیمات (یک کپی به نام .env بسازید) ──
# کپی کنید:  cp .env.example .env

# ---------- عمومی ----------
ENVIRONMENT=development

# ---------- هوش مصنوعی ----------
# تامین‌کننده: melious (پیشنهادی) | gemini (رایگان) | openai (پولی)
AI_PROVIDER=melious
# ── Melious (OpenAI-compatible، مدل‌های اروپایی) ──
MELIOUS_API_KEY=
MELIOUS_MODEL=deepseek-v4-flash
MELIOUS_BASE_URL=https://api.melious.ai/v1
# ── گزینه رایگان Gemini ──
# GEMINI_API_KEY=
# GEMINI_MODEL=gemini-3.1-flash-lite
# حداکثر طول پاسخ (توکن)
MAX_TOKENS=700
TEMPERATURE=0.5

# ---------- دیتابیس ----------
POSTGRES_USER=far
POSTGRES_PASSWORD=تغییرش-بده-یک-رمز-قوی
POSTGRES_DB=far_ai
# در اجرای لوکال (بدون داکر) از این استفاده کنید:
# DATABASE_URL=postgresql+asyncpg://far:رمز@localhost:5432/far_ai

# ---------- تلگرام ----------
# توکن بات اصلی Far (از BotFather) — هم برای پاسخ به مشتری و هم اعلان تیم
TELEGRAM_BOT_TOKEN=
# آیدی چت/کانال خصوصی تیم (می‌تواند عدد منفی برای گروه باشد)
TELEGRAM_TEAM_CHAT_ID=

# ---------- ایمیل ----------
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=Far AI <no-reply@far.agency>
# فرمت JSON:  ["team@far.agency","boss@far.agency"]
EMAIL_TO=[]

# ---------- دانش (RAG) ----------
KNOWLEDGE_ENABLED=true

# ---------- امنیت ----------
# فرمت JSON:  ["https://far.agency","https://www.far.agency"]
CORS_ORIGINS=["http://localhost","https://far.agency"]
RATE_LIMIT_PER_MINUTE=10
# رمز داشبورد و API آمار (در تولید حتماً بگذارید)
ADMIN_TOKEN=

# ---------- لید ----------
NOTIFY_SCORE_THRESHOLD=60
