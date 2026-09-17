import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.service import agency_profile_service
from data.db.db_config import get_async_db
from infrastructure.schema.agency_profile_schema import AgencyProfileListResponseSchema

public_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@public_router.get("/agency-profile", response_model=AgencyProfileListResponseSchema, tags=["agency-profile"])
async def get_agency_profile(
        db: AsyncSession = Depends(get_async_db)
) -> AgencyProfileListResponseSchema:
    return await agency_profile_service.get_agency_profiles(db)
