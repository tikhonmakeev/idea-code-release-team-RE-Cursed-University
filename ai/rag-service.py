from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import uvicorn

app = FastAPI()
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
llm_client = OpenAI(base_url='http://localhost:11434/v1',
                     api_key='ollama')

# Путь к хранилищу индексов (должен совпадать с embedding_service)
INDEX_STORAGE_PATH = "faiss_indices"
os.makedirs(INDEX_STORAGE_PATH, exist_ok=True)

class QueryRequest(BaseModel):
    user_id: str
    query: str
    top_k: int = 3

def load_user_chunks(user_id: str) -> List[str]:
    """Загружает чанки пользователя из JSON файла"""
    chunks_path = os.path.join(INDEX_STORAGE_PATH, f"chunks_{user_id}.json")
    if not os.path.exists(chunks_path):
        raise FileNotFoundError(f"Chunks file not found for user {user_id}")
    
    with open(chunks_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.post("/query/")
async def handle_query(request: QueryRequest):
    try:
        # Загружаем индекс пользователя
        index_path = os.path.join(INDEX_STORAGE_PATH, f"index_{request.user_id}.faiss")
        if not os.path.exists(index_path):
            raise HTTPException(status_code=404, detail=f"Index not found for user {request.user_id}")
        
        index = faiss.read_index(index_path)
        
        # Загружаем чанки пользователя
        chunks = load_user_chunks(request.user_id)
        
        # Получаем эмбеддинг запроса
        query_embedding = embedding_model.encode([request.query])
        
        # Ищем в FAISS
        distances, indices = index.search(query_embedding, request.top_k)
        
        # Получаем релевантные чанки
        relevant_chunks = [chunks[i] for i in indices[0]]
        
        # Генерируем ответ через LLM
        response = generate_llm_response(request.query, relevant_chunks)
        
        return {"response": response}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_llm_response(query: str, chunks: List[str]) -> str:
    context = "\n".join(chunks)
    print("context:", context)
    prompt = f"""Отвечай на русском языке.
Контекст: {context}
Вопрос: {query}
Ответ:"""
    
    response = llm_client.chat.completions.create(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)