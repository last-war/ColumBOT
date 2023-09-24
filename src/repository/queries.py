from sqlalchemy.orm import Session
from src.repository.users import get_user_by_user_id
from src.database.models import Query


async def get_user_queries(chat_id: int, db: Session) -> list:
    user = await get_user_by_user_id(chat_id, db)
    return db.query(Query).filter_by(user_id=user.id).all()


async def get_query_by_id(query_id: int, db: Session) -> Query | None:
    return db.query(Query).filter_by(id=query_id).first()


async def create_query(user_id, query_text, query_answer, db: Session) -> Query:
    new_query = Query()
    new_query.user = await get_user_by_user_id(user_id, db)
    new_query.query_text = query_text
    new_query.query_answer = query_answer
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    return new_query
