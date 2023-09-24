from io import BytesIO
from sqlalchemy.orm import Session

from src.repository.doc import get_user_documents, get_all_doc
from src.repository.users import get_all_users


async def save_image_in_ram(img):
    output = BytesIO()
    img.save(output)
    output.seek(0)
    return output


async def admin_panel_users_in_db(db: Session) -> str:
    result = ""

    users = await get_all_users(db)

    for user in users:
        result += f'user_id:{user.user_id}|username:{user.username} \n'

    return result


async def admin_panel_users_file_in_db(db: Session) -> str:
    result = ""

    users = await get_all_users(db)
    all_docs = await get_all_doc(db)

    for user in users:
        count_doc = []
        for doc in all_docs:
            if doc.user_id == user.id:
                count_doc.append(doc)
        result += f'user_id:{user.user_id}|user_doc:{len(count_doc)} \n'

    return result
