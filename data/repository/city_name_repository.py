from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.city_name_model import CityNameModelForUmrah


async def create_city_name(db:AsyncSession, request_dict:dict):
    try:
        stmt = insert(CityNameModelForUmrah).values(**request_dict).returning(CityNameModelForUmrah)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_city_names(db:AsyncSession, agency_name:str):
    try:
        result = await db.execute(
            select(CityNameModelForUmrah).where(CityNameModelForUmrah.agency_name == agency_name, CityNameModelForUmrah.is_active == True)
        )
        return result.scalars().all()
    except Exception as e:
        raise e