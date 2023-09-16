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


def send_message(chat_id: int, message: str) -> bool:
    """
    Send message to a Telegram user.

    Parameters:
        - chat_id(int): chat id of the user
        - message(str): text message to send

    Returns:
        - bool: either 0 for error or 1 for success
    """

    payload = {
        'chat_id': chat_id,
        'text': message
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.request(
        'POST', f'{settings.base_url}/sendMessage', json=payload, headers=headers)
    status_code = response.status_code
    response = json.loads(response.text)

    if status_code == 200 and response['ok']:
        return True
    else:
        return False


MESSAGE_COMMAND = {
    'send_message': send_message,
}



def bot_logic(chat_id: int, message: str) -> bool:
    if message in MESSAGE_COMMAND:





    payload = {
        'chat_id': chat_id,
        'text': message
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.request(
        'POST', f'{settings.base_url}/sendMessage', json=payload, headers=headers)
    status_code = response.status_code
    response = json.loads(response.text)

    if status_code == 200 and response['ok']:
        return True
    else:
        return False
