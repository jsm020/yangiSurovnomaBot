from aiogram import types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from states import SurveyStates
from keyboards import groupmates_keyboard, reasons_keyboard
from config import DJANGO_API_URL, SURVEY_API_URL
from utils import json_count
from api import get_json, post_json, finish_participation
from datetime import datetime, timezone

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

def register_handlers(dp):
    # /start buyrug‘i
    @dp.message(CommandStart())
    async def start_cmd(msg: types.Message, state: FSMContext):
        await msg.answer("HEMIS ID ni yuboring:")
        await state.set_state(SurveyStates.waiting_for_student_id)

    # HEMIS ID qabul qilinadi
    @dp.message(SurveyStates.waiting_for_student_id)
    async def process_student_id(msg: types.Message, state: FSMContext):
        hemis_id = msg.text.strip()
        url1 = f"{SURVEY_API_URL}?student={hemis_id}"
        url2 = f"{SURVEY_API_URL}?telegram_id={msg.from_user.id}"
        status1, data1 = await get_json(url1)

        status2, data2 = await get_json(url2)

        if await json_count(data1) > 0 or await json_count(data2) > 0:
            await msg.answer("❗️ Siz (yoki ushbu HEMIS ID) so‘rovnomani allaqachon to‘ldirgansiz.")
            return

        # Telegram ma'lumotlarini yangilash
        payload = {
            "student_id": hemis_id,
            "full_name": msg.from_user.full_name,
            "telegram_id": msg.from_user.id,
            "username": msg.from_user.username or "",
        }
        status, student_obj = await post_json(f"{DJANGO_API_URL}update-telegram-id/", payload)
        if status != 200:
            await msg.answer("Bunday ID topilmadi yoki ro‘yxatdan o‘tmagansiz.")
            return

        student_db_id = student_obj["id"]
        status, gdata = await get_json(f"{DJANGO_API_URL}groupmates/{hemis_id}/")
        if status != 200 or "groupmates" not in gdata:
            await msg.answer("Guruhdoshlar topilmadi.")
            return

        groupmates = gdata["groupmates"]
        part_payload = {
            "student": student_db_id,
            "telegram_id": msg.from_user.id,
            "finished_at":datetime.now(timezone.utc).isoformat()
,
        }
        status, participation = await post_json(SURVEY_API_URL, part_payload)
        if status != 201:
            await msg.answer("❗️ So‘rovnomani boshlashda xatolik.")
            return

        await state.update_data(
            student_db_id=student_db_id,
            all_groupmates=groupmates,
            work_groupmates=groupmates.copy(),
            good_selected=[],
            good_reasons=[],
            weak_selected=[],
            weak_reasons=[],
            stage="good_groupmates",
            participation_id=participation["id"],
        )
        await state.set_state(SurveyStates.survey)
        await msg.answer("Kimlar barcha nazorat ishlaridan a'lo (5) baho oladi deb o'ylaysiz?",
                         reply_markup=groupmates_keyboard(groupmates, "KEYINGI"))

    @dp.callback_query(F.data.startswith("select_"), SurveyStates.survey)
    async def select_groupmate(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        stage = data["stage"]

        sel_key = "good_selected" if stage == "good_groupmates" else "weak_selected"
        working_key = "work_groupmates"

        selected = data[sel_key]
        working = data[working_key]
        gm_id = int(call.data.split("_", 1)[1])

        if gm_id not in selected:
            selected.append(gm_id)
            working = [g for g in working if g["id"] != gm_id]

        await state.update_data({sel_key: selected, working_key: working})
        await call.message.edit_reply_markup(reply_markup=groupmates_keyboard(working, "KEYINGI"))
        await call.answer()

    @dp.callback_query(F.data == "next_stage", SurveyStates.survey)
    async def next_stage(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        stage = data["stage"]

        if stage == "good_groupmates":
            await state.update_data(stage="good_reasons")
            await call.message.edit_reply_markup()
            await call.message.answer(
                "Nega aynan shu talabalar yuqori natijalarga erishishi mumkin deb o‘ylaysiz?",
                reply_markup=reasons_keyboard(GOOD_REASONS, [])
            )

        elif stage == "weak_groupmates":
            await state.update_data(stage="weak_reasons")
            await call.message.edit_reply_markup()
            await call.message.answer(
                "Nega aynan shu talabalar topshira olmaydi deb o‘ylaysiz?",
                reply_markup=reasons_keyboard(WEAK_REASONS, [])
            )
        await call.answer()

    @dp.callback_query(F.data.startswith("reason_"), SurveyStates.survey)
    async def select_reason(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        stage = data["stage"]

        sel_key = "good_reasons" if stage == "good_reasons" else "weak_reasons"
        selected = data[sel_key]
        key = call.data.split("_", 1)[1]

        if key not in selected:
            selected.append(key)

        await state.update_data({sel_key: selected})
        reasons = GOOD_REASONS if stage == "good_reasons" else WEAK_REASONS
        await call.message.edit_reply_markup(reply_markup=reasons_keyboard(reasons, selected))
        await call.answer()

    @dp.callback_query(F.data == "next_reasons", SurveyStates.survey)
    async def finish_stage(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        stage = data["stage"]

        if stage == "good_reasons":
            # Keyingi bosqichga o‘tish: salbiylar
            all_ids = {g["id"] for g in data["all_groupmates"]}
            good_ids = set(data["good_selected"])
            remaining = [g for g in data["all_groupmates"] if g["id"] not in good_ids]

            await state.update_data(
                work_groupmates=remaining,
                weak_selected=[],
                stage="weak_groupmates"
            )
            await call.message.edit_reply_markup()
            await call.message.answer(
                "Kimlar nazorat ishlarini muvaffaqiyatli topshira olmaydi deb hisoblaysiz?",
                reply_markup=groupmates_keyboard(remaining, "KEYINGI")
            )

        elif stage == "weak_reasons":
            await finish_participation(data["participation_id"])
            await call.message.edit_reply_markup()
            await call.message.answer("✅ So‘rovnoma yakunlandi! Rahmat.")
            await state.clear()

        await call.answer()
