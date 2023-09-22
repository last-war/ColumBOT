from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.repository.doc import create_doc
from src.repository.users import get_use_docs, user_add_use_docs


def is_valid_pdf(file_path: str, password: str = None) -> bool:
    try:
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            if pdf.is_encrypted:
                if password:
                    pdf.decrypt(password)
                else:
                    return False  # PDF is encrypted, but no password provided.
            for page in pdf.pages:
                if '/JavaScript' in page and '/S' in page['/JavaScript']:
                    return False
            return True
    except Exception as e:
        print(e)
        return False


async def create_index(file_path: str, sender_id: int, file_name: str, db: Session, password: str = None) -> None:
    print('pdf check')
    if not is_valid_pdf(file_path, password):
        print("Неприпустимий PDF-файл з вкладеними скриптами або невірним паролем.")
        return
    print(f'{file_path} load index')
    print('# Відкриваємо PDF-файл за вказаним шляхом')
    reader = PdfReader(open(file_path, 'rb'))
    text = ''

    # Записуємо отриманий текст у файл output.txt у вказану директорію
    print('# Зчитуємо текст з кожної сторінки PDF і додаємо його до змінної text')
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()

    print('# Записуємо отриманий текст у файл output.txt у вказану директорію')
    with open(f'{settings.output_dir}/output.txt', 'w', encoding='utf-8') as file:
        file.write(text)

    # Зберегти документ в базу постгреc
    doc = await create_doc(sender_id, file_name, text, db)
    user_use_docs = await get_use_docs(sender_id, db)
    # Якщо список обраних документів юзера пустий додаємо йому ід цього документу до списку.
    if user_use_docs == 0:
        await user_add_use_docs(sender_id, doc.id, db)

    print('# Завантажуємо тексти з файлів у вказаній директорії')
    loader = DirectoryLoader(
        settings.output_dir,
        glob='**/*.txt',
        loader_cls=TextLoader
    )

    print('# Завантажуємо документи з вказаної директорії')
    documents = loader.load()

    print("# Ініціалізуємо об'єкт для розділення тексту на частини")
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1024,
        chunk_overlap=128
    )

    print('# Розділяємо тексти на частини')
    texts = text_splitter.split_documents(documents)

    print("# Ініціалізуємо об'єкт для векторизації тексту за допомогою OpenAI")
    #embeddings = HuggingFaceEmbeddings()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    print('# Визначаємо директорію для збереження векторів')
    persist_directory = settings.db_dir

    print('# Створюємо та зберігаємо індекс векторів Chroma')

    print(embeddings)
    print(persist_directory)

    vectordb = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print('# Зберігаємо створений індекс')
    #vectordb.persist()
    #vectordb = None

