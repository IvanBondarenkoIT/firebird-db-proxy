# Dockerfile для Railway deployment

FROM python:3.11-slim

# Метаданные
LABEL maintainer="Senior Developer"
LABEL description="Firebird Database Proxy API"
LABEL version="1.0.0"

# Установка системных зависимостей для компиляции Python пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY ./app ./app

# Создание непривилегированного пользователя
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Порт приложения (Railway может переопределить через $PORT)
EXPOSE 8000

# Переменная окружения для Railway
ENV PORT=8000

# Запуск приложения
# Railway автоматически установит $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2

