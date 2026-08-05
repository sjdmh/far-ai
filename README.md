
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
