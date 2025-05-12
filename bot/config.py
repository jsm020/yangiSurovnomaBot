
import os

# ──────────────── config.py ────────────────
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN","7912014686:AAF0oVi8Yma9qr4IiuSMEQ2gkCRDJ8wr5BI")
DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://localhost:8000/api/students/")
SURVEY_API_URL = os.getenv("SURVEY_API_URL", "http://localhost:8000/api/students/survey-participations/")

if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment o'zgaruvchisi topilmadi.")