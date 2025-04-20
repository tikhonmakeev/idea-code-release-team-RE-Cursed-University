FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов
COPY . .

# Права на исполнение entrypoint
RUN chmod +x entrypoint.sh

# Переменные окружения
ENV DB_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres

# Запуск через entrypoint
ENTRYPOINT ["./entrypoint.sh"]
