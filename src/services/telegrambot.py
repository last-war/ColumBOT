import os
import json
import tempfile
import uuid

import requests
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.repository.users import get_user_by_user_id, create_user, set_user_falcon_model, set_user_dolly_model, \
    set_user_gpt2_model, get_user_model, get_user_admin
from src.repository.queries import create_query, get_user_queries
from src.repository.doc import get_user_documents
from src.schemas.users import UserModel
from src.services.admin_panel import admin_panel_users_in_db, admin_panel_users_file_in_db, admin_panel_users_query
from src.services.create_index import create_index
from src.services.falcon_llm import create_conversation as create_falcon_conversation
from src.services.dolly_llm import create_conversation as create_dolly_conversation
from src.services.gpt2_llm import create_conversation as create_gpt2_conversation


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
        payload = await load_pdf(telegram_data, db)

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

        response = await MESSAGE_COMMAND.get(telegram_data['text'])(telegram_data, db)

        headers = {'Content-Type': 'application/json'}

        response = requests.request(
            'POST', f'{settings.base_url}/{response[1]}', json=response[0], headers=headers)
        status_code = response.status_code
        response = json.loads(response.text)

        if status_code == 200 and response['ok']:
            return True

# User change model
    if telegram_data['is_data'] and telegram_data['data'] in ['falcon_model', 'dolly_model', 'gpt2_model']:
        model_ = 'Помилка. Модель не обрано...'
        if telegram_data['data'] in 'falcon_model':
            model_ = await set_user_falcon_model(telegram_data['sender_id'], db)
        elif telegram_data['data'] in 'dolly_model':
            model_ = await set_user_dolly_model(telegram_data['sender_id'], db)
        elif telegram_data['data'] in 'gpt2_model':
            model_ = await set_user_gpt2_model(telegram_data['sender_id'], db)

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

    # admin_panel
    if telegram_data['is_data'] and telegram_data['data'] in ['admin_panel_users', 'admin_panel_us_file', 'admin_panel_users_query']:
        first_text = ''
        result = ''
        if telegram_data['data'] in 'admin_panel_users':
            first_text = 'Користувачі'
            result = await admin_panel_users_in_db(db)
        elif telegram_data['data'] in 'admin_panel_us_file':
            first_text = 'Документи користувачів'
            result = await admin_panel_users_file_in_db(db)
        elif telegram_data['data'] in 'admin_panel_users_query':
            result = await admin_panel_users_query(telegram_data, db)
            if result:
                return True

        payload = {
                'chat_id': telegram_data['sender_id'],
                'text': f'{first_text}:\n {result}'
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
            elif model == "gpt2":
                print('gpt2')
                qa = create_gpt2_conversation()
                q_text = qa({'question': telegram_data['text'], 'chat_history': {}})

        except Exception as e:
            print('exception')
            q_text = {'answer': e}

        await create_query(telegram_data['sender_id'], telegram_data['text'], q_text['answer'], db)

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
        {"command": "/delete_all_pdf", "description": "Видалити всі ПДФ"},
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

            with open(local_file_path, 'wb') as file:
                file.write(response.content)
                file.close()
            await create_index(local_file_path, sender_id=telegram_data['sender_id'], file_name=telegram_data['text'], db=db)
            # Create  doc in postgres database

            os.unlink(local_file_path)

    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': 'Файл прийнято, задавайте Ваше питання'
    }

    return payload, 'SendMessage'


async def choose_pdf(telegram_data: dict, db: Session) -> tuple:
    user_documents = await get_user_documents(telegram_data['sender_id'], db)
    # Підготовка відповіді для користувача
    if len(user_documents):
        response_text = ''
    #     list_of_users_doc = []
        for user_doc in user_documents:
    #        list_of_users_doc.append([{'text': user_doc.name, 'callback_data': 'doc_id'+user_doc.id}])
    #    keyboard = {'inline_keyboard': list_of_users_doc}
    #    keyboard_json = json.dumps(keyboard)

    #    payload = {
    #        'chat_id': telegram_data['sender_id'],
    #        'text': f'Ваші документи. Для того щоб вкажіть номер:',
    #        'reply_markup': keyboard_json
    #    }

    #    return payload, 'SendMessage'
            response_text += "".join(user_doc.name)
            response_text += '\n'
    else:
        # Якщо документів немає, повідомляємо користувачеві про це
        response_text = "У вас немає збережених документів."
    # Підготовка відповіді для відправки користувачеві
    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': response_text
    }

    return payload, 'SendMessage'


async def choose_model(telegram_data: dict, db: Session) -> tuple:
    user_model = await get_user_model(telegram_data['sender_id'], db)
    keyboard = {
        'inline_keyboard': [
            [{'text': 'Falcon', 'callback_data': 'falcon_model'}],
            [{'text': 'Dolly', 'callback_data': 'dolly_model'}],
            [{'text': 'GPT2', 'callback_data': 'gpt2_model'}],
        ]
    }

    keyboard_json = json.dumps(keyboard)

    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': f'Зараз активна модель: {user_model}. Для того щоб змінити оберіть модель нижче:',
        'reply_markup': keyboard_json
    }

    return payload, 'SendMessage'


async def admin_panel(telegram_data: dict, db: Session) -> tuple:
    user_admin = await get_user_admin(telegram_data['sender_id'], db)

    if not user_admin:
        payload = {
            'chat_id': telegram_data['sender_id'],
            'text': f'Ви не адмін. Доступ забаронений.',
        }
        return payload, 'SendMessage'

    keyboard = {
        'inline_keyboard': [
            [{'text': 'Користувачі', 'callback_data': 'admin_panel_users'}],
            [{'text': 'Файли користувачів', 'callback_data': 'admin_panel_us_file'}],
            [{'text': 'Запити користувачів', 'callback_data': 'admin_panel_users_query'}],
        ]
    }

    keyboard_json = json.dumps(keyboard)

    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': f'Адмін панель. Ви можете скористатися командами нижче:',
        'reply_markup': keyboard_json
    }

    return payload, 'SendMessage'


async def helps(telegram_data: dict, db: Session) -> tuple:
    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': 'Для початку необхідно відправити пдф файл. Після чого можна задавати питання по його змістом. Просто!'
    }

    return payload, 'SendMessage'


async def delete_all_pdf(telegram_data: dict, db: Session) -> tuple:

    payload = {
        'chat_id': telegram_data['sender_id'],
        'text': 'Ваші файли видалено з бази данних'
    }

    return payload, 'SendMessage'


MESSAGE_COMMAND = {
    '/start': start,
    '/choose_model': choose_model,
    '/choose_pdf': choose_pdf,
    '/delete_all_pdf': delete_all_pdf,
    '/helps': helps,
    '/admin_panel': admin_panel,
}
