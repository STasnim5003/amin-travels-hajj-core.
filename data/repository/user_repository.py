from logging import setLoggerClass
import logging
from sqlalchemy import insert, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.package_model import PackageModel
from data.model.user_model import UserModel
from infrastructure.schema.package_schema import PackageResponseSchema
from infrastructure.schema.user_schema import UserBaseSchema, UserResponseSchema


async def insert_user(user: UserBaseSchema, db: AsyncSession) -> UserResponseSchema:
    user_data = user.model_dump(exclude_unset=True, exclude_none=True)
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

async def get_users(db: AsyncSession, name: str = None, whats_app_no: str = None, search: str = None,):
    try:
        query = select(UserModel, PackageModel).join(PackageModel).where(PackageModel.id == UserModel.package_id)

        if name:
            query = query.where(UserModel.name == name)

        if whats_app_no:
            query = query.where(UserModel.whats_app_no == whats_app_no)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    UserModel.name.ilike(search_term),
                    UserModel.whats_app_no.ilike(search_term)
                )
            )

        result = await db.execute(query)
        response = result.all()

        return get_user_response_schema(response)
    except Exception as e:
        logging.error("Error : ", str(e))
        raise


def get_user_response_schema(responses):
    users_response = []
    for user, package in responses:
        package_schema = PackageResponseSchema.model_validate(package).model_dump()
        user_schema = UserResponseSchema.model_validate(user).model_dump()
        user_schema['package'] = package_schema
        users_response.append(user_schema)
    return users_response


