from pydantic import BaseModel, Field


class WebhookModel(BaseModel):
    ngrok_url: str = Field()
    secret_token: str = Field()


class WebhookResponse(BaseModel):
    result: bool
