# Dockerfile
FROM python:3.11-slim

# Ishchi katalog yaratish
WORKDIR /app

# Tizim kutubxonalarini o'rnatish
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Talablar faylini ko'chirish va kutubxonalarni o'rnatish
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip install uvicorn gunicorn

# Loyihani ko'chirish
COPY . .

# Statik fayllarni yig'ish (agar kerak bo'lsa)
RUN python manage.py collectstatic --noinput || true

# Port ochish
EXPOSE 8000

# Uvicorn orqali Django'ni ishga tushirish
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
