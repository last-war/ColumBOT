from datetime import datetime

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel


async def get_user_by_user_id(user_id: int, db: Session) -> User | None:
    return db.query(User).filter_by(user_id=user_id).first()


async def create_user(body: UserModel, db: Session) -> User:

    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
