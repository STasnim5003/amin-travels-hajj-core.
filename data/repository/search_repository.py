from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.pilgrim_data_model import PilgrimDataModel


async def search_pilgrim_by_any_field(
        db: AsyncSession, search_term: str, agency_name: str | None = None
):
    try:
        search_fields = [
            PilgrimDataModel.tracking_id,
            PilgrimDataModel.nid,
            PilgrimDataModel.mobile_no,
            PilgrimDataModel.passport_no,
            PilgrimDataModel.name_en,
        ]

        for field in search_fields:
            if field == PilgrimDataModel.name_en:
                stmt = select(PilgrimDataModel).where(field.ilike(f"%{search_term}%"))
            else:
                stmt = select(PilgrimDataModel).where(field == search_term)

            if agency_name:
                stmt = stmt.where(PilgrimDataModel.group_name == agency_name)

            result = await db.execute(stmt)
            pilgrims = result.scalars().all()

            if pilgrims:
                return pilgrims

        return []

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error searching pilgrim: {str(e)}")
