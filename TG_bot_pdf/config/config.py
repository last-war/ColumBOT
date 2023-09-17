# Імпорт необхідних модулів
import os
from dotenv import load_dotenv, find_dotenv

# Завантаження змінних середовища з файлу .env (якщо він існує)
load_dotenv(find_dotenv())

# Отримання значень змінних середовища
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')            # Ключ API OpenAI
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Визначення шляхів до директорій та файлів
DB_DIR = 'data/db'                                   # Директорія для бази даних
INPUT_FILE_PATH = 'data/input/sample.pdf'            # Шлях до вхідного PDF-файлу
OUTPUT_DIR = 'data/output'                           # Директорія для виводу даних
