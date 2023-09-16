from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.conf.config import settings
from src.routes import telegrambot

telegram_token = settings.telegram_token

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI!"}


app.include_router(telegrambot.router, prefix='/api')
