"""تست اسمک Far AI — بدون نیاز به کلید OpenAI و PostgreSQL واقعی.

اجرا:  . .venv/bin/activate && python scripts/smoke_test.py
"""
import os
import sys

# ── تنظیمات قبل از import برنامه ──────────────────────────────
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./smoke_test.db"
os.environ["EMAIL_TO"] = "[]"
os.environ["CORS_ORIGINS"] = '["http://localhost"]'
os.environ["OPENAI_API_KEY"] = "sk-test"

import asyncio

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app  # noqa: E402
from app.services import ai  # noqa: E402

# ── شبیه‌سازی مدل (بدون تماس واقعی با OpenAI) ─────────────────
calls = []


async def fake_chat(messages, **kwargs):
    user_last = next(m["content"] for m in reversed(messages) if m["role"] == "user")
    calls.append(user_last)
    return f"پاسخ Far AI به: «{user_last}»"


async def fake_extract(history, detected_services):
    return {
        "name": "علی رضایی",
        "phone": "09121234567",
        "telegram_contact": None,
        "company": "کلینیک زیبایی رضا",
        "services": detected_services or ["طراحی لوگو"],
        "is_decision_maker": True,
        "budget_mentioned": True,
        "urgency": 3,
        "contact_provided": True,
        "ready": True,
    }


ai.chat_completion = fake_chat
ai.extract_lead = fake_extract


def main():
    if os.path.exists("smoke_test.db"):
        os.remove("smoke_test.db")

    with TestClient(app) as client:
        # ۱) سلامت
        r = client.get("/health")
        assert r.status_code == 200, r.text
        assert r.json()["database"] == "ok"
        print("✅ /health ok")

        # ۲) گفتگوی سه‌مرحله‌ای → باید لید ساخته شود
        session_id = None
        for i, msg in enumerate(
            [
                "سلام، می‌خوام برای کلینیکمون لوگو طراحی بشه",
                "کلینیک زیباییه، هویت بصری کامل هم می‌خوایم",
                "من مدیر کلینیکم؛ بودجه‌مون حدود ۵۰ میلیونه و تا دو هفته دیگه باید شروع بشه. شمارم ۰۹۱۲۱۲۳۴۵۶۷",
            ]
        ):
            payload = {"message": msg, "source": "website"}
            if session_id:
                payload["session_id"] = session_id
            r = client.post("/api/chat", json=payload)
            assert r.status_code == 200, (r.status_code, r.text)
            data = r.json()
            session_id = data["session_id"]
            assert data["answer"]
            print(f"✅ پیام {i+1}: پاسخ دریافت شد ({len(data['answer'])} کاراکتر)")

        # ۳) لید ساخته و امتیازدهی شده؟
        r = client.get("/api/leads")
        assert r.status_code == 200
        leads = r.json()
        assert len(leads) == 1, f"expected 1 lead, got {len(leads)}"
        lead = leads[0]
        assert lead["name"] == "علی رضایی"
        assert lead["lead_score"] == 100, lead  # بودجه+فوریت+تماس+تصمیم‌گیرنده
        assert "طراحی لوگو" in (lead["service"] or [])
        print(f"✅ لید ثبت شد: {lead['name']} — امتیاز {lead['lead_score']} — خدمت {lead['service']}")

        # ۴) تکرار لید ساخته نمی‌شود (یک session = یک لید)
        r = client.post("/api/chat", json={"message": "ممنون", "session_id": session_id})
        assert r.status_code == 200
        leads = client.get("/api/leads").json()
        assert len(leads) == 1
        print("✅ لید تکراری ساخته نشد")

        # ۵) Rate Limit
        r = client.get("/health")  # هدر بده
        for _ in range(12):
            r = client.post("/api/chat", json={"message": "تست", "session_id": "rl-test"})
        assert r.status_code == 429, r.status_code
        print("✅ Rate Limit فعال است")

    print("\n🎉 همه تست‌ها موفق بودند — Far AI نسخه ۱ کار می‌کند!")


if __name__ == "__main__":
    main()
