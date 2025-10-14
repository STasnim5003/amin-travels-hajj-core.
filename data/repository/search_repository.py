from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.pilgrim_data_model import PilgrimDataModel


async def search_pilgrim_by_any_field(db: AsyncSession, search_term: str, agency_name : str | None = None):
    try:
        filters = or_(
            PilgrimDataModel.tracking_id == search_term,
            PilgrimDataModel.nid == search_term,
            PilgrimDataModel.mobile_no == search_term,
            PilgrimDataModel.passport_no == search_term
        )

        # If agency_name is provided, combine with group_name filter
        if agency_name:
            filters = and_(filters, PilgrimDataModel.group_name == agency_name)

        stmt = select(PilgrimDataModel).where(filters)

        result = await db.execute(stmt)
        pilgrims = result.scalars().all()
        return pilgrims

    except Exception as e:
        await db.rollback()
        raise Exception(f"Error searching pilgrim: {str(e)}")