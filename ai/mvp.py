from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI

# Чтение данных и создание эмбеддингов
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

# Поиск релевантных фрагментов
def find_relevant_chunks(query, chunks, embeddings, top_k=3):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)
    top_indices = np.argsort(similarities[0])[-top_k:][::-1]
    return [chunks[i] for i in top_indices]

# Генерация ответа с помощью локальной LLM
def generate_response(query, relevant_chunks):
    # Формируем контекст из релевантных фрагментов
    context = "\n".join(relevant_chunks)

    # Создаем клиент для взаимодействия с Ollama
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama',  # API ключ для Ollama
    )

    # Формируем промпт с контекстом и вопросом пользователя
    prompt = f"""Контекст: {context}
Вопрос: {query}
Ответ:"""

    # Отправляем запрос к модели
    response = client.chat.completions.create(
        model="llama3",  # Используем модель Llama 3
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    # Извлекаем содержимое ответа
    response_content = response.choices[0].message.content
    return response_content.strip()

# Основная функция RAG с обработкой ошибок
def rag_pipeline(query, file_path="vault.txt"):
    try:
        # Загружаем данные и эмбеддинги
        chunks, embeddings = load_data_and_embeddings(file_path)
        
        # Находим релевантные фрагменты
        relevant_chunks = find_relevant_chunks(query, chunks, embeddings)
        
        if not relevant_chunks:
            return "Не удалось найти релевантную информацию в документах."
            
        # Генерируем ответ с использованием модели
        answer = generate_response(query, relevant_chunks)
        return answer
        
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

# Пример использования с интеграцией с upload.py
if __name__ == "__main__":
    # Путь к папке с файлами
    folder_path = "ai/resources"
    
    # Загружаем данные из папки в vault.txt
    from upload import process_folder  # Импортируем новую функцию
    process_folder(folder_path)

    # Интерактивный режим вопрос-ответ
    print("RAG система готова к работе. Данные загружены из vault.txt")
    print("Введите 'exit' для выхода.")

    while True:
        query = input("\nВаш вопрос: ")
        if query.lower() == 'exit':
            break

        # Получаем ответ от RAG-системы
        answer = rag_pipeline(query)
        print("\nОтвет:", answer)