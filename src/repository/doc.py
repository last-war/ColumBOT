from sqlalchemy.orm import Session
from src.repository.users import get_user_by_user_id

from src.database.models import Doc


async def get_user_documents(chat_id: int, db: Session) -> list:
    user_documents = []
    if chat_id:
        # Ваш SQL-запит для отримання документів користувача
        query = f"SELECT document_name FROM user_documents WHERE user_id = {chat_id}"
        try:
            with db as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                user_documents = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print('Помилка при отриманні документів:', str(e))
    return user_documents


async def get_doc_by_id(doc_id: int, db: Session) -> Doc | None:
    return db.query(Doc).filter_by(id=doc_id).first()


async def create_doc(user_id, file_name, text, db: Session) -> Doc:
    new_doc = Doc()
    new_doc.user = await get_user_by_user_id(user_id, db)
    new_doc.name = file_name
    new_doc.description = text
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc
