from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.script_model import AgencyHajjiCountFetchModel



async def agency_hajji_count(db: AsyncSession):
    try:
        query = select(AgencyHajjiCountFetchModel)
        result = await db.execute(query)
        rows =  result.scalars().all()
        return rows
    except Exception as e:
        await db.rollback()
        raise e