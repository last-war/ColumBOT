import os
import json
import tempfile
import uuid
import requests
from fastapi import Depends
from sqlalchemy.orm import Session
from src.conf.config import settings
from src.database.db import get_db
from src.repository.users import (
    get_user_by_user_id,
    create_user,
    set_user_falcon_model,
    set_user_dolly_model,
    set_user_openai_model,
    get_user_model,
    delete_user_documents,  # Додали функцію для видалення документів користувача
)
from src.repository.doc import get_user_documents
from src.schemas.users import UserModel
from src.services.create_index import create_index
from src.services.falcon_llm import create_conversation as create_falcon_conversation
from src.services.dolly_llm import create_conversation as create_dolly_conversation

BASE_URL = f'https://api.telegram.org/bot{settings.telegram_token}'

async def set_webhook(url: str, secret_token: str = '') -> bool:
    print('Setting webhook')
    payload = {'url': url}
    if secret_token != '':
        payload['secret_token'] = secret_token
    headers = {'Content-Type': 'application/json'}
    response = requests.request('POST', f'{settings.base_url}/setWebhook', json=payload, headers=headers)
    print(response.text)
    status_code = response.status_code
    response = json.loads(response.text)
    if status_code == 200 and response['ok']:
        return True
    else:
        return False

async def bot_logic(telegram_data: dict, db: Session) -> bool:
    if 'application/pdf' in telegram_data['mime_type']:
        payload = await load_pdf(telegram_data, db)
        headers = {'Content-Type': 'application/json'}
        response = requests.request('POST', f'{settings.base_url}/{payload[1]}', json=payload[0], headers=headers)
        status_code = response.status_code
        response = json.loads(response.text)
        if status_code == 200 and response['ok']:
            return True
        else:
            return False

    if telegram_data['text'] in MESSAGE_COMMAND.keys():
        response = await MESSAGE_COMMAND.get(telegram_data['text'])(telegram_data, db)
        headers = {'Content-Type': 'application/json'}
        response = requests.request('POST', f'{settings.base_url}/{response[1]}', json=response[0], headers=headers)
        status_code = response.status_code
        response = json.loads(response.text)
        if status_code == 200 and response['ok']:
            return True

    # User change model
    if telegram_data['is_data']:
        model_ = 'Помилка. Модель не обрано...'
        if telegram_data['data'] == 'falcon_model':  # Змінено умову порівняння
            model_ = await set_user_falcon_model(telegram_data['sender_id'], db)
        elif telegram_data['data'] == 'dolly_model':  # Змінено умову порівняння
            model_ = await set_user_dolly_model(telegram_data['sender_id'], db)
        elif telegram_data['data'] == 'openai_model':  # Змінено умову порівняння
            model_ = await set_user_openai_model(telegram_data['sender_id'], db)

        payload = {
            'chat_id': telegram_data['sender_id'],
            'text': f'Ви обрали модель: {str(model_.name)}.'
        }

        headers = {'Content-Type': 'application/json'}

        response = requests.request(
            'POST', f'{settings.base_url}/SendMessage', json=payload, headers=headers)
        status_code = response.status_code
        response = json.loads(response.text)

        if status_code == 200 and response['ok']:
            return True

    else:

        # Activate model user
        model = await get_user_model(telegram_data['sender_id'], db)
        try:
            if model == "falcon":
                print('falcon')
                qa = create_falcon_conversation()
                q_text = qa({'question': telegram_data['text'], 'chat_history': {}})
            elif model == "dolly":
                print('dolly')
                qa = create_dolly_conversation()
                q_text = qa({'question': telegram_data['text'], 'chat_history': {}})
            elif model == "openai":
                pass

        except Exception as e:
            print('exception')
            q_text = {'answer': e}

        payload = {
            'chat_id': telegram_data['sender_id'],
            'text': f"Відповідь на питання {telegram_data['text']}: {q_text['answer']}",
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.request(
            'POST', f'{settings.base_url}/SendMessage', json=payload, headers=headers)
        status_code = response.status_code
        response = json.loads(response.text)

        if status_code == 200 and response['ok']:
            return True
        else:
            return False


def create_command_menu():
    headers = {'Content-Type': 'application/json'}

    commands = [
        {"command": "/choose_model", "description": "Обрати модель"},
        {"command": "/choose_pdf", "description": "Обрати ПДФ"},
        {"command": "/helps", "description": "Допомога"},
        {"command": "/del_files", "description": "Видалити всі файли"}  # Додана команда для видалення всіх файлів
    ]

    data = {"commands": commands}

    response = requests.request(
        'POST', f'{settings.base_url}/setMyCommands', json=data)
    status_code = response.status_code
    response = json.loads(response.text)

    if status_code == 200:
        return True
    else:
        return False


async def start(telegram_data: dict, db: Session) -> tuple:
    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': 'Привіт друже, це АІ бот який допоможе тобі знайти відповідь на питання. Просто завантаж ПДФ.'
    }
    print('telegram data ----> \n' + str(telegram_data))
    user = await get_user_by_user_id(telegram_data['sender_id'], db)
    if user:
        return payload, 'SendMessage'
    elif not user:
        await create_user(UserModel(user_id=telegram_data['sender_id'],
                                    is_bot=telegram_data['is_bot'],
                                    first_name=telegram_data['first_name'],
                                    username=telegram_data['username']), db)
        print('Create user')

        return payload, 'SendMessage'


async def load_pdf(telegram_data: dict, db: Session) -> tuple:
    url = f'https://api.telegram.org/bot{settings.telegram_token}/getFile'
    querystring = {'file_id': telegram_data['file_id']}
    response = requests.request('GET', url, params=querystring)
    if response.status_code == 200:
        print('get file id')
        data = json.loads(response.text)
        file_path = data['result']['file_path']
        url = f'https://api.telegram.org/file/bot{settings.telegram_token}/{file_path}'
        response = requests.request('GET', url)
        TMP_DIR = tempfile.gettempdir()
        file_name = f'{uuid.uuid1()}.pdf'
        local_file_path = os.path.join(
            TMP_DIR,
            file_name
        )
        if response.status_code == 200:
            print('get file to pdf')
            with open(local_file_path, 'wb') as file:
                file.write(response.content)
                file.close()
            await create_index(local_file_path, sender_id=telegram_data['sender_id'], file_name=file_name, db=db)
            # Create doc in postgres database
            print(local_file_path)
            os.unlink(local_file_path)

    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': 'Файл прийнято, задавайте Ваше питання'
    }

    return payload, 'SendMessage'


async def choose_pdf(telegram_data: dict, db: Session) -> tuple:
    user_documents = await get_user_documents(telegram_data['sender_id'], db)
    
    # Підготовка відповіді для користувача
    if user_documents:
        # Якщо є документи, то відправляємо їх користувачеві разом з кнопкою для видалення
        keyboard = {
            'inline_keyboard': [
                [{'text': 'Видалити всі файли', 'callback_data': 'delete_all_files'}],
            ]
        }
        keyboard_json = json.dumps(keyboard)
        documents_text = "\n".join(user_documents)
        response_text = f"Ваші документи:\n{documents_text}\n\nВи можете видалити всі файли за допомогою кнопки нижче:"
    else:
        # Якщо документів немає, повідомляємо користувачеві про це
        response_text = "У вас немає збережених документів."
        keyboard_json = None

    # Підготовка відповіді для відправки користувачеві
    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': response_text,
        'reply_markup': keyboard_json  # Додаємо кнопку для видалення файлів
    }

    return payload, 'SendMessage'


async def delete_all_files(telegram_data: dict, db: Session) -> tuple:
    await delete_user_documents(telegram_data['sender_id'], db)

    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': 'Всі файли були успішно видалені.'
    }

    return payload, 'SendMessage'


async def choose_model(telegram_data: dict, db: Session) -> tuple:
    user_model = await get_user_model(telegram_data['sender_id'], db)
    keyboard = {
        'inline_keyboard': [
            [{'text': 'Falcon', 'callback_data': 'falcon_model'}],
            [{'text': 'Dolly', 'callback_data': 'dolly_model'}],
            [{'text': 'OpenAI', 'callback_data': 'openai_model'}],
        ]
    }

    keyboard_json = json.dumps(keyboard)

    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': f'Зараз активна модель: {user_model}. Для того щоб змінити оберіть модель нижче:',
        'reply_markup': keyboard_json
    }

    return payload, 'SendMessage'


async def helps(telegram_data: dict, db: Session) -> tuple:
    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': 'Для початку необхідно відправити пдф файл. Після чого можна задавати питання по його змістом. Просто!'
    }

    return payload, 'SendMessage'


MESSAGE_COMMAND = {
    '/start': start,
    '/choose_model': choose_model,
    '/choose_pdf': choose_pdf,
    '/helps': helps,
    '/del_files': delete_all_files  # Додана команда для видалення всіх файлів
}

