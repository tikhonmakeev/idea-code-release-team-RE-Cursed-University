import os
import PyPDF2
import re
import json

# Function to process all files in a folder
def process_folder(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Папка '{folder_path}' не найдена.")
        return

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Process PDF files
        if file_name.endswith(".pdf"):
            convert_pdf_to_text(file_path)

        # Process TXT files
        elif file_name.endswith(".txt"):
            upload_txtfile(file_path)

        # Process JSON files
        elif file_name.endswith(".json"):
            upload_jsonfile(file_path)

        else:
            print(f"Файл '{file_name}' не поддерживается. Пропускаем.")

# Function to convert PDF to text and append to vault.txt
def convert_pdf_to_text(file_path):
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            text = ''
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                if page.extract_text():
                    text += page.extract_text() + " "
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split into chunks
            sentences = re.split(r'(?<=[.!?]) +', text)
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 < 1000:
                    current_chunk += (sentence + " ").strip()
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:
                chunks.append(current_chunk)
            
            # Append chunks to vault.txt
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    vault_file.write(chunk.strip() + "\n")
            print(f"PDF файл '{file_path}' добавлен в vault.txt.")
    except Exception as e:
        print(f"Ошибка при обработке PDF файла '{file_path}': {str(e)}")

# Function to upload a text file and append to vault.txt
def upload_txtfile(file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as txt_file:
            text = txt_file.read()
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split into chunks
            sentences = re.split(r'(?<=[.!?]) +', text)
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 < 1000:
                    current_chunk += (sentence + " ").strip()
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:
                chunks.append(current_chunk)
            
            # Append chunks to vault.txt
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    vault_file.write(chunk.strip() + "\n")
            print(f"Текстовый файл '{file_path}' добавлен в vault.txt.")
    except Exception as e:
        print(f"Ошибка при обработке текстового файла '{file_path}': {str(e)}")

# Function to upload a JSON file and append to vault.txt
def upload_jsonfile(file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
            
            # Convert JSON to string
            text = json.dumps(data, ensure_ascii=False)
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split into chunks
            sentences = re.split(r'(?<=[.!?]) +', text)
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 < 1000:
                    current_chunk += (sentence + " ").strip()
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:
                chunks.append(current_chunk)
            
            # Append chunks to vault.txt
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    vault_file.write(chunk.strip() + "\n")
            print(f"JSON файл '{file_path}' добавлен в vault.txt.")
    except Exception as e:
        print(f"Ошибка при обработке JSON файла '{file_path}': {str(e)}")

def main():
    # Specify the folder path containing the files
    folder_path = "/home/annalebedeva/Repos/idea-code-release-team-RE-Cursed-University/ai/resources"  # Укажите путь к вашей папке здесь
    
    # Process all files in the folder
    process_folder(folder_path)

if __name__ == "__main__":
    main()