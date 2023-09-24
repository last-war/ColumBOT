from typing import Type

from pydantic import BaseModel, Field
from sqlalchemy.types import ARRAY

from src.database.models import Model
import os


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
        

async def delete_user_documents(user_id: int, db: Session) -> None:
    # Знаходимо користувача
    user = db.query(User).filter_by(user_id=user_id).first()
    
    if user:
        # Отримуємо список обраних документів користувача
        user_documents = db.query(Document).filter(Document.id.in_(user.use_docs)).all()
        
        # Видаляємо файли з системи та бази даних
        for document in user_documents:
            file_path = os.path.join(settings.output_dir, document.file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
            db.delete(document)
        
        # Очищуємо список обраних документів користувача
        user.use_docs = []
        db.commit()
