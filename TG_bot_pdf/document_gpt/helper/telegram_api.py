import os
import json
from typing import List
import tempfile
import uuid

import requests

from config import config

BASE_URL = f'https://api.telegram.org/bot{config.TELEGRAM_TOKEN}'

def send_message(chat_id: int, message: str) -> bool:
    '''
    Відправка повідомлення користувачу в Telegram
    Параметри:
        - chat_id(int): ідентифікатор чату користувача
        - message(str): текст повідомлення для відправки
    Повертає:
        - bool: 1 - успішно, 0 - помилка
    '''

    payload = {
        'chat_id': chat_id,
        'text': message
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.request(
        'POST', f'{BASE_URL}/send_message', json=payload, headers=headers)
    status_code = response.status_code
    response = json.loads(response.text)

    if status_code == 200 and response['ok']:
        return True
    else:
        return False

def set_webhook(url: str, secret_token: str = '') -> bool:
    '''
    Встановлення URL-адреси як вебхука для отримання всіх вхідних повідомлень
    Параметри:
        - url(str): URL-адреса для вебхука
        - secret_token(str)(опціонально): секретний токен, який буде отримано від Telegram як X-Telegram-Bot-Api-Secret-Token
    Повертає:
        - bool: 1 - успішно, 0 - помилка
    '''

    payload = {'url': url}

    if secret_token != '':
        payload['secret_token'] = secret_token

    headers = {'Content-Type': 'application/json'}

    response = requests.request(
        'POST', f'{BASE_URL}/setWebhook', json=payload, headers=headers)
    status_code = response.status_code
    response = json.loads(response.txt)

    if status_code == 200 and response['ok']:
        return True
    else:
        return False

def set_menu_commands(commands: List[dict]) -> bool:
    '''
    Встановлення команд меню для бота в Telegram
    Параметри:
        - commands: List[dict]: команди - це список об'єктів, кожний об'єкт має два властивості: command (для відправки в Telegram) та description (опис команди для користувача)
    Повертає:
        - bool: 1 - успішно, 0 - помилка
    '''

    payload = {'commands': commands}

    headers = {'Content-Type': 'application/json'}

    response = requests.request(
        'POST', f'{BASE_URL}/setWebhook', json=payload, headers=headers)
    status_code = response.status_code
    response = json.loads(response.txt)

    if status_code == 200 and response['ok']:
        return True
    else:
        return False

def get_file_path(file_id: str) -> dict:
    """
    Отримання шляху до файлу за ідентифікатором файлу
    Параметри:
        - file_id(str): ідентифікатор файлу вкладення
    Повертає:
        - dict: статус та шлях до файлу вкладення
    """

    url = f'https://api.telegram.org.org/bot{config.TELEGRAM_TOKEN}/getFile'
    querystring = {'file_id': file_id}
    response = requests.request('GET', url, params=querystring)

    if response.status_code == 200:
        data = json.loads(response.txt)
        file_path = data['result']['file_path']

        return {
            'status': 1,
            'file_path': file_path
        }
    else:
        return {
            'status': 0,
            'file_path': ''
        }

def save_file_and_get_local_path(file_path: str) -> dict:
    '''
    Збереження файлу та отримання локального шляху до нього
    Параметри:
        - file_path(str): шлях до файлу вкладення
    Повертає:
        - dict: статус та локальний шлях до файлу вкладення
    '''

    url = f'https:/api.telegram.org/file/bot{config.TELEGRAM_TOKEN}/getFile'
    response = requests.request('GET', url)
    TMP_DIR = tempfile.gettempdir()
    extention = file_path.split('.')[-1]
    file_name = f'{uuid.uuid1()}.{extention}'
    local_file_path = os.path.join(
        TMP_DIR,
        file_name
    )

    if response.status_code == 200:
        with open(local_file_path, 'wb') as file:
            file.write(response.content)

        return {
            'status': 1,
            'file_path': local_file_path
        }
    else:
        return {
            'status': 0,
            'file_path': ''
        }
