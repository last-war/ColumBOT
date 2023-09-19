import os
import json
import tempfile
import uuid

import requests

from src.conf.config import settings
from src.services.create_index import create_index


BASE_URL = f'https://api.telegram.org/bot{settings.telegram_token}'


async def set_webhook(url: str, secret_token: str = '') -> bool:
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


async def bot_logic(telegram_data: dict) -> bool:
    if telegram_data['text'] in MESSAGE_COMMAND.keys():
        response = await MESSAGE_COMMAND.get(telegram_data['text'])(telegram_data['sender_id'], telegram_data['text'], telegram_data)

        headers = {'Content-Type': 'application/json'}

        response = requests.request(
            'POST', f'{settings.base_url}/{response[1]}', json=response[0], headers=headers)
        status_code = response.status_code
        response = json.loads(response.text)

        if status_code == 200 and response['ok']:
            return True
    else:
        return False


def create_command_menu():
    headers = {'Content-Type': 'application/json'}

    commands = [
        {"command": "/load_pdf", "description": "Завантажити PDF"},
        {"command": "/choose_pdf", "description": "Обрати ПДФ"},
        {"command": "/send_question", "description": "Задати питання"},
        {"command": "/helps", "description": "Допомога"}
    ]

    data = {"commands": commands}

    response = requests.request(
        'POST', f'{settings.base_url}/setMyCommands', json=data)
    status_code = response.status_code
    print(status_code)
    response = json.loads(response.text)
    print(response)

    if status_code == 200:
        return True
    else:
        return False


async def load_pdf(chat_id: int, message: str, telegram_data: dict) -> tuple:
    if 'application/pdf' not in telegram_data['mime_type']:
        payload = {
            'chat_id': chat_id,
            'text': "The bot can only understand PDF files"
        }

        return payload, 'SendMessage'

    url = f'https://api.telegram.org/bot{settings.telegram_token}/getFile'
    querystring = {'file_id': telegram_data['file_id']}
    response = await requests.request('GET', url, params=querystring)

    if response.status_code == 200:
        print('file start')
        data = await json.loads(response.txt)
        file_path = data['result']['file_path']

        TMP_DIR = tempfile.gettempdir()
        extention = file_path.split('.')[-1]
        file_name = f'{uuid.uuid1()}.{extention}'
        local_file_path = os.path.join(
            TMP_DIR,
            file_name
        )

        with open(local_file_path, 'wb') as file:
            file.write(response.content)

        create_index(local_file_path)
        os.unlink(local_file_path)

    payload = {
        'chat_id': chat_id,
        'text': 'Пдф завантажено.......'
    }

    return payload, 'SendMessage'


async def choose_pdf(chat_id: int, message: str, telegram_data: dict) -> tuple:
    #TODO logic choose pdf
    payload = {
        'chat_id': chat_id,
        'text': 'Пдф обрано для роботи.......'
    }

    return payload, 'SendMessage'


async def send_question(chat_id: int, message: str, telegram_data: dict) -> tuple:
    #TODO logic send question pdf
    payload = {
        'chat_id': chat_id,
        'text': 'Відповідь на питання по ПДФ.......'
    }

    return payload, 'SendMessage'


async def helps(chat_id: int, message: str, telegram_data: dict) -> tuple:
    #TODO logic help
    payload = {
        'chat_id': chat_id,
        'text': 'Коротка довідка по застосунку'
    }

    return payload, 'SendMessage'


MESSAGE_COMMAND = {
    '/load_pdf': load_pdf,
    '/choose_pdf': choose_pdf,
    '/send_question': send_question,
    '/helps': helps,
}
