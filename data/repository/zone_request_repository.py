from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.zone_request_model import ZoneRequestModel


async def create(db: AsyncSession, data: dict):
    try:
        new_zone_request = ZoneRequestModel(**data)
        db.add(new_zone_request)
        await db.commit()
        await db.refresh(new_zone_request)
        return new_zone_request
    except Exception as e:
        await db.rollback()
        raise e


async def get_by_id(db: AsyncSession, zone_request_id: int, agency_name: str):
    try:
        result = await db.execute(
            select(ZoneRequestModel).where(
                ZoneRequestModel.id == zone_request_id,
                ZoneRequestModel.agency_name == agency_name
            )
        )
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def update_zone_request(db: AsyncSession, zone_request_id: int, data: dict):
    try:
        stmt = (
            update(ZoneRequestModel)
            .where(ZoneRequestModel.id == zone_request_id)
            .values(**data)
            .returning(ZoneRequestModel)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_all_zone_requests(db: AsyncSession, agency_names: list):
    try:
        stmt = select(ZoneRequestModel).where(ZoneRequestModel.agency_name.in_(agency_names))
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e

async def delete_zone_request(db: AsyncSession, zone_request_id: int, agency_name: str) -> bool:
    try:
        # Check if the zone request exists
        result = await db.execute(
            select(ZoneRequestModel).where(
                ZoneRequestModel.id == zone_request_id,
                ZoneRequestModel.agency_name == agency_name
            )
        )
        zone_request = result.scalar_one_or_none()
        if not zone_request:
            return False

        # Delete the zone request
        await db.execute(
            delete(ZoneRequestModel).where(
                ZoneRequestModel.id == zone_request_id,
                ZoneRequestModel.agency_name == agency_name
            )
        )
        await db.commit()
        return True

    except Exception as e:
        await db.rollback()
        raise e
