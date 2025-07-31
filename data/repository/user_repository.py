from logging import setLoggerClass
import logging
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.user_model import UserModel
from infrastructure.schema.user_schema import UserBaseSchema, UserResponseSchema


async def insert_user(user: UserBaseSchema, db: AsyncSession) -> UserResponseSchema:
    user_data = user.model_dump(by_alias=False, exclude_unset=True, exclude_none=True)
    query = insert(UserModel).values(**user_data).returning(UserModel)
    try:
        result = await db.execute(query)
        await db.commit()

        row = result.fetchone()
        if row is None:
            raise ValueError("User insertion failed. No row returned.")

        user_model_instance = row._mapping['UserModel']
        return UserResponseSchema.model_validate(user_model_instance.__dict__)

    except Exception as e:
        await db.rollback()
        logging.error("Error : ", str(e))
        raise

async def get_users(db: AsyncSession, name: str = None, whats_app_no: str = None):
    try:
        query = select(UserModel)
        if name:
            query = query.where(UserModel.name == name)
        if whats_app_no:
            query = query.where(UserModel.whats_app_no == whats_app_no)
        result = await db.execute(query)
        result = result.scalars().all()
        user_responses = []
        for user in result:
            user_responses.append(UserResponseSchema.model_validate(user).model_dump())
        return user_responses
    except Exception as e:
        await db.rollback()
        logging.error("Error : ", str(e))
        raise