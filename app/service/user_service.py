from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import user_repository
from infrastructure.schema.user_schema import UserBaseSchema, UserResponseSchema


async def create_user(user_request_schema: UserBaseSchema, db: AsyncSession) -> UserResponseSchema:
    result = await user_repository.insert_user(user_request_schema, db=db)
    return result


async def get_users( db: AsyncSession, name:str=None, whats_app_no: str=None) -> List[UserResponseSchema]:
    result = await user_repository.get_users(name=name, whats_app_no=whats_app_no, db=db)
    return result