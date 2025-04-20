import io
import PyPDF2
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from pathlib import Path
import json
import os
import re
from datetime import datetime

model = SentenceTransformer('all-MiniLM-L6-v2')

# Пути для хранения данных
INDEX_STORAGE_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_indices")
METADATA_FILE = os.path.join(INDEX_STORAGE_PATH, "user_metadata.json")
os.makedirs(INDEX_STORAGE_PATH, exist_ok=True)

# Получаем путь к папке с файлами из переменных окружения
SOURCE_FOLDER = os.getenv("BASE_USER_FILES_DIR", "user_files")
os.makedirs(SOURCE_FOLDER, exist_ok=True)


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


def save_embeddings_for_file(base_dir: str, user_id: str, filename: str):
    """
    Обрабатывает указанный файл и обновляет соответствующий FAISS индекс
    Возвращает словарь с результатами обработки
    """
    try:
        file_path = Path(os.path.join(base_dir, user_id, filename))
        if not file_path.exists():
            return {"status": "error", "message": "File not found"}

        # Извлекаем user_id из структуры папок (предполагаем SOURCE_FOLDER/user_id/filename)
        relative_path = file_path.relative_to(SOURCE_FOLDER)
        user_id = relative_path.parts[0] if len(relative_path.parts) > 1 else "default_user"

        # Инициализируем all_chunks существующими чанками пользователя
        all_chunks = []
        chunks_path = os.path.join(INDEX_STORAGE_PATH, f"chunks_{user_id}.json")

        if os.path.exists(chunks_path):
            with open(chunks_path, 'r', encoding='utf-8') as f:
                all_chunks = json.load(f)

        # Обрабатываем файл
        file_type = file_path.suffix.lower()

        with open(file_path, 'rb') as f:
            content = f.read()

        if file_type == '.txt':
            chunks = process_text_content(content.decode('utf-8'))
        elif file_type == '.pdf':
            chunks = process_pdf_content(content)
        elif file_type == '.json':
            chunks = process_json_content(content)
        else:
            return {"status": "error", "message": f"Unsupported file type: {file_type}"}

        all_chunks.extend(chunks)

        if not all_chunks:
            return {"status": "error", "message": "No valid content found in file"}

        # Генерируем эмбеддинги
        embeddings = model.encode(all_chunks)

        # Создаем/обновляем FAISS индекс
        index_path = os.path.join(INDEX_STORAGE_PATH, f"index_{user_id}.faiss")
        dimension = embeddings.shape[1]

        if os.path.exists(index_path):
            index = faiss.read_index(index_path)
            index.reset()
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

        return {
            "status": "success",
            "user_id": user_id,
            "chunks_count": len(all_chunks),
            "index_path": index_path,
            "processed_file": str(file_path)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


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


def get_user_info(user_id: str) -> Dict:
    """Получение информации об обработанных файлах пользователя"""
    current_data = load_user_metadata()
    if user_id not in current_data:
        return {"status": "error", "message": "User not found"}
    return current_data[user_id]


def process_all_existing_files():
    """Обрабатывает все существующие файлы в SOURCE_FOLDER"""
    results = []
    for root, _, files in os.walk(SOURCE_FOLDER):
        for filename in files:
            file_path = os.path.join(root, filename)
            result = save_embeddings_for_file(file_path)
            results.append(result)
    return results


# При старте можно обработать все существующие файлы
if __name__ == "__main__":
    print("Processing existing files...")
    results = process_all_existing_files()
    for result in results:
        print(f"Processed: {result.get('processed_file', 'unknown')}, status: {result.get('status', 'unknown')}")
    print("Ready to process new files using make_embeddings_for_file(filename)")