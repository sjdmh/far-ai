"""بازیابی دانش فَر (RAG نسخه اول) — روز ۲۲ تا ۲۵ سند.

روش MVP:
- فایل‌های markdown در پوشه `knowledge/` به بخش‌های (##) تقسیم می‌شوند.
- برای هر پیام کاربر، مرتبط‌ترین بخش‌ها با امتیازدهی واژه‌ای پیدا و به System Prompt اضافه می‌شوند.
- بدون نیاز به کلید API کار می‌کند (تعیین‌پذیر و قابل تست).

نسخه بعدی: جایگزینی با Embedding + دیتابیس برداری (pgvector) برای دقت بالاتر.
"""
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge"

# کلمات کم‌ارزش برای امتیازدهی
_STOPWORDS = {
    "برای", "یک", "می", "که", "را", "با", "به", "از", "تا", "این", "آن",
    "در", "و", "است", "هست", "داریم", "دارید", "کردن", "شود", "می‌شود",
    "بوده", "شما", "من", "ما", "باید", "اگر", "یا", "نه", "بله", "خواهد",
    "همه", "خیلی", "بیشتر", "مثلا", "مثلاً", "مثل", "هم", "را", "ها",
}


def _normalize(text: str) -> str:
    text = text.replace("ي", "ی").replace("ك", "ک")
    text = re.sub(r"[^\w\sآ-ی]", " ", text.lower())
    return re.sub(r"\s+", " ", text)


def _tokens(text: str) -> list[str]:
    return _normalize(text).split()


def _tokenize_for_score(text: str) -> Counter:
    return Counter(t for t in _tokens(text) if t not in _STOPWORDS)


@lru_cache(maxsize=1)
def _load_chunks() -> list[dict]:
    """هر فایل knowledge به بخش‌های عنوان‌دار تقسیم می‌شود."""
    chunks: list[dict] = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        source = path.stem
        content = path.read_text(encoding="utf-8")
        sections = re.split(r"\n(?=##\s)", content)
        for sec in sections:
            lines = [ln.strip() for ln in sec.strip().splitlines() if ln.strip()]
            if not lines:
                continue
            if lines[0].startswith("##"):
                title = lines[0].lstrip("#").strip()
                body = " ".join(lines[1:])
            else:
                title = source
                body = " ".join(lines)
            if len(body) < 25:
                continue
            chunks.append(
                {
                    "title": title,
                    "source": source,
                    "text": body,
                    "tokens": _tokenize_for_score(f"{title} {body}"),
                }
            )
    return chunks


# اگر سوال درباره موضوع خاصی بود، اول فایل مربوطه را مستقیم بردار (مطمئن‌ترین حالت)
_TOPIC_MAP: dict[str, str] = {
    "قیمت": "pricing",
    "هزینه": "pricing",
    "تعرفه": "pricing",
    "تومان": "pricing",
    "چنده": "pricing",
    "قیمتش": "pricing",
    "چقدره": "pricing",
    "زمان": "process",
    "مدت": "process",
    "طول": "process",
    "مهلت": "process",
    "کی تحویل": "process",
    "نمونه": "portfolio",
    "نمونه‌کار": "portfolio",
    "مشتری": "portfolio",
    "بریف": "process",
    "فرم بریف": "process",
    "طاووس": "brand",
    "شکوه": "brand",
    "درباره فر": "brand",
    "هویت برند": "brand",
    "پشتیبانی": "faq",
    "گارانتی": "faq",
    "تضمین": "faq",
    "دوره": "faq",
    "کلاس": "faq",
    "یادگیری": "faq",
    "گرافیک یاد بگیرم": "faq",
}


def _force_chunks(source_name: str) -> list[dict]:
    return [c for c in _load_chunks() if c["source"] == source_name]


def retrieve(query: str, top_k: int = 3, min_score: int = 2) -> list[dict]:
    """مرتبط‌ترین بخش‌های دانش فَر برای یک پیام کاربر."""
    normalized = _normalize(query)

    # ۱) اگر موضوع مشخصی بود، همان فایل را مستقیم بردار
    for keyword, source in _TOPIC_MAP.items():
        if keyword in normalized:
            forced = _force_chunks(source)
            if forced:
                # اول فایل موضوع، بعد بقیه امتیازها
                result = [{k: c[k] for k in ("title", "source", "text")} for c in forced[:top_k]]
                remaining = _score_chunks(query, min_score, exclude_source=source)
                result.extend(remaining[: max(0, top_k - len(result))])
                return result[:top_k]

    # ۲) وگرنه امتیازدهی معمولی
    return _score_chunks(query, min_score)


def _score_chunks(query: str, min_score: int, exclude_source: str | None = None) -> list[dict]:
    query_counter = _tokenize_for_score(query)
    if not query_counter:
        return []

    scored: list[tuple[int, dict]] = []
    for chunk in _load_chunks():
        if exclude_source and chunk["source"] == exclude_source:
            continue
        score = 0
        for word, count in query_counter.items():
            if len(word) < 2:
                continue
            # کلماتی که در عنوان هستند وزن بیشتری دارند
            title_bonus = 3 if word in chunk["title"] else 1
            score += chunk["tokens"].get(word, 0) * count * title_bonus
        if score >= min_score:
            scored.append((score, chunk))

    scored.sort(key=lambda item: -item[0])
    return [{k: c[k] for k in ("title", "source", "text")} for _, c in scored[:3]]


def build_context(query: str) -> str:
    """متن آماده تزریق به System Prompt؛ اگر چیزی نیافت خالی برمی‌گرداند."""
    chunks = retrieve(query)
    if not chunks:
        return ""
    parts = []
    for chunk in chunks:
        head = f"### {chunk['title']} (منبع: {chunk['source']})"
        parts.append(f"{head}\n{chunk['text'][:1500]}")
    return "دانش اختصاصی آژانس فَر (در پاسخ‌ها از این اطلاعات استفاده کن):\n\n" + "\n\n".join(parts)
