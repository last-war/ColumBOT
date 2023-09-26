#!/bin/bash

# Вставляємо змінні з файлу .env
source ./ColumBOT/.env

# install ngrok
snap install ngrok

# install alembic
pip install alembic

# Apply Alembic migrations
alembic upgrade heads

# add key in ngrok authorization
ngrok config add-authtoken "NG_ROCK_KEY is $NG_ROCK_KEY"

# start ngrok
ngrok http 8000

