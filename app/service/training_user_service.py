from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import training_user_repository
from infrastructure.schema.training_schema import TrainingUserBaseSchema, TrainingUserResponseSchema, \
    PaginatedTrainingUserResponseSchema


async def create_training_user(training_user_request_schema: TrainingUserBaseSchema,
                               db: AsyncSession) -> TrainingUserResponseSchema:
    result = await training_user_repository.insert_training_user(training_user_request_schema, db=db)
    return result


async def fetch_training_users(
        db: AsyncSession,
        name: Optional[str],
        whats_app_no: Optional[str],
        page: int,
        limit: int
) -> PaginatedTrainingUserResponseSchema:
    skip = (page - 1) * limit
    users, total = await training_user_repository.get_training_users(db, name, whats_app_no, skip, limit)

    return PaginatedTrainingUserResponseSchema(
        users=users,
        total=total,
        page=page,
        limit=limit
    )
