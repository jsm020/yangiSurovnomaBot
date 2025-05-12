import asyncio
import logging
import os
from typing import List

import aiohttp
from aiogram import Bot, Dispatcher, F, types     # type: ignore
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN",
                      "7912014686:AAF0oVi8Yma9qr4IiuSMEQ2gkCRDJ8wr5BI")
DJANGO_API_URL = os.getenv("DJANGO_API_URL",
                           "http://localhost:8000/api/students/")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


class SurveyStates(StatesGroup):
    waiting_for_student_id = State()
    select_excellent_groupmates = State()


# ──────────────────────────── /start ────────────────────────────
@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await message.answer("HEMIS ID ni yuboring:")
    await state.set_state(SurveyStates.waiting_for_student_id)


# ──────────────── HEMIS ID → student_db_id va groupmates ───────────────
@dp.message(SurveyStates.waiting_for_student_id)
async def process_student_id(message: types.Message, state: FSMContext):
    hemis_id = message.text.strip()

    async with aiohttp.ClientSession() as session:
        # 1) Telegram ID’ni yangilaymiz va student obyektini qaytib olamiz
        payload = {
            "student_id": hemis_id,
            "full_name": message.from_user.full_name,
            "telegram_id": message.from_user.id,
            "username": message.from_user.username or "",
        }
        async with session.post(f"{DJANGO_API_URL}update-telegram-id/",
                                json=payload) as resp:
            if resp.status != 200:
                await message.answer("Bunday ID topilmadi yoki siz ro'yxatdan o'tmagansiz.")
                return
            student_obj = await resp.json()       # {"id":123, "student_id":"3182...", ...}
            student_db_id = student_obj["id"]     # primary‑key

        # 2) Guruhdoshlarni olamiz
        async with session.get(f"{DJANGO_API_URL}groupmates/{hemis_id}/") as resp:
            if resp.status != 200:
                await message.answer("Guruhdoshlar topilmadi.")
                return
            groupmates_data = await resp.json()   # {"groupmates":[{id, full_name, ...}, ...]}

    await state.update_data(
        student_db_id=student_db_id,         # ← bazadagi id
        groupmates=groupmates_data["groupmates"],
        selected=[],
    )
    await state.set_state(SurveyStates.select_excellent_groupmates)
    await send_groupmates_keyboard(message, groupmates_data["groupmates"])


# ───────────────── Tugmachalar ─────────────────
async def send_groupmates_keyboard(message: types.Message, groupmates: List[dict]):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=g["full_name"],
                                  callback_data=f"select_{g['id']}")]
            for g in groupmates
        ] + [[InlineKeyboardButton(text="KEYINGI", callback_data="next_stage")]]
    )
    await message.answer(
        "Kimlar barcha nazorat ishlari bo‘yicha a'lo oladi deb o'ylaysiz?",
        reply_markup=kb,
    )


# ─────────── Tanlash callback’i ───────────
@dp.callback_query(F.data.startswith("select_"),
                   SurveyStates.select_excellent_groupmates)
async def select_groupmate_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    groupmates = data["groupmates"]
    selected = data["selected"]

    gm_id = int(call.data.split("_", 1)[1])      # primary‑key

    if gm_id not in selected:
        selected.append(gm_id)

    groupmates = [g for g in groupmates if g["id"] != gm_id]
    await state.update_data(groupmates=groupmates, selected=selected)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=g["full_name"],
                                  callback_data=f"select_{g['id']}")]
            for g in groupmates
        ] + [[InlineKeyboardButton(text="KEYINGI", callback_data="next_stage")]]
    )
    await call.message.edit_reply_markup(reply_markup=kb)
    await call.answer()


# ─────────── "KEYINGI" callback’i ───────────
@dp.callback_query(F.data == "next_stage",
                   SurveyStates.select_excellent_groupmates)
async def next_stage_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_reply_markup(reply_markup=None)
    await post_excellent_candidates(data)        # ← student_db_id & selected
    await call.message.answer("Tanlov yakunlandi! Rahmat.")
    await call.answer()


# ──────── Natijani backend’ga yuborish + konsolga chiqarish ────────
async def post_excellent_candidates(data: dict):
    student_db_id: int = data["student_db_id"]       # primary‑key
    selected_ids: List[int] = data["selected"]

    payload = {"student": student_db_id,
               "selected_groupmates": selected_ids}

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{DJANGO_API_URL}excellent-candidates/",
                                json=payload) as resp:
            status = resp.status
            try:
                body = await resp.json()
            except aiohttp.ContentTypeError:
                body = await resp.text()

            # Konsol logi
            print(f"[POST /excellent-candidates/] status = {status}")
            print(f"[POST /excellent-candidates/] body   = {body}")


# ───────────────────────────── main() ─────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
