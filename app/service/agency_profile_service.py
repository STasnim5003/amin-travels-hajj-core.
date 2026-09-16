from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import agency_profile_repository
from infrastructure.schema.agency_profile_schema import AgencyProfileItemSchema, AgencyProfileListResponseSchema


async def get_agency_profiles(db: AsyncSession) -> AgencyProfileListResponseSchema:
    try:
        rows = await agency_profile_repository.get_all_agency_profiles(db)
        data = [AgencyProfileItemSchema.model_validate(row) for row in rows]
        return AgencyProfileListResponseSchema(success=True, count=len(data), data=data)
    except Exception as e:
        raise e
