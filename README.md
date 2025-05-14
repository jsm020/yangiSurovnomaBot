# yangiSurovnomaBot

## Loyihaning qisqacha tavsifi
Bu loyiha Django va Django REST Framework asosida qurilgan bo‘lib, talabalar va ularning guruhdoshlari haqidagi so‘rovnomalarni boshqarish uchun API, admin panel va Telegram botni taqdim etadi. Frontend qismi esa talabalarni filtrlash, baholash va statistikani ko‘rish uchun HTML/CSS/JS yordamida yaratilgan.

## O‘rnatish
1. Virtual muhit yarating va faollashtiring:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Kerakli kutubxonalarni o‘rnating:
   ```bash
   pip install -r requirements.txt
   ```
3. Migratsiyalarni bajaring:
   ```bash
   python manage.py migrate
   ```
4. Superuser yarating (ixtiyoriy, admin panel uchun):
   ```bash
   python manage.py createsuperuser
   ```

## Ishga tushirish
```bash
python manage.py runserver
```

## Telegram botni ishga tushirish
```bash
cd bot
python bot.py
```

## API endpointlar
- `GET/POST /api/students/groupmates/<student_id>/` — Guruhdoshlarni olish
- `GET/POST /api/students/excellent-candidates/` — A'lochi nomzodlar
- `GET/POST /api/students/excellence-reasons/` — A'lochi sabablari
- `GET/POST /api/students/atrisk-candidates/` — Xavf ostidagi nomzodlar
- `GET/POST /api/students/atrisk-reasons/` — Xavf sabablari
- `GET /api/students/list/` — Talabalar ro‘yxati (filtrlash uchun)
- `GET /api/students/good_reasons/` — Yaxshi xususiyatlar ro‘yxati
- `GET /api/students/weak_reasons/` — Kuchsiz tomonlar ro‘yxati
- `GET /api/students/filter-options/` — Filtr variantlari (fakultet, kurs, guruh)
- `POST /api/students/update-telegram-id/` — Telegram ID yangilash

## Frontend
- `templates/report/index.html` — Talabalarni filtrlash, baholash va statistikani ko‘rish uchun sahifa.
- `static/style.css` — Sahifa uchun uslublar.

## Talablar
`requirements.txt` faylida ko‘rsatilgan.

## Muallif
- [Loyihani ishlab chiquvchi haqida ma'lumot kiriting]