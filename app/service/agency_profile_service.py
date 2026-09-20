from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import agency_profile_repository
from infrastructure.schema.agency_profile_schema import (
    AgencyProfileItemSchema,
    AgencyProfileListResponseSchema,
    QuotaSummarySchema,
)

ORIGINAL_PILGRIM_QUOTA = 2669
GUIDE_QUOTA = 61


async def get_agency_profiles(db: AsyncSession) -> AgencyProfileListResponseSchema:
    try:
        rows = await agency_profile_repository.get_all_agency_profiles(db)
        data = [AgencyProfileItemSchema.model_validate(row) for row in rows]

        registration_done = sum(item.reg or 0 for item in data)
        summary = QuotaSummarySchema(
            original_pilgrim_quota=ORIGINAL_PILGRIM_QUOTA,
            guide_quota=GUIDE_QUOTA,
            total_quota=ORIGINAL_PILGRIM_QUOTA + GUIDE_QUOTA,
            current_pilgrim_registration_done=registration_done,
            remaining_pilgrim_balance=ORIGINAL_PILGRIM_QUOTA - registration_done,
        )
        return AgencyProfileListResponseSchema(success=True, count=len(data), summary=summary, data=data)
    except Exception as e:
        raise e
