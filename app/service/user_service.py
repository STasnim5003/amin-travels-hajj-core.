from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile

from data.repository import user_repository, file_repository
from infrastructure.schema.user_schema import UserBaseSchema, UserResponseSchema


async def create_user(user_request_schema: UserBaseSchema, db: AsyncSession, nid:List[UploadFile]) -> UserResponseSchema:
    nid_images = []
    for pic in nid:
       nid_images.append(await file_repository.upload_file(file=pic, name="users"))

    user_request_schema.nid_images = nid_images
    result = await user_repository.insert_user(user_request_schema, db=db)
    return result


async def get_users( db: AsyncSession, name:str=None, whats_app_no: str=None, search: str=None) -> List[UserResponseSchema]:
    result = await user_repository.get_users(name=name, whats_app_no=whats_app_no,search=search, db=db)
    return result


async def update_user(id, payment_status, db):
    result = await user_repository.update_user(id=id, payment_status=payment_status, db=db)
    return result