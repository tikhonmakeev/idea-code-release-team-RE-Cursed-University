import io
import PyPDF2
import numpy as np
import faiss
from fastapi import FastAPI, UploadFile, HTTPException, File
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
import uvicorn
import json
import os
import re
from datetime import datetime


app = FastAPI()
model = SentenceTransformer('all-MiniLM-L6-v2')

# Пути для хранения данных
INDEX_STORAGE_PATH = "faiss_indices"
METADATA_FILE = os.path.join(INDEX_STORAGE_PATH, "user_metadata.json")
os.makedirs(INDEX_STORAGE_PATH, exist_ok=True)

class ProcessResponse(BaseModel):
    status: str
    user_id: str
    chunks_count: int
    index_path: str

def load_user_metadata() -> Dict[str, Dict]:
    """Загружает метаданные пользователей из файла"""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_metadata(data: Dict[str, Dict]):
    """Сохраняет метаданные пользователей в файл"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Загружаем существующие метаданные при старте
user_data_storage = load_user_metadata()

@app.post("/process_files/", response_model=ProcessResponse)
async def process_files(
    user_id: str,
    files: List[UploadFile] = File(...)
):
    """
    Обрабатывает загруженные файлы пользователя и создает/обновляет FAISS индекс
    """
    try:
        # Инициализируем all_chunks существующими чанками пользователя (если они уже есть в папках)
        all_chunks = []
        chunks_path = os.path.join(INDEX_STORAGE_PATH, f"chunks_{user_id}.json")
        
        # Если у пользователя уже есть чанки, загружаем их
        if os.path.exists(chunks_path):
            with open(chunks_path, 'r', encoding='utf-8') as f:
                all_chunks = json.load(f)
        
        # Обрабатываем новые файлы
        for file in files:
            content = await file.read()
            file_type = Path(file.filename).suffix.lower()
            
            if file_type == '.txt':
                chunks = process_text_content(content.decode('utf-8'))
            elif file_type == '.pdf':
                chunks = process_pdf_content(content)
            elif file_type == '.json':
                chunks = process_json_content(content)
            else:
                print(f"Unsupported file type: {file_type}")
                continue
                
            all_chunks.extend(chunks)
        
        if not all_chunks:
            raise HTTPException(status_code=400, detail="No valid content found in files")
        
        # Генерируем эмбеддинги для всех чанков (старых и новых)
        embeddings = model.encode(all_chunks)
        
        # Создаем/обновляем FAISS индекс
        index_path = os.path.join(INDEX_STORAGE_PATH, f"index_{user_id}.faiss")
        dimension = embeddings.shape[1]
        
        # Если индекс уже существует, загружаем и обновляем его
        if os.path.exists(index_path):
            index = faiss.read_index(index_path)
            index.reset()  # Очищаем старые данные
            index.add(embeddings)
        else:
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
        
        faiss.write_index(index, index_path)
        
        # Сохраняем обновленные чанки
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, ensure_ascii=False)
        
        # Обновляем метаданные
        user_data_storage[user_id] = {
            "chunks_path": chunks_path,
            "index_path": index_path,
            "chunks_count": len(all_chunks),
            "timestamp": str(datetime.now())
        }
        save_user_metadata(user_data_storage)
        
        return ProcessResponse(
            status="success",
            user_id=user_id,
            chunks_count=len(all_chunks),
            index_path=index_path
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/user_info/{user_id}")
async def get_user_info(user_id: str):
    """Получение информации о обработанных файлах пользователя"""
    # Всегда загружаем свежие данные из файла
    current_data = load_user_metadata()
    if user_id not in current_data:
        raise HTTPException(status_code=404, detail="User not found")
    return current_data[user_id]

def process_text_content(text: str) -> List[str]:
    """Обработка текстового содержимого"""
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?]) +', text)
    return split_into_chunks(sentences)

def process_pdf_content(pdf_content: bytes) -> List[str]:
    """Обработка PDF файла"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'(?<=[.!?]) +', text)
        return split_into_chunks(sentences)
    except Exception as e:
        print(f"PDF processing error: {str(e)}")
        return []

def process_json_content(json_content: bytes) -> List[str]:
    """Обработка JSON файла"""
    try:
        data = json.loads(json_content.decode('utf-8'))
        text = json.dumps(data, ensure_ascii=False)
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'(?<=[.!?]) +', text)
        return split_into_chunks(sentences)
    except Exception as e:
        print(f"JSON processing error: {str(e)}")
        return []

def split_into_chunks(sentences: List[str], max_length: int = 1000) -> List[str]:
    """Разделение текста на чанки фиксированного размера"""
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += (sentence + " ").strip()
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

@app.get("/user_info/{user_id}")
async def get_user_info(user_id: str):
    """Получение информации о обработанных файлах пользователя"""
    if user_id not in user_data_storage:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data_storage[user_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)