import json

import requests

from src.conf.config import settings


def set_webhook(url: str, secret_token: str = '') -> bool:
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


def bot_logic(chat_id: int, message: str) -> bool:
    if message in MESSAGE_COMMAND.keys():
        response = MESSAGE_COMMAND.get(message)(chat_id, message)

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


def load_pdf(chat_id: int, message: str) -> tuple:
    #TODO logic download pdf
    payload = {
        'chat_id': chat_id,
        'text': 'Пдф завантажено.......'
    }

    return payload, 'SendMessage'


def choose_pdf(chat_id: int, message: str) -> tuple:
    #TODO logic choose pdf
    payload = {
        'chat_id': chat_id,
        'text': 'Пдф обрано для роботи.......'
    }

    return payload, 'SendMessage'


def send_question(chat_id: int, message: str) -> tuple:
    #TODO logic send question pdf
    payload = {
        'chat_id': chat_id,
        'text': 'Відповідь на питання по ПДФ.......'
    }

    return payload, 'SendMessage'


def helps(chat_id: int, message: str) -> tuple:
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
