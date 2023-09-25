# Використовуємо офіційний образ Python з Docker Hub
FROM python:3.10.12

# Змінні оточення
ENV TELEGRAM_TOKEN="${TELEGRAM_TOKEN}"
ENV BASE_URL="${BASE_URL}"

ENV HF_API_KEY="${HF_API_KEY}"

ENV DB_DIR="${DB_DIR}"
ENV INPUT_FILE_PATH="${INPUT_FILE_PATH}"
ENV OUTPUT_DIR="${OUTPUT_DIR}"

ENV POSTGRES_DB="${POSTGRES_DB}"
ENV POSTGRES_USER="${POSTGRES_USER}"
ENV POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"
ENV POSTGRES_PORT="${POSTGRES_PORT}"
ENV POSTGRES_DOMAIN="${POSTGRES_DOMAIN}"
ENV DATABASE_URL="${DATABASE_URL}"

# Встановлюємо додаткові пакети або бібліотеки (якщо потрібно)
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt install nano iproute2 telnet git -y

# Створюємо папку для проекту
RUN mkdir -p /app

RUN pip install --upgrade pip

# Клонуємо репозиторій з GitHub (замініть URL на URL вашого репозиторію)
RUN git clone https://github.com/last-war/ColumBOT /app

# Переходимо в каталог з клонованим репозиторієм
WORKDIR /app

# Переключаємося на певну гілку (замініть 'yourbranch' на назву гілки)
RUN git checkout docker_hub

# Встановлюємо залежності з requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Port
EXPOSE 8000

# Встановлюємо ENTRYPOINT
#ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD alembic upgrade head && uvicorn main:app --host localhost --port 8000 --reload