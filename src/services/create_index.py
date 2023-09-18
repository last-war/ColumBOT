from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from PyPDF2 import PdfReader

from src.conf.config import settings


def create_index(file_path: str) -> None:
    # Відкриваємо PDF-файл за вказаним шляхом
    reader = PdfReader(file_path)
    text = ''
    
    # Зчитуємо текст з кожної сторінки PDF і додаємо його до змінної text
    for page in reader.pages:
        text += page.extract_text()

    # Записуємо отриманий текст у файл output.txt у вказану директорію
    with open(f'{settings.output_dir}/output.txt', 'w', encoding='utf-8') as file:
        file.write(text)

    # Завантажуємо тексти з файлів у вказаній директорії
    loader = DirectoryLoader(
        settings.output_dir,
        glob='**/*.txt',
        loader_cls=TextLoader
    )


    # Завантажуємо документи з вказаної директорії
    documents = loader.load()

    # Ініціалізуємо об'єкт для розділення тексту на частини
    text_splitter = CharacterTextSplitter(
    separator='\n',
    chunk_size=1024,
    chunk_overlap=128
    )

    # Розділяємо тексти на частини
    texts = text_splitter.split_documents(documents)

    # Ініціалізуємо об'єкт для векторизації тексту за допомогою OpenAI
    embeddings = HuggingFaceEmbeddings()

    # Визначаємо директорію для збереження векторів
    persist_directory = settings.db_dir

    # Створюємо та зберігаємо індекс векторів Chroma
    vectordb = Chroma.from_documents(
    documents=texts,
    embedding=embeddings,
    persist_directory=persist_directory
    )

    # Зберігаємо створений індекс
    vectordb.persist()

    