from fastapi import FastAPI

from src.conf.config import settings
from src.routes import telegrambot
from src.services.telegrambot import create_command_menu

telegram_token = settings.telegram_token

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI!"}


@app.get("/settings")
def settings():
    result = create_command_menu()
    if result:
        return {"message": "Create menu"}
    else:
        return {"message": "Do not create menu"}


app.include_router(telegrambot.router, prefix='/api')
