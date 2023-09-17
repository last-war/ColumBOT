from langchain.embeddings import OpenAIEmbeddings  # Імпорт бібліотеки для роботи з векторними представленнями тексту від OpenAI
from langchain.vectorstores import Chroma  # Імпорт бібліотеки для зберігання та роботи з векторними представленнями тексту
from langchain.chat_models import ChatOpenAI  # Імпорт бібліотеки, яка використовує модель чат-бота від OpenAI
from langchain.chains import ConversationalRetrievalChain  # Імпорт бібліотеки для створення ланцюжка обробки чат-взаємодії
from langchain.memory import ConversationBufferMemory  # Імпорт бібліотеки для роботи з пам'яттю для зберігання історії розмови

# Імпорт конфігураційних налаштувань з файлу config.py
from src.conf.config import settings


def create_conversation() -> ConversationalRetrievalChain:
    # Встановлення шляху до папки для збереження даних
    persist_directory = settings.db_dir

    # Ініціалізація моделі для створення векторних представлень тексту від OpenAI
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings._ai_api_key
    )

    # Ініціалізація бази даних для зберігання векторних представлень тексту
    db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    # Ініціалізація пам'яті для зберігання історії розмови
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=False
    )

    # Створення ланцюжка обробки чат-взаємодії з використанням моделі чат-бота від OpenAI
    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(),
        chain_type='stuff',
        retriever=db.as_retriever(),
        memory=memory,
        get_chat_history=lambda h: h,
        verbose=True
    )

    return qa
