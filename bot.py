import asyncio
from aiogram import Bot, Dispatcher, types, F # type: ignore
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import os

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7912014686:AAF0oVi8Yma9qr4IiuSMEQ2gkCRDJ8wr5BI")
DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://localhost:8000/api/students/")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class SurveyStates(StatesGroup):
    waiting_for_student_id = State()
    select_excellent_groupmates = State()

@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await message.answer("HEMIS ID (talaba ID) ni yuboring:")
    await state.set_state(SurveyStates.waiting_for_student_id)

@dp.message(SurveyStates.waiting_for_student_id)
async def process_student_id(message: types.Message, state: FSMContext):
    student_id = message.text.strip()
    payload = {
        "student_id": student_id,
        "full_name": message.from_user.full_name,
        "telegram_id": message.from_user.id,
        "username": message.from_user.username or ""
    }
    async with aiohttp.ClientSession() as session:
        # Studentni yangilash (telegram_id, username, full_name)
        async with session.post(f"{DJANGO_API_URL}update-telegram-id/", json=payload) as resp:
            if resp.status != 200:
                await message.answer("Bunday ID topilmadi yoki siz ro'yxatdan o'tmagansiz. Iltimos, to'g'ri ID yuboring.")
                return
        # Guruhdoshlarni olish
        async with session.get(f"{DJANGO_API_URL}groupmates/{student_id}/") as resp:
            if resp.status != 200:
                await message.answer("Guruhdoshlar topilmadi.")
                return
            groupmates_data = await resp.json()
    await state.update_data(student_id=student_id, groupmates=groupmates_data["groupmates"])
    await state.set_state(SurveyStates.select_excellent_groupmates)
    await send_groupmates_keyboard(message, groupmates_data["groupmates"])

async def send_groupmates_keyboard(message, groupmates):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{g['full_name']}", callback_data=f"select_{g['student_id']}")]
            for g in groupmates
        ] + [[InlineKeyboardButton(text="KEYINGI", callback_data="next_stage")]]
    )
    await message.answer("Guruhdoshlaringizdan kimlar barcha nazorat ishlaridan a'lo (5) baho olishi mumkin deb o'ylaysiz?", reply_markup=keyboard)


# Inline button orqali kursdosh tanlash
@dp.callback_query(F.data.startswith("select_"), SurveyStates.select_excellent_groupmates)
async def select_groupmate_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    groupmates = data.get("groupmates", [])
    selected = data.get("selected", [])
    student_id = call.data.replace("select_", "")
    if student_id not in selected:
        selected.append(student_id)
    groupmates = [g for g in groupmates if g["student_id"] != student_id]
    await state.update_data(groupmates=groupmates, selected=selected)
    # Inline buttonlarni yangilash (KEYINGI tugmasi doim oxirida qoladi)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{g['full_name']}", callback_data=f"select_{g['student_id']}")]
            for g in groupmates
        ] + [[InlineKeyboardButton(text="KEYINGI", callback_data="next_stage")]]
    )
    await call.message.edit_reply_markup(reply_markup=keyboard)
    await call.answer()

# "KEYINGI" tugmasi bosilganda POST qilish yoki bo'sh yuborish
@dp.callback_query(F.data == "next_stage", SurveyStates.select_excellent_groupmates)
async def next_stage_callback(call: types.CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    await call.message.edit_reply_markup(reply_markup=None)
    await post_excellent_candidates(call, all_data)
    await call.message.answer("Tanlov yakunlandi! (Keyingi bosqich uchun buyruq yoki tugma chiqadi)")
    await call.answer()

async def post_excellent_candidates(call, data):
    """
    Tanlangan guruhdoshlarni ExcellentCandidates API'ga POST qilish (ViewSet router uchun mos)
    """
    student_id = data.get("student_id")
    selected = data.get("selected", [])
    if not student_id:
        return
    async with aiohttp.ClientSession() as session:
        # Student obyektini olish (student_id orqali)
        async with session.get(f"{DJANGO_API_URL}?student_id={student_id}") as resp:
            if resp.status == 200:
                students = await resp.json()
                # ViewSet router uchun natija {'results': [...]} bo'lishi mumkin
                if isinstance(students, dict) and "results" in students:
                    students = students["results"]
                if students and isinstance(students, list):
                    student_db_id = students[0]["id"]
                else:
                    return
            else:
                return
        # Tanlanganlarni bazadagi id larini olish
        groupmate_ids = []
        for sid in selected:
            async with session.get(f"{DJANGO_API_URL}?student_id={sid}") as resp:
                if resp.status == 200:
                    students = await resp.json()
                    if isinstance(students, dict) and "results" in students:
                        students = students["results"]
                    if students and isinstance(students, list):
                        groupmate_ids.append(students[0]["id"])
        # ExcellentCandidates obyektini yaratish
        payload = {"student": student_db_id, "selected_groupmates": groupmate_ids}
        await session.post(f"{DJANGO_API_URL}excellent-candidates/", json=payload)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
