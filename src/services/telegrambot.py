import os
import json
import tempfile
import uuid

import requests
from fastapi import Depends
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.repository.users import get_user_by_user_id, create_user
from src.schemas.users import UserModel
from src.services.create_index import create_index
from src.services.falcon_llm import create_conversation as create_falcon_conversation
from src.services.dolly_llm import create_conversation as create_dolly_conversation


BASE_URL = f'https://api.telegram.org/bot{settings.telegram_token}'


async def set_webhook(url: str, secret_token: str = '') -> bool:
    print('Setting webhook')
    """
    Set a url as a webhook to receive all incoming messages

    Parameters:
        - url(str): url as a webhook
        - secret_token(str)(Optional): you will receive this secret token from Telegram request as X-Telegram-Bot-Api-Secret-Token

    Returns:
        - bool: either 0 for error or 1 for success
    """

    payload = {'url': url}

    if secret_token != '':
        payload['secret_token'] = secret_token

    headers = {'Content-Type': 'application/json'}

    response = requests.request(
        'POST', f'{settings.base_url}/setWebhook', json=payload, headers=headers)
    print(response.text)
    status_code = response.status_code
    response = json.loads(response.text)

    if status_code == 200 and response['ok']:
        return True
    else:
        return False


async def bot_logic(telegram_data: dict, db: Session) -> bool:
    if 'application/pdf' in telegram_data['mime_type']:
        payload = await load_pdf(telegram_data['sender_id'], telegram_data, db)

        headers = {'Content-Type': 'application/json'}
        response = requests.request(
            'POST', f'{settings.base_url}/{payload[1]}', json=payload[0], headers=headers)
        status_code = response.status_code
        response = json.loads(response.text)

        if status_code == 200 and response['ok']:
            return True
        else:
            return False

    if telegram_data['text'] in MESSAGE_COMMAND.keys():

        response = await MESSAGE_COMMAND.get(telegram_data['text'])(telegram_data['sender_id'], telegram_data['text'],
                                                                    telegram_data, db)

        headers = {'Content-Type': 'application/json'}

        response = requests.request(
            'POST', f'{settings.base_url}/{response[1]}', json=response[0], headers=headers)
        status_code = response.status_code
        response = json.loads(response.text)

        if status_code == 200 and response['ok']:
            return True
    else:
        #TODO отримати перелік доків з бази
        model = "falcon"
        #model = "dolly"
        try:
            if model == "falcon":
                print('falcon')
                qa = create_falcon_conversation()
                q_text = qa({'question': telegram_data['text'], 'chat_history': {}})
                print(q_text.keys())
            else:
                print('dolly')
                qa = create_dolly_conversation()
                q_text = qa({'question': telegram_data['text'], })
        except:
            print('exception')
            q_text = {'answer': 'Помилка отримання з моделі'}

        payload = {
            'chat_id': telegram_data['sender_id'],
            'text': f"Відповідь на питання {telegram_data['text']}: {q_text['answer']}",
        }
        print(payload)
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
        {"command": "/choose_pdf", "description": "Обрати ПДФ"},
        {"command": "/helps", "description": "Допомога"}
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


async def start(chat_id: int, message: str, telegram_data: dict, db: Session) -> tuple:
    payload = {
        'chat_id': chat_id,
        'text': 'Привіт друже, це АІ бот який допоможе тобі знайти відповідь на питання. Просто завантаж ПДФ.'
    }
    print('telegram data ----> \n' + str(telegram_data))
    user = await get_user_by_user_id(chat_id, db)
    if user:
        return payload, 'SendMessage'
    elif not user:
        await create_user(UserModel(user_id=telegram_data['sender_id'],
                                    is_bot=telegram_data['is_bot'],
                                    first_name=telegram_data['first_name'],
                                    username=telegram_data['username']), db)
        print('Create user')

        return payload, 'SendMessage'


async def load_pdf(chat_id: int, telegram_data: dict, db: Session) -> tuple:
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
            # Create  doc in postgres database
            print(local_file_path)
            os.unlink(local_file_path)

    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': 'Файл прийнято, задавайте Ваше питання'
    }

    return payload, 'SendMessage'


async def choose_pdf(chat_id: int, message: str, telegram_data: dict, db: Session) -> tuple:
    payload = {
        'chat_id': chat_id,
        'text': 'Пдф обрано для роботи.......'
    }

    return payload, 'SendMessage'


async def helps(chat_id: int, message: str, telegram_data: dict, db: Session) -> tuple:
    #TODO logic help
    payload = {
        'chat_id': chat_id,
        'text': 'Коротка довідка по застосунку'
    }

    return payload, 'SendMessage'


MESSAGE_COMMAND = {
    '/start': start,
    #'/load_pdf': load_pdf,
    '/choose_pdf': choose_pdf,
    #'/send_question': send_question,
    '/helps': helps,
}
