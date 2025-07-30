from sqlalchemy.ext.asyncio import AsyncSession

from data.repository.user_repository import insert_user
from infrastructure.schema.user_schema import UserBaseSchema, UserResponseSchema


async def create_user(user_request_schema: UserBaseSchema, db: AsyncSession) -> UserResponseSchema:
    result = await insert_user(user_request_schema, db=db)
    return result
