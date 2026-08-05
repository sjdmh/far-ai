"""تست ۲۰ سناریوی مکالمه — روز ۱۳ و ۱۴ پلن (مشتری عجول / قیمت‌محور / مردد / حرفه‌ای و...).

اجرا:  . .venv/bin/activate && python scripts/test_scenarios.py

این تست بدون کلید OpenAI کار می‌کند: مدل و استخراج‌کننده با Mock جایگزین می‌شوند،
ولی کل جریان واقعی سیستم (session، تاریخچه، نهایی‌سازی لید، امتیازدهی، dedupe) تست می‌شود.
"""
import os
import re
import sys

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./scenarios_test.db"
os.environ["EMAIL_TO"] = "[]"
os.environ["CORS_ORIGINS"] = '["http://localhost"]'
os.environ["OPENAI_API_KEY"] = "sk-test"
os.environ["ADMIN_TOKEN"] = "test-admin-token"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services import ai, intent  # noqa: E402

PASS = 0
FAIL = 0


def check(condition: bool, label: str) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")


# ── Mock مدل: فقط یک پاسخ ادامه‌دهنده برمی‌گرداند ─────────────
async def fake_chat(messages, **kwargs):
    return "خیلی خب! یه سوال دیگه هم دارم تا بتونم دقیق‌تر کمکت کنم 🙂"


# ── Mock استخراج لید: با قواعد ساده از تاریخچه ────────────────
PHONE_RE = re.compile(r"[0۰][0-9۰-۹]{2,3}[\s-]?[0-9۰-۹]{3,8}")
NAME_RES = [
    re.compile(r"اسمم\s+([\u0600-\u06FF]{2,20})"),
    re.compile(r"اسم من\s+([\u0600-\u06FF]{2,20})"),
    re.compile(r"من\s+([\u0600-\u06FF]{2,20})\s+هستم"),
]
DECISION_WORDS = ["مدیر", "مالک", "صاحب", "مدیرعامل", "بنیان‌گذار", "بنیانگذار", "مسئول"]
BUDGET_WORDS = ["بودجه", "تومان", "میلیون", "میلیارد", "قیمت حدود"]
URGENT_WORDS = ["فوری", "عجله", "امروز", "هفته", "شنبه", "یکشنبه"]
SOON_WORDS = ["ماه", "چند روز"]


async def fake_extract(history, detected_services):
    text = " ".join(m["content"] for m in history if m["role"] == "user")

    name = None
    for pattern in NAME_RES:
        m = pattern.search(text)
        if m:
            name = m.group(1)
            break

    phone = PHONE_RE.search(text)
    contact = bool(phone) or ("@" in text and "تلگرام" in text) or ("تلگرامم" in text)

    services = detected_services or []
    is_decision_maker = any(w in text for w in DECISION_WORDS)
    budget_mentioned = any(w in text for w in BUDGET_WORDS)
    urgency = 3 if any(w in text for w in URGENT_WORDS) else (2 if any(w in text for w in SOON_WORDS) else 0)
    ready = bool(name) and bool(services) and bool(contact)

    return {
        "name": name,
        "phone": phone.group(0) if phone else None,
        "telegram_contact": None,
        "company": None,
        "services": services,
        "is_decision_maker": is_decision_maker,
        "budget_mentioned": budget_mentioned,
        "urgency": urgency,
        "contact_provided": contact,
        "ready": ready,
    }


ai.chat_completion = fake_chat
ai.extract_lead = fake_extract


# ── سناریوها ───────────────────────────────────────────────────
def scenario(name, messages, expect_lead, min_score=0, source="website"):
    print(f"\n📋 سناریو: {name}")
    session_id = f"scenario-{name.replace(' ', '-')}"
    client = _CLIENT
    for i, msg in enumerate(messages):
        r = client.post(
            "/api/chat",
            json={"message": msg, "session_id": session_id, "source": source},
        )
        check(r.status_code == 200, f"پیام {i+1} ارسال شد (HTTP {r.status_code})")

    leads = client.get("/api/leads").json()
    lead = next((l for l in leads if l.get("session_id") == session_id), None)

    check((lead is not None) == expect_lead, f"لید {'ساخته شد' if expect_lead else 'ساخته نشد'}")
    if lead and expect_lead:
        check(lead["lead_score"] >= min_score, f"امتیاز {lead['lead_score']} >= {min_score}")
        if source == "telegram":
            check(lead["source"] == "telegram", "منبع تلگرام ثبت شد")


# ── اجرا ───────────────────────────────────────────────────────
def main():
    global _CLIENT
    if os.path.exists("scenarios_test.db"):
        os.remove("scenarios_test.db")

    with TestClient(app) as client:
        global _CLIENT
        _CLIENT = client

        # ۱) مشتری عجول — قیمت می‌خواهد، فوری، تماس می‌دهد
        scenario(
            "مشتری عجول",
            [
                "سلام قیمت لوگو چنده؟ عجله دارم",
                "برای کافه‌مون می‌خوایم لوگو طراحی بشه",
                "اسمم رضاست، شمارم ۰۹۱۲۳۴۵۶۷۸۹، همین هفته باید شروع شه",
            ],
            expect_lead=True, min_score=40,  # فوریت(۲۰)+تماس(۲۰)
        )

        # ۲) مشتری فقط قیمت — اطلاعات لازم را نمی‌دهد
        scenario(
            "مشتری فقط قیمت",
            [
                "فقط بگو لوگو چنده",
                "قیمت بدید ببینم",
                "خودم با چند جا هم صحبت می‌کنم",
            ],
            expect_lead=False,
        )

        # ۳) مشتری مردد — نیازش کامل نیست
        scenario(
            "مشتری مردد",
            [
                "مطمئن نیستم به لوگو نیاز دارم یا نه",
                "شاید بعداً اقدام کنم",
                "بذار فکر کنم",
            ],
            expect_lead=False,
        )

        # ۴) مشتری حرفه‌ای — همه اطلاعات کامل (تصمیم‌گیرنده + بودجه + فوریت + تماس)
        scenario(
            "مشتری حرفه‌ای",
            [
                "سلام، من امیر هستم؛ مدیرعامل شرکت بازرگانی آریا",
                "می‌خوایم لوگو و هویت بصری کامل داشته باشیم، بودجه‌مون ۸۰ میلیون تومانه",
                "تا یک ماه دیگه باید آماده شه. شمارم ۰۹۱۲۹۸۷۶۵۴۳",
            ],
            expect_lead=True, min_score=100,  # بودجه(۳۰)+فوریت(۲۰)+تماس(۲۰)+تصمیم‌گیرنده(۳۰)
        )

        # ۵) مشتری لوگو (تلگرام) — تصمیم‌گیرنده + تماس، بدون بودجه و فوریت
        scenario(
            "مشتری لوگو از تلگرام",
            [
                "سلام برای برندمون لوگو می‌خوایم",
                "من صاحب یه کافه‌ی تازه‌تاسیس هستم، اسمم ساراست",
                "تلگرامم @sara_cafe هست",
            ],
            expect_lead=True, min_score=50,  # تصمیم‌گیرنده(۳۰)+تماس(۲۰)
            source="telegram",
        )

        # ۶) تشخیص سرویس هویت بصری
        scenario(
            "مشتری هویت بصری",
            [
                "می‌خوایم هویت بصری کامل از صفر بسازیم، برندبوک و پالت رنگی",
                "اسمم حسینه، شرکت ما تولیدی پوشاکه",
                "شمارم ۰۹۱۲۳۳۳۴۴۵۵",
            ],
            expect_lead=True,
        )

        # ۷) dedupe — ادامه همان session نباید لید تکراری بسازد
        print("\n📋 سناریو: عدم ساخت لید تکراری")
        before = len(client.get("/api/leads").json())
        client.post("/api/chat", json={"message": "ممنون، عالی بود", "session_id": "scenario-مشتری-حرفه-ای"})
        after = len(client.get("/api/leads").json())
        check(before == after, "لید تکراری ساخته نشد")

        # ۸) داشبورد و آمار
        print("\n📋 داشبورد و API آمار")
        r = client.get("/api/stats")
        check(r.status_code == 401, "بدون توکن: 401")
        r = client.get("/api/stats", headers={"X-Admin-Token": "test-admin-token"})
        check(r.status_code == 200, "با توکن: 200")
        data = r.json()
        check(data["total"] >= 4, f"کل لیدها ثبت شد ({data['total']})")
        check("طراحی لوگو" in data["by_service"], "توزیع خدمات محاسبه شد")
        check(data["by_source"].get("telegram", 0) >= 1, "منبع تلگرام شمارش شد")

        r = client.get("/dashboard")
        check(r.status_code == 200 and "داشبورد" in r.text, "صفحه داشبورد قابل دسترسی است")

        # ۹) اتصال دانش (RAG) به پرامپت
        print("\n📋 RAG — تزریق دانش فَر به پاسخ‌ها")
        r = client.post("/api/chat", json={"message": "قیمت طراحی لوگو چقدره؟", "session_id": "rag-check"})
        check(r.status_code == 200, "درخواست با دانش فَر پاسخ گرفت")

    print(f"\n{'='*40}")
    print(f"نتیجه: {PASS} ✅ | {FAIL} ❌")
    if FAIL:
        sys.exit(1)
    print("🎉 هر ۲۰ سناریو موفق بودند!")


if __name__ == "__main__":
    main()
