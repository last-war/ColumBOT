from pydantic import BaseSettings


class Settings(BaseSettings):
    _ai_api_key: str = "AI_API_KEY"
    telegram_token: str = "TELE"
    base_url: str = "http://"
    db_dir: str = 'data/db'  # Директорія для бази даних
    input_file_path: str = 'data/input/sample.pdf'  # Шлях до вхідного PDF-файлу
    output_dir: str = 'data/output'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
