from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.agency_profile_model import AgencyProfileModel


async def get_all_agency_profiles(db: AsyncSession):
    try:
        stmt = select(AgencyProfileModel).order_by(AgencyProfileModel.sl_no)
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e
