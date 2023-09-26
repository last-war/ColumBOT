from typing import Type

from pydantic import BaseModel, Field
from sqlalchemy.types import ARRAY

from src.database.models import Model


class UserModel(BaseModel):
    user_id: str = Field()
    is_bot: bool
    first_name: str = Field()
    username: str = Field()


class UserResponse(BaseModel):
    user_id: str = Field()
    is_bot: bool
    first_name: str = Field()
    username: str = Field()
    model: Type[Model]
    use_docs: Type[ARRAY]

    class Config:
        orm_mode = True
