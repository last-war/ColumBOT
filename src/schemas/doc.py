from pydantic import BaseModel, Field


class DocResponse(BaseModel):
    id: int = Field()
    user_id: int = Field()
    name: str = Field()

    class Config:
        orm_mode = True
