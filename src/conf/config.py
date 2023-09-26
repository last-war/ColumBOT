from pydantic import BaseSettings


class Settings(BaseSettings):
    hf_api_key: str = "hf_"
    telegram_token: str = "TELE"
    base_url: str = "http://"
    db_dir: str = 'data/db'  # Директорія для бази даних
    input_file_path: str = 'data/input/sample.pdf'  # Шлях до вхідного PDF-файлу
    output_dir: str = 'data/output'
    database_url: str = 'postgresql+psycopg2://user:password@server:5432/database'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
