import logging

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.training_user_model import TrainingUserModel
from infrastructure.schema.training_schema import TrainingUserBaseSchema, TrainingUserResponseSchema


async def insert_training_user(training_user: TrainingUserBaseSchema, db: AsyncSession) -> TrainingUserResponseSchema:
    user_data = training_user.model_dump(exclude_unset=True, exclude_none=True)
    query = insert(TrainingUserModel).values(**user_data).returning(TrainingUserModel)
    try:
        result = await db.execute(query)
        await db.commit()

        row = result.fetchone()
        if row is None:
            raise ValueError("User insertion failed. No row returned.")

        user_model_instance = row._mapping['TrainingUserModel']
        return TrainingUserResponseSchema.model_validate(user_model_instance.__dict__)

    except Exception as e:
        await db.rollback()
        logging.error("Error : ", str(e))
        raise