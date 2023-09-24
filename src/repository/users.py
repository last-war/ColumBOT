from typing import Type

from sqlalchemy.orm import Session

from src.database.models import User, Model
from src.schemas.users import UserModel


async def get_user_by_user_id(user_id: int, db: Session) -> User | None:
    return db.query(User).filter_by(user_id=user_id).first()


async def create_user(body: UserModel, db: Session) -> User:

    new_user = User(**body.dict())
    new_user.model = Model.falcon
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def get_use_docs(user_id: int, db: Session) -> bool:
    user = db.query(User).filter_by(user_id=user_id).first()
    return user.use_docs


async def user_add_use_docs(user_id: int, doc_id: int, db: Session) -> Type[User]:
    user = db.query(User).filter_by(user_id=user_id).first()
    user.use_docs.append(doc_id)
    db.commit()
    db.refresh(user)
    return user


async def set_user_falcon_model(user_id: int, db: Session) -> Model:
    user = await get_user_by_user_id(user_id, db)
    user.model = Model.falcon
    db.commit()
    db.refresh(user)
    return user.model


async def set_user_dolly_model(user_id: int, db: Session) -> Model:
    user = await get_user_by_user_id(user_id, db)
    user.model = Model.dolly
    db.commit()
    db.refresh(user)
    return user.model


async def set_user_openai_model(user_id: int, db: Session) -> Model:
    user = await get_user_by_user_id(user_id, db)
    user.model = Model.openai
    db.commit()
    db.refresh(user)
    return user.model


async def get_user_model(user_id: int, db: Session) -> str:
    user = await get_user_by_user_id(user_id, db)
    model_name = user.model.name
    return model_name


async def get_user_admin(user_id: int, db: Session) -> bool:
    user = await get_user_by_user_id(user_id, db)
    if user:
        if user.user_is_admin:
            return True

    return False
