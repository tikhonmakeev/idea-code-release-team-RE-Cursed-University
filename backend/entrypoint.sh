#!/bin/sh

# Применение миграций
alembic upgrade head

# Запуск приложения
exec uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4