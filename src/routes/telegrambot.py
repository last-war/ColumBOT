from fastapi import APIRouter, Request

from src.services.telegrambot import set_webhook, send_message

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post('/bot')
async def telegram(request: Request):
    try:
        body = await request.json()
        print(body)
        sender_id = body['message']['from']['id']
        query = body['message']['text']
        send_message(sender_id, query)
        return 'OK', 200
    except Exception as e:
        print('Error at telegram...')
        print(e)
        return 'OK', 200


@router.post('/set-telegram-webhook')
async def set_telegram_webhook(request: Request):
    try:
        body = await request.json()
        flag = set_webhook(body['url'], body['secret_token'])
        if flag:
            return 'OK', 200
        else:
            return 'BAD REQUEST', 400
    except Exception as e:
        print('Error at set_telegram_webhook...')
        print(e)
        return 'BAD REQUEST', 400
