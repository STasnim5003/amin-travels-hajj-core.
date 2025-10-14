from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import search_repository
from infrastructure.schema.pilgrim_data_schema import PilgrimDataResponseSchema


async def pilgrim_search_service(db: AsyncSession, search_term: str, agency_name: str | None = None):
    if not search_term:
        raise HTTPException(status_code=400, detail="Search term cannot be empty")

    pilgrims = await search_repository.search_pilgrim_by_any_field(db, search_term, agency_name)

    if not pilgrims:
        raise HTTPException(status_code=400, detail="No pilgrim found with given information")

    return [
        PilgrimDataResponseSchema.model_validate(p).model_dump(exclude={"password", "preliminary_password"})
        for p in pilgrims
    ]
