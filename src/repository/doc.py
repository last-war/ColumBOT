from sqlalchemy.orm import Session
from src.repository.users import get_user_by_user_id

from src.database.models import Doc


async def get_doc_by_id(doc_id: int, db: Session) -> Doc | None:
    return db.query(Doc).filter_by(id=doc_id).first()



async def create_doc(user_id, db: Session) -> Doc:

    new_doc = Doc()
    new_doc.user_id = get_user_by_user_id(user_id, db)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc
