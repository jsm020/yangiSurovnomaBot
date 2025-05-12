# ──────────────── states.py ────────────────
from aiogram.fsm.state import State, StatesGroup

class SurveyStates(StatesGroup):
    waiting_for_student_id = State()
    survey = State()
