# yangiSurovnomaBot

## Loyihaning qisqacha tavsifi
Bu loyiha Django va Django REST Framework asosida qurilgan bo‘lib, talabalar va ularning guruhdoshlari haqidagi so‘rovnomalarni boshqarish uchun API va admin panelni taqdim etadi.

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

## API endpointlar
- `GET/POST /api/students/groupmates/<student_id>/` — Guruhdoshlarni olish
- `GET/POST /api/students/excellent-candidates/` — A'lochi nomzodlar
- `GET/POST /api/students/excellence-reasons/` — A'lochi sabablari
- `GET/POST /api/students/atrisk-candidates/` — Xavf ostidagi nomzodlar
- `GET/POST /api/students/atrisk-reasons/` — Xavf sabablari

## Ishga tushirish
```bash
python manage.py runserver
```

## Talablar
`requirements.txt` faylida ko‘rsatilgan.