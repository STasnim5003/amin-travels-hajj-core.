from sqlalchemy import insert
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
        print("Error : ", str(e))
        raise
