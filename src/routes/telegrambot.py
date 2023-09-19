from fastapi import APIRouter, Request

from src.services.telegrambot import set_webhook, bot_logic
from src.services.utils import process_telegram_data

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post('/bot')
async def telegram(request: Request):
    try:
        body = await request.json()
        telegram_data = process_telegram_data(body)
        rez = await bot_logic(telegram_data)
        if rez:
            return 'OK', 200
    except Exception as e:
        print('Error at telegram...')
        print(e)
        return 'BAD REQUEST', 400


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
