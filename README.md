yangiSurovnomaBot
🎓 yangiSurovnomaBot — bu Django asosida ishlab chiqilgan veb-ilova bo‘lib, talabalar bilan ishlashni avtomatlashtirish va Telegram orqali interaktiv so‘rovlar o‘tkazish imkonini beradi. Ilova asinxron ishlashni ta'minlaydi va Docker yordamida konteynerlashtirilgan.

🧰 Texnologiyalar
Backend: Django 4.x, Django REST Framework

Bot: Python Telegram Bot

ASGI Server: Uvicorn

Ma'lumotlar bazasi: PostgreSQL

Konteynerlash: Docker, Docker Compose

Yordamchi vositalar: Gunicorn, dotenv

📁 Loyiha tuzilmasi
bash
Copy
Edit
yangiSurovnomaBot/
├── bot/                  # Telegram bot kodi
├── config/               # Django konfiguratsiyasi (ASGI, sozlamalar)
├── students/             # Talabalar bilan ishlash uchun ilova
├── static/               # Statik fayllar (CSS, JS, rasm)
├── media/                # Yuklangan fayllar (rasmlar, hujjatlar)
├── templates/            # HTML shablonlar
├── Dockerfile            # Docker tasviri uchun fayl
├── docker-compose.yml    # Xizmatlarni boshqarish
├── requirements.txt      # Python kutubxonalari ro‘yxati
└── .env                  # Muhit o‘zgaruvchilari
🚀 Ishga tushirish
1. Muhit o‘zgaruvchilarini sozlash
Loyihaning ildiz papkasida .env faylini yarating va quyidagi o‘zgaruvchilarni belgilang:

env
Copy
Edit
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@db:5432/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
2. Docker yordamida ishga tushirish
bash
Copy
Edit
# Tasvirlarni qurish
docker-compose build

# Xizmatlarni ishga tushirish
docker-compose up
3. Ma'lumotlar bazasini migratsiya qilish
Agar kerak bo‘lsa, quyidagi buyruqlarni bajarib, ma'lumotlar bazasini sozlang:

bash
Copy
Edit
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
4. Superfoydalanuvchi yaratish
Admin panelga kirish uchun superfoydalanuvchi yarating:

bash
Copy
Edit
docker-compose exec web python manage.py createsuperuser
5. Statik fayllarni yig‘ish
bash
Copy
Edit
docker-compose exec web python manage.py collectstatic --noinput
📡 API va Bot
API Endpoint: http://localhost:8000/api/students/

Admin Panel: http://localhost:8000/admin/

Telegram Bot: bot/bot.py faylida joylashgan

🐳 Docker Compose xizmatlari
web: Django ilovasi, Uvicorn orqali ishlaydi

bot: Telegram bot, bot/bot.py faylidan ishga tushadi

🧪 Testlar
Testlarni ishga tushirish uchun quyidagi buyruqni bajaring:

bash
Copy
Edit
docker-compose exec web python manage.py test
📄 Litsenziya
Ushbu loyiha MIT litsenziyasi ostida tarqatiladi.