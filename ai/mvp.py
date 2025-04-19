from sentence_transformers import SentenceTransformer  # Исправлено: transformers вместо transform_ers
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline
import sys
from upload import main as upload_main

# Шаг 1: Чтение данных и создание эмбеддингов (оптимизированная версия)
def load_data_and_embeddings(file_path="vault.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            chunks = [line.strip() for line in f if line.strip()]
        
        if not chunks:
            raise ValueError("Файл vault.txt пуст. Загрузите данные сначала через upload.py")
            
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(chunks)
        return chunks, embeddings
    except FileNotFoundError:
        raise FileNotFoundError("Файл vault.txt не найден. Сначала загрузите данные через upload.py")

# Шаг 2: Поиск релевантных фрагментов (оптимизированная версия)
def find_relevant_chunks(query, chunks, embeddings, top_k=3):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)
    top_indices = np.argsort(similarities[0])[-top_k:][::-1]
    return [chunks[i] for i in top_indices]

# Шаг 3: Генерация ответа с помощью локальной LLM
def generate_response(query, relevant_chunks):
    context = "\n".join(relevant_chunks)
    
    # Инициализируем локальную LLM (можно заменить на другую модель)
    qa_pipeline = pipeline(
        "text-generation",
        model="IlyaGusev/saiga_mistral_7b",
        device="cpu"  # или "cuda" если есть GPU
    )
    
    prompt = f"""Контекст: {context}
Вопрос: {query}
Ответ:"""
    
    response = qa_pipeline(
        prompt,
        max_new_tokens=150,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )
    
    return response[0]['generated_text'].split("Ответ:")[-1].strip()

# Основная функция RAG с обработкой ошибок
def rag_pipeline(query, file_path="vault.txt"):
    try:
        chunks, embeddings = load_data_and_embeddings(file_path)
        relevant_chunks = find_relevant_chunks(query, chunks, embeddings)
        
        if not relevant_chunks:
            return "Не удалось найти релевантную информацию в документах."
            
        answer = generate_response(query, relevant_chunks)
        return answer
        
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

# Пример использования с интеграцией с upload.py
if __name__ == "__main__":
    # Проверяем, есть ли аргументы командной строки
    if len(sys.argv) > 1 and sys.argv[1] == "upload":
        upload_main()
    else:
        # Интерактивный режим вопрос-ответ
        print("RAG система готова к работе. Данные загружены из vault.txt")
        print("Введите 'exit' для выхода.")
        
        while True:
            query = input("\nВаш вопрос: ")
            if query.lower() == 'exit':
                break
                
            answer = rag_pipeline(query)
            print("\nОтвет:", answer)