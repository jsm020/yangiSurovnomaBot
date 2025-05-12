# survey_bot.py  – 4 bosqichli so‘rovnoma
import asyncio
import logging
import os
from typing import List

import aiohttp
from aiogram import Bot, Dispatcher, F, types                       # type: ignore
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

# ───────────────────────────── FSM ─────────────────────────────
class SurveyStates(StatesGroup):
    waiting_for_student_id = State()
    survey = State()                      # barcha oraliq bosqichlar

# ───────────── Reason ro‘yxatlari ─────────────
GOOD_REASONS = [
    ("responsibility",  "Javobgarlik hissi kuchli"),
    ("hardwork",        "Tinimsiz mehnat qiladi"),
    ("attentive",       "Darslarni diqqat bilan tinglaydi"),
    ("efficient_time",  "Vaqtidan samarali foydalanadi"),
    ("extra_sources",   "Qo‘shimcha manbalardan bilim oladi"),
    ("good_relation",   "O‘qituvchilar bilan yaxshi munosabatga ega"),
    ("active_events",   "Tadbirlarda faol qatnashadi"),
]

WEAK_REASONS = [
    ("difficulty",        "Dars materialini tushunishda qiyinchilikka duch keladi"),
    ("unprepared",        "Imtihonlarga yaxshi tayyorlanmaydi"),
    ("poor_time",         "Vaqtini samarali boshqara olmaydi"),
    ("motivation",        "Motivatsiya yetishmaydi"),
    ("confidence",        "O‘ziga bo‘lgan ishonch yetarli emas"),
    ("teacher_relation",  "O‘qituvchining talabaga bo‘lgan shaxsiy munosabati ta’sir qiladi"),
    ("subjective_factors","Tanish‑bilishchilik yoki boshqa subyektiv omillar ta’sir qiladi"),
]

# ─────────────────── /start ───────────────────
@dp.message(CommandStart())
async def start_cmd(msg: types.Message, state: FSMContext):
    await msg.answer("HEMIS ID ni yuboring:")
    await state.set_state(SurveyStates.waiting_for_student_id)

# ───── HEMIS ID → student_db_id va groupmates ─────
@dp.message(SurveyStates.waiting_for_student_id)
async def process_student_id(msg: types.Message, state: FSMContext):
    hemis_id = msg.text.strip()

    async with aiohttp.ClientSession() as s:
        # 1) Telegram maʼlumotlarini yangilash
        payload = {
            "student_id": hemis_id,
            "full_name": msg.from_user.full_name,
            "telegram_id": msg.from_user.id,
            "username": msg.from_user.username or "",
        }
        async with s.post(f"{DJANGO_API_URL}update-telegram-id/", json=payload) as r:
            if r.status != 200:
                await msg.answer("Bunday ID topilmadi yoki ro‘yxatdan o‘tmagansiz.")
                return
            student_obj = await r.json()
            student_db_id = student_obj["id"]

        # 2) Guruhdoshlar
        async with s.get(f"{DJANGO_API_URL}groupmates/{hemis_id}/") as r:
            if r.status != 200:
                await msg.answer("Guruhdoshlar topilmadi.")
                return
            groupmates = (await r.json())["groupmates"]

    await state.update_data(
        student_db_id=student_db_id,
        all_groupmates=groupmates,             # o‘zgarmas nusxa
        work_groupmates=groupmates.copy(),     # har bosqichda kamayib boradi
        good_selected=[],
        good_reasons=[],
        weak_selected=[],
        weak_reasons=[],
        stage="good_groupmates",
    )
    await state.set_state(SurveyStates.survey)
    await send_groupmates_keyboard(
        msg,
        groupmates,
        "Kimlar barcha nazorat ishlaridan a'lo (5) baho oladi deb o'ylaysiz?",
    )

# ────────── Guruhdosh tanlash klaviasi ──────────
async def send_groupmates_keyboard(message: types.Message,
                                   mates: List[dict],
                                   question: str):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=g["full_name"],
                                  callback_data=f"select_{g['id']}")]
            for g in mates
        ] + [[InlineKeyboardButton(text="KEYINGI", callback_data="next_stage")]]
    )
    await message.answer(question, reply_markup=kb)

# ────────── «Sabab» klaviasi ──────────
def reasons_keyboard(choices, chosen: List[str]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"reason_{key}")]
            for key, label in choices if key not in chosen
        ] + [[InlineKeyboardButton(text="KEYINGI", callback_data="next_reasons")]]
    )

# ────────── Tanlov callback’i (ikkala bosqich) ──────────
@dp.callback_query(F.data.startswith("select_"), SurveyStates.survey)
async def select_groupmate(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    stage = data["stage"]
    if stage not in ("good_groupmates", "weak_groupmates"):
        return

    working = data["work_groupmates"]
    sel_key = "good_selected" if stage == "good_groupmates" else "weak_selected"
    selected = data[sel_key]

    gm_id = int(call.data.split("_", 1)[1])
    if gm_id not in selected:
        selected.append(gm_id)

    working = [g for g in working if g["id"] != gm_id]
    await state.update_data(work_groupmates=working, **{sel_key: selected})

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=g["full_name"],
                                  callback_data=f"select_{g['id']}")]
            for g in working
        ] + [[InlineKeyboardButton(text="KEYINGI", callback_data="next_stage")]]
    )
    await call.message.edit_reply_markup(reply_markup=kb)
    await call.answer()

# ────────── "KEYINGI" callback’i (bosqich almashadi) ──────────
@dp.callback_query(F.data == "next_stage", SurveyStates.survey)
async def next_stage(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    stage = data["stage"]

    # ── 1‑bosqich → 2‑bosqich (good_reasons)
    if stage == "good_groupmates":
        await call.message.edit_reply_markup(reply_markup=None)
        await post_excellent_candidates(data)       # serverga yuborildi
        await state.update_data(stage="good_reasons")
        await call.message.answer(
            "Nega aynan shu talabalar yuqori natijalarga erishishi mumkin deb o‘ylaysiz? "
            "(Bir nechta variantni tanlashingiz mumkin)",
            reply_markup=reasons_keyboard(GOOD_REASONS, []),
        )

    # ── 3‑bosqich → 4‑bosqich (weak_reasons)
    elif stage == "weak_groupmates":
        await call.message.edit_reply_markup(reply_markup=None)
        await post_weak_candidates(data)
        await state.update_data(stage="weak_reasons")
        await call.message.answer(
            "Nega aynan shu talabalar topshira olmaydi deb o‘ylaysiz? "
            "(Bir nechta variantni tanlashingiz mumkin)",
            reply_markup=reasons_keyboard(WEAK_REASONS, []),
        )

    await call.answer()

# ────────── Sabab tanlash (ikkala bosqich) ──────────
@dp.callback_query(F.data.startswith("reason_"), SurveyStates.survey)
async def select_reason(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    stage = data["stage"]
    if stage not in ("good_reasons", "weak_reasons"):
        return

    key = call.data.split("_", 1)[1]
    sel_key = "good_reasons" if stage == "good_reasons" else "weak_reasons"
    selected = data[sel_key]
    if key not in selected:
        selected.append(key)

    choices = GOOD_REASONS if stage == "good_reasons" else WEAK_REASONS
    kb = reasons_keyboard(choices, selected)
    await state.update_data(**{sel_key: selected})
    await call.message.edit_reply_markup(reply_markup=kb)
    await call.answer()

# ────────── "KEYINGI" sabab tugmasi ──────────
@dp.callback_query(F.data == "next_reasons", SurveyStates.survey)
async def next_reasons(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    stage = data["stage"]

    # ── good_reasons → weak_groupmates
    if stage == "good_reasons":
        await call.message.edit_reply_markup(reply_markup=None)
        await post_excellence_reasons(data)
        # guruhdoshlar ro‘yxatini qayta tiklaymiz
        all_mates = data["all_groupmates"]
        await state.update_data(
            work_groupmates=all_mates.copy(),
            stage="weak_groupmates",
        )
        await send_groupmates_keyboard(
            call.message,
            all_mates,
            "Kimlar nazorat ishlarini muvaffaqiyatli topshira olmaydi deb hisoblaysiz?",
        )

    # ── weak_reasons → yakun
    elif stage == "weak_reasons":
        await call.message.edit_reply_markup(reply_markup=None)
        await post_weak_reasons(data)
        await call.message.answer("So‘rovnoma yakunlandi! Rahmat.")
        await state.clear()

    await call.answer()

# ────────────────── BACKEND POST funksiyalari ──────────────────
async def post_excellent_candidates(data: dict):
    payload = {
        "student": data["student_db_id"],
        "selected_groupmates": data["good_selected"],
    }
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{DJANGO_API_URL}excellent-candidates/", json=payload) as r:
            print("[excellent‑candidates] status:", r.status)
            try:
                res = await r.json()
            except aiohttp.ContentTypeError:
                res = await r.text()
            print("[excellent‑candidates] body  :", res)

async def post_excellence_reasons(data: dict):
    # Oxirgi ExcellentCandidates obyektini topish
    sid = data["student_db_id"]
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{DJANGO_API_URL}excellent-candidates/?student={sid}") as r:
            res = await r.json()
            cand_id = (res["results"][-1] if isinstance(res, dict) else res[-1])["id"]
        for reason in data["good_reasons"]:
            await s.post(f"{DJANGO_API_URL}excellence-reasons/",
                         json={"candidate": cand_id, "reason": reason})

# ─── Salbiy variantlar (endpoint nomlarini loyihangizga moslashtiring) ───
async def post_weak_candidates(data: dict):
    payload = {
        "student": data["student_db_id"],
        "selected_groupmates": data["weak_selected"],
    }
    async with aiohttp.ClientSession() as s:
        # TODO: endpoint nomini o‘zgartiring, agar boshqa bo‘lsa
        async with s.post(f"{DJANGO_API_URL}atrisk-candidates/", json=payload) as r:
            print("[failure‑candidates] status:", r.status)
            try:
                res = await r.json()
            except aiohttp.ContentTypeError:
                res = await r.text()
            print("[failure‑candidates] body  :", res)

async def post_weak_reasons(data: dict):
    sid = data["student_db_id"]
    async with aiohttp.ClientSession() as s:
        # TODO: endpoint nomini o‘zgartiring
        async with s.get(f"{DJANGO_API_URL}atrisk-candidates/?student={sid}") as r:
            res = await r.json()
            cand_id = (res["results"][-1] if isinstance(res, dict) else res[-1])["id"]
        for reason in data["weak_reasons"]:
            await s.post(f"{DJANGO_API_URL}atrisk-reasons/",
                         json={"candidate": cand_id, "reason": reason})

# ──────────────────── main() ────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
