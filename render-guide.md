"""تلگرام بات Far AI — یک «لایه نازک» که پیام را به مغز (Backend API) می‌سپارد.

معماری: تمام هوش و ذخیره‌سازی در Backend است؛ بات فقط:
  1. پیام مشتری را به POST /api/chat می‌فرستد
  2. پاسخ را به مشتری برمی‌گرداند
session_id = آیدی چت تلگرام، پس گفتگو در هر دو کانال ادامه‌پذیر است.
"""
import logging
import os

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from prompts import TELEGRAM_START_TEXT

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("far_ai.bot")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
FAR_API_URL = os.getenv("FAR_API_URL", "http://localhost:8000")

if not BOT_TOKEN:
    raise SystemExit("TELEGRAM_BOT_TOKEN تنظیم نشده است.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(TELEGRAM_START_TEXT)


@dp.message(F.text)
async def handle_text(message: Message) -> None:
    payload = {
        "message": message.text,
        "session_id": f"tg:{message.chat.id}",
        "source": "telegram",
        "telegram_id": str(message.chat.id),
        "telegram_username": message.from_user.username if message.from_user else None,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{FAR_API_URL}/api/chat", json=payload)
            response.raise_for_status()
            answer = response.json().get("answer", "")
    except Exception as exc:
        logger.error("خطا در ارتباط با Backend: %s", exc)
        answer = "یه لحظه مشکل فنی داریم 🙏 لطفاً چند دقیقه دیگه دوباره تلاش کن."

    # پیام‌های طولانی تلگرام را در چند بخش می‌فرستیم
    if answer:
        for chunk in _chunks(answer, 4000):
            await message.answer(chunk)


def _chunks(text: str, size: int):
    return [text[i : i + size] for i in range(0, len(text), size)]


async def main() -> None:
    logger.info("Far AI Telegram Bot راه‌اندازی شد 🤖")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
