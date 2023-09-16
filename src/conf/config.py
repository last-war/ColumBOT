from pydantic import BaseSettings


class Settings(BaseSettings):
    telegram_token: str = "token"
    base_url: str = "url"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
