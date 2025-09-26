from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import view_field_repository
from infrastructure.schema.view_field_schema import ViewFieldSchema, ViewFieldResponseSchema, \
    ViewFieldListResponseSchema


async def create_view(db:AsyncSession, request_body : ViewFieldSchema, username:str):
    try:
        new_view = await view_field_repository.create_view(db, request_body, username)
        return ViewFieldResponseSchema.model_validate(new_view)
    except Exception as e:
        raise e

async def get_views(db: AsyncSession, username : str) -> ViewFieldListResponseSchema:
    try:
        result = await view_field_repository.get_views(db, username)
        return ViewFieldListResponseSchema(data = result)
    except Exception as e:
        raise e

