import json
from io import BytesIO
import matplotlib.pyplot as plt
import requests
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.repository.doc import get_user_documents, get_all_doc
from src.repository.queries import get_all_queries
from src.repository.users import get_all_users


async def admin_panel_users_query(telegram_data: dict, db: Session) -> bool:
    users = await get_all_users(db)
    queries = await get_all_queries(db)

    result_user = []
    result_queries = []

    for user in users:
        result_user.append(f"id:{user.user_id}")
        queries_ = []
        for query in queries:
            if query.user_id == user.id:
                queries_.append(query)
        result_queries.append(len(queries_))

    # Створюємо кругову діаграму
    plt.figure(figsize=(7, 7))  # Розмір діаграми (опціонально)

    plt.pie(result_queries, labels=result_user, autopct='%1.1f%%', startangle=140)
    # autopct - формат виводу відсотків, startangle - початковий кут

    plt.title('Діаграма запитів користувачів:', y=1.10)
    plt.axis('equal')  # Рівномірність вісей для отримання кругової діаграми

    image_data = BytesIO()
    plt.savefig(image_data, format='jpg')
    image_data.seek(0)

    payload = {
        'chat_id': telegram_data['sender_id'],
        'caption': 'diagram'
    }

    response = requests.request(
        'POST', f'{settings.base_url}/SendPhoto',
        data=payload,
        files={'photo': image_data})

    status_code = response.status_code
    response = json.loads(response.text)

    if status_code == 200 and response['ok']:
        return True


async def admin_panel_users_in_db(db: Session) -> str:
    result = ""

    users = await get_all_users(db)

    for user in users:
        result += f'user_id:{user.user_id}|username:{user.username} \n'

    return result


async def admin_panel_users_file_in_db(db: Session) -> str:
    result = ""

    users = await get_all_users(db)
    all_docs = await get_all_doc(db)

    for user in users:
        count_doc = []
        for doc in all_docs:
            if doc.user_id == user.id:
                count_doc.append(doc)
        result += f'user_id:{user.user_id}|user_doc:{len(count_doc)} \n'

    return result
