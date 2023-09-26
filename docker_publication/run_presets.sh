#!/bin/bash

# Вставляємо змінні з файлу .env
if [ -f .env ]; then
  source .env
fi

# Запустити компосе
docker-compose up -d

# примінити міграції
docker-compose exec postgres sh -c "alembic upgrade heads"

# install ngrok
snap install ngrok

# add key in ngrok authorization
sudo ngrok config add-authtoken "$NG_ROCK_KEY"

# start ngrok
ngrok http 8000