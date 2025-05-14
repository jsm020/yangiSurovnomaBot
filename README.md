# yangiSurovnomaBot

🗳️ Django + Telegram asosida ishlovchi so‘rovnoma va auksion bot

---

## 📌 Loyiha haqida

**yangiSurovnomaBot** — bu Django backend va Telegram bot asosida ishlab chiqilgan tizim bo‘lib, foydalanuvchilar o‘rtasida interaktiv auksion yoki so‘rovlar o‘tkazishga mo‘ljallangan. Har bir mahsulot Telegram kanalida post qilinadi, foydalanuvchilar bot orqali ishtirok etadi, narxlar real vaqtda yangilanadi va g‘olib avtomatik aniqlanadi.

---

## ⚙️ Texnologiyalar

- **Django 4.x** — backend framework
- **PostgreSQL** — ma'lumotlar bazasi
- **Telegram Bot API** — foydalanuvchi interfeysi
- **Docker / Docker Compose** — deploy va izolyatsiya
- **ASGI (Uvicorn)** — asinxron ishlash uchun
- **Gunicorn** — ishlab chiqarish muhitida server

---

## 📁 Loyihaning tuzilmasi

```
yangiSurovnomaBot/
├── bot/                  # Telegram bot kodi
├── config/               # Django konfiguratsiyasi
├── students/             # Talabalar (foydalanuvchilar) ilovasi
├── static/               # CSS, JS, rasm fayllari
├── media/                # Yuklangan fayllar (rasm, video)
├── Dockerfile            # Docker tasvir konfiguratsiyasi
├── docker-compose.yml    # Xizmatlarni boshqarish
├── requirements.txt      # Python kutubxonalari ro‘yxati
└── .env                  # Muhit sozlamalari
```

---

## 🚀 Ishga tushirish

### 1. `.env` fayl yaratish

Ildiz papkada `.env` fayl yarating:

```env
DEBUG=True
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/dbname
```

### 2. Docker yordamida ishga tushiring

```bash
docker-compose build
docker-compose up
```

### 3. Ma'lumotlar bazasini sozlang

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 4. Statik fayllarni yig‘ing

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

---

## 📡 URL’lar

- Admin panel: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- API: [http://localhost:8000/api/students/](http://localhost:8000/api/students/)
- Bot kodi: `bot/bot.py` faylida

---

## 🤖 Bot funksiyalari

- Telegram kanalga auksion mahsulotini post qilish
- Har bir post tagida botga olib boruvchi referral (deep link)
- Ishtirokchilar narx taklif qilishlari mumkin
- Har bir yangilangan narx barcha ishtirokchilarga yuboriladi
- Har bir bid uchun taymer (masalan, 5 daqiqa) ishlaydi
- Vaqt tugasa, g‘olib avtomatik aniqlanadi

---

## 🧪 Test

```bash
docker-compose exec web python manage.py test
```

---

## 📜 Litsenziya

Ushbu loyiha MIT litsenziyasi asosida tarqatiladi. Istalgan tarzda foydalanish va o‘zgartirish mumkin.

---

👨‍💻 **Muallif**: [@jsm020](https://github.com/jsm020)  
📅 **Yaratilgan sana**: 2025-yil