from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import training_user_repository
from infrastructure.schema.training_schema import TrainingUserBaseSchema, TrainingUserResponseSchema


async def create_training_user(training_user_request_schema: TrainingUserBaseSchema, db: AsyncSession) -> TrainingUserResponseSchema:
    result = await training_user_repository.insert_training_user(training_user_request_schema, db=db)
    return result