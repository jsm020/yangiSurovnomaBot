# ──────────────── main.py ────────────────
import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import API_TOKEN
from handlers import register_handlers

# Bot va Dispatcher yaratish
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Handlerlarni ro‘yxatdan o‘tkazish
register_handlers(dp)

# Botni ishga tushirish
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
