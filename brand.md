"""امتیازدهی لید (Lead Scoring) — منطبق با بخش ۷ سند مشخصات."""
from __future__ import annotations

WEIGHTS = {
    "budget_mentioned": 30,   # بودجه مشخص اعلام کرده
    "urgent": 20,             # نیاز فوری / شروع نزدیک
    "contact_provided": 20,   # شماره تماس یا تلگرام داده
    "decision_maker": 30,     # تصمیم‌گیرنده است
}


def score_lead(extracted: dict) -> int:
    """امتیاز ۰ تا ۱۰۰ از روی خروجی استخراج لید."""
    score = 0
    if extracted.get("budget_mentioned") is True:
        score += WEIGHTS["budget_mentioned"]
    if int(extracted.get("urgency") or 0) >= 2:
        score += WEIGHTS["urgent"]
    if extracted.get("contact_provided") is True or bool(
        extracted.get("phone") or extracted.get("telegram_contact")
    ):
        score += WEIGHTS["contact_provided"]
    if extracted.get("is_decision_maker") is True:
        score += WEIGHTS["decision_maker"]
    return min(100, score)


def lead_level(score: int) -> str:
    """🔵 سرد / 🟡 گرم / 🔥 داغ"""
    if score < 40:
        return "سرد"
    if score <= 70:
        return "گرم"
    return "داغ"


def is_hot(score: int, threshold: int) -> bool:
    return score >= threshold
