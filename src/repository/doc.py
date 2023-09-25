from typing import List, Type

from sqlalchemy.orm import Session
from src.repository.users import get_user_by_user_id

from src.database.models import Doc
from src.schemas.doc import DocResponse


async def get_user_documents(user_id: int, db: Session) -> List[DocResponse]:
    user = await get_user_by_user_id(user_id, db)
    docs = db.query(Doc).filter_by(user_id=user.id).limit(5).all()
    result = []
    for doc in docs:
        doc_resp = DocResponse(
            id=doc.id,
            user_id=doc.user_id,
            name=doc.name
        )
        result.append(doc_resp)

    return result


async def get_all_doc(db: Session) -> List[DocResponse]:
    docs = db.query(Doc).all()
    result = []
    for doc in docs:
        doc_resp = DocResponse(
            id=doc.id,
            user_id=doc.user_id,
            name=doc.name
        )
        result.append(doc_resp)

    return result


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
