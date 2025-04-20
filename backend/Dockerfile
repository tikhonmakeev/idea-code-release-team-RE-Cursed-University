FROM python:3.11-slim

WORKDIR /app

# Для psycopg2, alembic и компиляции
RUN apt-get update && apt-get install -y gcc libpq-dev && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# entrypoint и миграции
RUN chmod +x /app/entrypoint.sh /app/migrate.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]