FROM python:3.11-slim

WORKDIR /rag

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# создаём папку для faiss, если не будет создана автоматически
RUN mkdir -p /rag/faiss_indices

CMD ["python", "rag-service.py"]
