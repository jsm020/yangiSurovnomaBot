# ──────────────── survey_bot.py – 4 bosqichli so‘rovnoma ────────────────
import asyncio
import datetime
import logging
import os
from typing import List

import aiohttp
from aiogram import Bot, Dispatcher, F, types                       # type: ignore
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ──────────────── Konstanta va tokenlar ────────────────
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN",
                      "7912014686:AAF0oVi8Yma9qr4IiuSMEQ2gkCRDJ8wr5BI")
DJANGO_API_URL = os.getenv("DJANGO_API_URL",
                           "http://localhost:8000/api/students/")
# ➕ SurveyParticipation endpointi
SURVEY_API_URL = os.getenv(
    "SURVEY_API_URL",
    "http://localhost:8000/api/students/survey-participations/"
)

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
async def json_count(resp: aiohttp.ClientResponse) -> int:
    """
    DRF ListAPIView bo'lsa {"count": n, ...} keladi.
    Oddiy list bo'lsa len(list) qaytadi.
    404 yoki JSON bo'lmasa → 0.
    """
    if resp.status != 200:
        return 0
    try:
        data = await resp.json()
    except aiohttp.ContentTypeError:
        return 0

    if isinstance(data, dict):
        return data.get("count", 0)
    return len(data)            # list bo'lsa

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
        # 0) allaqachon qatnashgan‑qatnashmaganini tekshirish
        r1 = await s.get(f"{SURVEY_API_URL}?student={hemis_id}")
        r2 = await s.get(f"{SURVEY_API_URL}?telegram_id={msg.from_user.id}")

        count_student  = await json_count(r1)
        count_telegram = await json_count(r2)

        if count_student > 0 or count_telegram > 0:
            await msg.answer("❗️ Siz (yoki ushbu HEMIS ID) so‘rovnomani allaqachon to‘ldirgansiz.")
            return

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

        # 3) Participation yozuvini yaratamiz
        participation_payload = {
            "student": student_db_id,
            "telegram_id": msg.from_user.id,
            "finished_at": datetime.datetime.utcnow().isoformat(),
        }
        async with s.post(SURVEY_API_URL, json=participation_payload) as pr:
            if pr.status != 201:
                err = await pr.json()
                await msg.answer(f"❗️ {err.get('detail', 'So‘rovnomani to‘ldirish mumkin emas.')}")
                return
            participation_id = (await pr.json())["id"]

    # FSM ma'lumotlari
    await state.update_data(
        student_db_id=student_db_id,
        all_groupmates=groupmates,             # o‘zgarmas nusxa
        work_groupmates=groupmates.copy(),     # har bosqichda kamayib boradi
        good_selected=[],
        good_reasons=[],
        weak_selected=[],
        weak_reasons=[],
        stage="good_groupmates",
        participation_id=participation_id,     # ➕
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
    await state.update_data(
        work_groupmates=working,
        **{sel_key: selected.copy()}   # <‑‑ .copy() muhim
    )

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

        # good_selected ID‑larini chiqarib tashlaymiz
        all_mates = data["all_groupmates"]
        good_ids = set(data["good_selected"])
        remaining = [g for g in all_mates if g["id"] not in good_ids]

        await state.update_data(
            work_groupmates=remaining,
            weak_selected=[],
            stage="weak_groupmates",
        )
        await send_groupmates_keyboard(
            call.message,
            remaining,
            "Kimlar nazorat ishlarini muvaffaqiyatli topshira olmaydi deb hisoblaysiz?",
        )

    # ── weak_reasons → yakun
    elif stage == "weak_reasons":
        await call.message.edit_reply_markup(reply_markup=None)
        await post_weak_reasons(data)
        await call.message.answer("So‘rovnoma yakunlandi! Rahmat.")

        # finished_at ni belgilaymiz
        part_id = data.get("participation_id")
        if part_id:
            async with aiohttp.ClientSession() as s:
                await s.patch(
                    f"{SURVEY_API_URL}{part_id}/",
                    json={"finished_at": datetime.datetime.utcnow().isoformat()}
                )

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
