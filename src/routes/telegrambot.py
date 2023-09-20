from fastapi import APIRouter, Request, HTTPException, status, Depends

from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas.telegrambot import WebhookModel
from src.services.telegrambot import set_webhook, bot_logic
from src.services.utils import process_telegram_data

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post('/bot')
async def telegram(request: Request,
                   db: Session = Depends(get_db)):
    try:
        body = await request.json()
        telegram_data = process_telegram_data(body)
        rez = await bot_logic(telegram_data, db)
        if rez:
            return 'OK', 200
    except Exception as e:
        print('Error at telegram...')
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HTTP_400_BAD_REQUEST")


@router.post('/set-telegram-webhook')
async def set_telegram_webhook(body: WebhookModel):
    try:
        # body = await request.json()
        flag = await set_webhook(body.ngrok_url, body.secret_token)
        if flag:
            return 'OK', 200
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HTTP_400_BAD_REQUEST")
    except Exception as e:
        print('Error at set_telegram_webhook...')
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HTTP_400_BAD_REQUEST")
