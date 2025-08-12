import logging
from typing import Optional

from sqlalchemy import insert, select, func
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


async def get_training_users(db: AsyncSession,
                             name: Optional[str] = None,
                             whats_app_no: Optional[str] = None,
                             skip: int = 0,
                             limit: int = 10,
                             ):
    query = select(TrainingUserModel)

    if name:
        query = query.where(TrainingUserModel.name.ilike(f"%{name}%"))
    if whats_app_no:
        query = query.where(TrainingUserModel.whats_app_no.ilike(f"%{whats_app_no}%"))

    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()

    result = await db.execute(query.offset(skip).limit(limit))
    users = result.scalars().all()

    return users, total
