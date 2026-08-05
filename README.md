# Far AI — دستیار هوشمند آژانس تبلیغاتی فَر 🤖🦚

> نسخه ۱ (MVP) — «کارمند دیجیتال» آژانس فَر: در سایت و تلگرام جواب می‌دهد، مثل یک بریف‌گیر نیازسنجی می‌کند، لید می‌سازد و به تیم اطلاع می‌دهد.
> هویت برند بر اساس سایت واقعی آژانس: **farr-agency.com** — «فر؛ شکوه تکامل برند شما»

## 🆓 راه‌اندازی رایگان بدون کارت (Render + Neon)

**هزینه صفر، بدون کارت بانکی:** Render (هاست) + Neon (دیتابیس) + Gemini (هوش مصنوعی)

راهنمای کامل قدم‌به‌قدم: **`docs/render-guide.md`**

مسیر سریع:
1. کلید رایگان Gemini از [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. کد را در GitHub آپلود کن
3. دیتابیس رایگان از [neon.tech](https://neon.tech) بساز
4. سرویس Docker از [render.com](https://render.com) بساز (Root Directory: `backend`)
5. کلیدها را در Environment تنظیم کن → `https://far-ai.onrender.com`

---

## معماری

```
مشتری (سایت وردپرسی / تلگرام)
        │
        ▼
   Far AI API (FastAPI)  ←── مغز و مرکز داده
        │
   ┌────┴────┐
   ▼         ▼
 OpenAI    PostgreSQL
 (شخصیت فَر)  (لیدها و گفتگوها)
        │
        ▼
   اعلان به تیم: تلگرام + ایمیل
```

**اصل مهم:** همه‌چیز با Docker بالا می‌آید؛ یعنی سیستم روی هر VPS/هاست ابری قابل انتقال است
(Google Cloud VM، Hetzner، Contabo و…).

---

## ساختار پروژه

```
far-ai/
├── Far-AI-Specification.md        # سند مشخصات (شخصیت، فلو، امتیازدهی، معماری)
├── README.md                      # این فایل
├── docker-compose.yml             # بالا آوردن کل سیستم با یک دستور
├── .env.example                   # نمونه تنظیمات محیطی
├── docs/
│   └── deployment-guide.md        # راهنمای کامل استقرار روی سرور (VPS / Google Cloud)
├── backend/                       # API اصلی (FastAPI)
│   ├── app/
│   │   ├── main.py                # نقطه ورود (+ داشبورد در /dashboard)
│   │   ├── config.py              # تنظیمات (.env)
│   │   ├── database.py            # اتصال PostgreSQL
│   │   ├── models.py              # جدول‌ها: sessions / messages / customers
│   │   ├── schemas.py             # ورودی/خروجی API
│   │   ├── prompts.py             # ⭐ شخصیت Far AI + پرامپت استخراج لید
│   │   ├── routers/
│   │   │   ├── chat.py            # POST /api/chat (قلب سیستم)
│   │   │   ├── leads.py           # مشاهده لیدها
│   │   │   ├── stats.py           # آمار داشبورد (GET /api/stats)
│   │   │   └── health.py          # /health
│   │   ├── services/
│   │   │   ├── ai.py              # اتصال OpenAI
│   │   │   ├── intent.py          # تشخیص سرویس از متن
│   │   │   ├── lead_scoring.py    # امتیازدهی لید (۰ تا ۱۰۰)
│   │   │   ├── rag.py             # بازیابی دانش فَر (RAG)
│   │   │   └── notifications.py   # اعلان تلگرام تیم + ایمیل
│   │   └── static/index.html      # داشبورد ساده مدیریت لیدها
│   ├── knowledge/                 # 📚 دانش‌نامه فَر (منبع RAG — بر اساس سایت واقعی)
│   │   ├── services.md            # خدمات: لوگو، هویت بصری، عکاسی، تیزر، استاپ موشن، آموزش
│   │   ├── process.md             # فرآیند همکاری + فرم بریف + مشاوره رایگان
│   │   ├── faq.md                 # سوالات پرتکرار (قیمت، زمان، نمونه‌کار...)
│   │   ├── portfolio.md           # نمونه‌کارها (B.I.T، آهورا، شیکاگو کافه...)
│   │   ├── pricing.md             # سیاست قیمت‌گذاری
│   │   └── brand.md               # داستان برند: طاووس و شکوه تکامل
│   └── requirements.txt
├── bot/                           # تلگرام بات (لایه نازک)
│   └── bot.py                     # ارسال پیام به API و برگرداندن پاسخ
├── deploy/
│   ├── nginx.conf                 # Reverse Proxy + Rate Limit
│   └── backup.sh                  # بکاپ روزانه دیتابیس
├── scripts/
│   ├── smoke_test.py              # تست اصلی سیستم
│   └── test_scenarios.py          # تست ۲۰ سناریوی مکالمه
└── wordpress-plugin/
    └── far-ai-chat-widget/        # پلاگین وردپرس: ویجت چت سایت
```

---

## شروع سریع (اجرای لوکال)

### ۱) پیش‌نیازها
- Docker + Docker Compose روی سیستم شما
- یک API Key از OpenAI
- (اختیاری) توکن بات تلگرام از [@BotFather](https://t.me/BotFather)

### ۲) تنظیمات
```bash
cd far-ai
cp .env.example .env
nano .env    # کلیدها را پر کنید
```

> **💡 هوش مصنوعی رایگان:** پروژه به‌صورت پیش‌فرض از **Google Gemini** (رایگان، بدون کارت بانکی)
> استفاده می‌کند. فقط کافی است یک کلید رایگان از `https://aistudio.google.com/apikey` بسازید
> و در `GEMINI_API_KEY` بگذارید. (گزینه OpenAI هم با `AI_PROVIDER=openai` پشتیبانی می‌شود.)

### ۳) بالا آوردن کل سیستم
```bash
docker compose up -d --build
```

### ۴) تست
```bash
# سلامتی سیستم
curl http://localhost/health

# یک پیام چت
curl -X POST http://localhost/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"سلام، می‌خوام یه سایت فروشگاهی داشته باشم","source":"website"}'
```

- مستندات خودکار API: `http://localhost/docs`
- لیست لیدها: `http://localhost/api/leads`

---

## اجرای بدون Docker (برای توسعه)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# یک PostgreSQL لوکال داشته باشید و DATABASE_URL را تنظیم کنید، سپس:
uvicorn app.main:app --reload
```

بات تلگرام جداگانه:
```bash
cd bot
pip install -r requirements.txt
FAR_API_URL=http://localhost:8000 TELEGRAM_BOT_TOKEN=... python bot.py
```

---

## نصب پلاگین وردپرس (چت سایت)

دو راه:
1. **ساده:** فایل `far-ai-chat-widget.zip` را از پیشخوان وردپرس (افزونه‌ها ← افزودن ← بارگذاری افزونه) نصب کنید.
2. **دستی:** پوشه `wordpress-plugin/far-ai-chat-widget` را در `wp-content/plugins` کپی کنید.

سپس از **تنظیمات ← Far AI Widget** آدرس API سرور را وارد کنید (مثلاً `https://api.far.agency`).

> نکته: سرور API باید روی دامنه با HTTPS در دسترس باشد تا مرورگر سایت وردپرسی اجازه دهد (CORS هم باید دامنه سایت را شامل شود).

---

## استقرار روی سرور (VPS / Google Cloud)

### مسیر پیشنهادی
1. **الان:** یک VPS اروپایی (Hetzner/Contabo، حدود ۵ تا ۱۰ دلار) — بدون دردسر تحریم و پرداخت.
2. **بعداً:** انتقال به Google Cloud (Compute Engine) — فقط کافی است همان کانتینرها را روی VM جدید بالا بیاورید.

### قدم‌ها (روی هر VPS با Ubuntu 24.04)
```bash
# نصب داکر
curl -fsSL https://get.docker.com | sh

# کلون پروژه و تنظیم .env
git clone <repo> far-ai && cd far-ai
cp .env.example .env && nano .env

# بالا آوردن
docker compose up -d --build

# دامنه را به IP سرور وصل کنید و در nginx.conf بگذارید
# سپس برای SSL:  certbot --nginx -d api.far.agency
```

### مشخصات VM پیشنهادی
| منبع | مقدار |
|---|---|
| OS | Ubuntu 24.04 LTS |
| CPU | 2 vCPU |
| RAM | 4 GB |
| Disk | 50 GB SSD |

---

## جریان کار داخلی (POST /api/chat)

1. یافتن/ساخت `session` (سایت: UUID در localStorage مرورگر / تلگرام: آیدی چت)
2. ذخیره پیام مشتری در `messages`
3. ارسال تاریخچه + **System Prompt فَر** به مدل
4. ذخیره پاسخ
5. وقتی گفتگو ≥ ۳ پیام کاربر شد: **استخراج لید** (JSON) → **امتیازدهی** → اگر امتیاز ≥ ۶۰: **اعلان تلگرام تیم + ایمیل** 🔥

### امتیازدهی (بخش ۷ سند)
| فاکتور | امتیاز |
|---|---|
| بودجه مشخص اعلام کرده | +۳۰ |
| نیاز فوری / شروع نزدیک | +۲۰ |
| شماره تماس یا تلگرام داده | +۲۰ |
| تصمیم‌گیرنده است | +۳۰ |

### نمونه اعلان تیم
```
🔥 لید جدید فَر

👤 نام: علی رضایی
🏢 شرکت: کلینیک زیبایی رضا
🎯 خدمت: طراحی سایت، سئو
📊 امتیاز: 85٪ — داغ
📱 تماس: 0912xxxxxxx
🕐 زمان: 1405/05/02 - 14:32
```

---

## شخصیت Far AI کجاست؟

در `backend/app/prompts.py` فایل `SYSTEM_PROMPT` است. برای تغییر لحن/قوانین فقط همان فایل را ویرایش کنید؛
نیازی به تغییر هیچ‌جای دیگر نیست.

---

## نکات امنیتی (قبل از Production)
- [ ] `.env` هرگز در گیت — `gitignore` آماده است
- [ ] رمز قوی برای PostgreSQL
- [ ] HTTPS با Let's Encrypt
- [ ] CORS فقط دامنه فَر
- [ ] Backup روزانه دیتابیس (اسکریپت + cron)

---

## وضعیت نسخه ۱

| قابلیت | وضعیت |
|---|---|
| Backend + AI + دیتابیس | ✅ تست‌شده |
| تشخیص سرویس + نیازسنجی + استخراج لید | ✅ تست‌شده (۲۰ سناریو) |
| امتیازدهی + اعلان تیم | ✅ تست‌شده |
| دانش‌نامه فَر + RAG | ✅ تست‌شده |
| داشبورد `/dashboard` | ✅ نوشته‌شده |
| پلاگین وردپرس | ✅ ZIP آماده نصب |
| استقرار روی سرور | ⏳ قدم بعدی — راهنمای کامل در `docs/deployment-guide.md` |

## تست پروژه (لوکال)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install aiosqlite   # فقط برای تست (بدون PostgreSQL)
python ../scripts/smoke_test.py        # تست اصلی
python ../scripts/test_scenarios.py    # تست ۲۰ سناریوی مکالمه
```

## داشبورد
- آدرس: `/dashboard` روی سرور (مثلاً `https://api.far.agency/dashboard`)
- رمز: `ADMIN_TOKEN` از `.env`
- نمایش: لیدهای امروز، لیدهای داغ، توزیع خدمات، آخرین مکالمات (به‌روزرسانی هر ۳۰ ثانیه)

## Roadmap بعد از نسخه ۱
- [x] دانش فَر + RAG ساده (نسخه ۱)
- [x] داشبورد ساده لیدها
- [ ] ارتقای RAG به Embedding + pgvector
- [ ] CRM کامل
- [ ] Proposal Generator
- [ ] چند Agent (فروش/پشتیبانی/محتوا)
- [ ] تحلیل خودکار سایت مشتری

---

ساخته‌شده برای **آژانس فَر** — پروژه داخلی **Far OS** 🚀
