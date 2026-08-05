# 🆓 راهنمای استقرار Far AI روی Render — بدون کارت بانکی، ۱۰۰٪ رایگان

> این مسیر برای کسانی است که کارت بین‌المللی ندارند. همه سرویس‌ها رایگان هستند:
> **Render** (هاست) + **Neon** (دیتابیس) + **Gemini** (هوش مصنوعی)

## معماری نهایی

```
سایت وردپرس (farr-agency.com)
        │  ویجت چت
        ▼
https://far-ai.onrender.com/api/chat   ← Render (Backend FastAPI)
        │
        ├── Gemini (هوش مصنوعی رایگان)
        └── Neon (PostgreSQL رایگان)
```

---

## قدم ۰ — پیش‌نیازها (هر ۳ رایگان)

| چیز | کجا | چرا |
|---|---|---|
| حساب GitHub | github.com — ثبت‌نام با ایمیل | برای آپلود کد و اتصال به Render |
| کلید Gemini | aistudio.google.com/apikey (قبلاً گرفتی ✅) | هوش مصنوعی |
| حساب Render | render.com — با دکمه «Continue with GitHub» ثبت‌نام کن | هاست |

---

## قدم ۱ — آپلود پروژه به GitHub

1. وارد **github.com** شو → دکمه **+** (بالا سمت راست) → **New repository**
2. اسم بذار: `far-ai` — حالت **Public** — **Create repository**
3. بعد از ساخت، روی لینک **«uploading an existing file»** کلیک کن
4. **پوشه `far-ai`** رو (از داخل فایل پروژه که دانلود کردی) بکش و توی صفحه رها کن — گیت‌هاب خودش همه فایل‌ها و پوشه‌ها رو آپلود می‌کنه
5. پایین صفحه → **Commit changes**

> ⚠️ فقط یک پوشه `far-ai` باید آپلود بشه (نه چند تا). اگه گیت‌هاب گفت فایل تکراری هست، اشکال نداره — فقط جای درستش بذار.

---

## قدم ۲ — ساخت دیتابیس رایگان با Neon

1. برو به **neon.tech** → **Sign up** (با گوگل یا گیت‌هاب — رایگان، بدون کارت)
2. بعد از ورود، یک پروژه می‌سازه. از منوی **Connection Details**، آدرس **`connection string`** رو کپی کن — چیزی شبیه این:

```
postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
```

3. **اینجا تغییر کوچک بده:** اولش بنویس `postgresql+asyncpg://` به‌جای `postgresql://` (فقط همین). یعنی بشه:

```
postgresql+asyncpg://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
```

این آدرس رو نگه دار — در قدم ۴ لازم می‌شه.

---

## قدم ۳ — ساخت سرویس روی Render

1. برو به **render.com** → **Dashboard** → **New +** → **Web Service**
2. **Connect a repository** → `far-ai` رو انتخاب کن
3. این مقادیر رو بذار:

| فیلد | مقدار |
|---|---|
| Name | `far-ai` |
| Runtime | `Docker` |
| Root Directory | `backend` |
| Instance Type | **Free** |

4. دکمه **Create Web Service** → صبر کن تا بسازه (بار اول چند دقیقه طول می‌کشه)

---

## قدم ۴ — تنظیم کلیدها (Environment Variables)

از منوی سرویس → **Environment** → **Add Environment Variable**، این‌ها رو اضافه کن:

| کلید | مقدار |
|---|---|
| `GEMINI_API_KEY` | کلید Gemini خودت (`AQ.Ab8...`) |
| `DATABASE_URL` | آدرس Neon که در قدم ۲ درست کردی |
| `CORS_ORIGINS` | `["https://farr-agency.com","https://www.farr-agency.com","http://localhost"]` |
| `ADMIN_TOKEN` | یک رمز دلخواه برای داشبورد (مثلاً `far-secret-1405`) |
| `AI_PROVIDER` | `gemini` |

> 🔁 بعد از هر تغییر این‌ها، دکمه **Save Changes** → سرویس دوباره بالا میاد.

---

## قدم ۵ — تست

1. بعد از Deploy موفق، آدرس سرویس مثل این می‌شه: `https://far-ai.onrender.com`
2. توی مرورگر باز کن:
   - `https://far-ai.onrender.com/health` → باید ببینی `{"status":"ok","database":"ok"}`
   - `https://far-ai.onrender.com/dashboard` → داشبورد لیدها (با `ADMIN_TOKEN`)

---

## قدم ۶ — نصب ویجت روی وردپرس

1. پلاگین `far-ai-chat-widget.zip` رو نصب و فعال کن
2. **تنظیمات ← Far AI Widget**
3. آدرس API رو بذار: `https://far-ai.onrender.com`
4. ذخیره کن — تموم! 🎉

---

## ⚠️ نکات مهم Render (پلن رایگان)

### ۱) خواب رفتن سرویس (Spin Down)
Render رایگان بعد از **۱۵ دقیقه بدون بازدید** سرویس رو می‌خوابونه؛ اولین بازدید بعدش ~۱ دقیقه طول می‌کشه.
**راه‌حل:** یک سرویس رایگان **UptimeRobot** بساز که هر ۱۰ دقیقه به `/health` سر بزنه:
- uptimerobot.com → ثبت‌نام رایگان → **New Monitor**
- Type: HTTPS | URL: `https://far-ai.onrender.com/health` | Interval: 10 دقیقه

### ۲) دیتابیس Neon
Neon رایگان ۵۰۰MB فضا داره — برای لیدهای یک آژانس چند ماه کافیه. اگر سرویس Neon بعد از مدتی بی‌استفاده «خواب» رفت، با اولین درخواست خودکار بیدار می‌شه.

### ۳) بات تلگرام (اختیاری — فاز بعدی)
پلن رایگان Render اجازه دو سرویس ۲۴ ساعته نمی‌ده. بات تلگرام رو می‌تونید:
- اول MVP روی سایت راه بیفتد و بعداً بات اضافه شود، یا
- روی یک کامپیوتر همیشه‌روشن (مثلاً سیستم خودتان) با `python bot/bot.py` اجرا شود

### ۴) خطای CORS اگه دیدی
مطمئن شو `CORS_ORIGINS` دقیقاً با دامنه سایتت (`farr-agency.com`) هماهنگه — بدون `https://` اشتباهه.

---

## جمع‌بندی هزینه

| سرویس | هزینه |
|---|---|
| Render (هاست) | ۰ تومان 🆓 |
| Neon (دیتابیس) | ۰ تومان 🆓 |
| Gemini (هوش مصنوعی) | ۰ تومان 🆓 |
| GitHub | ۰ تومان 🆓 |
| **جمع** | **۰ تومان — برای همیشه** 🎉 |
