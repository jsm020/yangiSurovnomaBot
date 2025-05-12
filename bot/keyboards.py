# ──────────────── keyboards.py ────────────────
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def groupmates_keyboard(mates, label):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=g["full_name"], callback_data=f"select_{g['id']}")]
            for g in mates
        ] + [[InlineKeyboardButton(text=label, callback_data="next_stage")]]
    )

def reasons_keyboard(choices, selected):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"reason_{key}")]
            for key, label in choices if key not in selected
        ] + [[InlineKeyboardButton(text="KEYINGI", callback_data="next_reasons")]]
    )

