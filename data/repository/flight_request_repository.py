from sqlalchemy import update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.flight_request_model import FlightRequestModel


async def create(db: AsyncSession, data: dict):
    try:
        new_flight = FlightRequestModel(**data)
        db.add(new_flight)
        await db.commit()
        await db.refresh(new_flight)
        return new_flight
    except Exception as e:
        await db.rollback()
        raise e

async def get_by_id(db:AsyncSession, flight_request_id:int, agency_name:str):
    try:
        result = await db.execute(
            select(FlightRequestModel).where(FlightRequestModel.id == flight_request_id, FlightRequestModel.agency_name==agency_name)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        raise e

async def update_flight_request(db: AsyncSession, flight_request_id: int, data: dict):
    try:
        stmt = (
            update(FlightRequestModel)
            .where(FlightRequestModel.id == flight_request_id)
            .values(**data)
            .returning(FlightRequestModel)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_all_flight_requests(db, agency_name):
    try:
        stmt = (
            select(FlightRequestModel)
            .where(FlightRequestModel.agency_name==agency_name)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e

async def delete_flight_request(db: AsyncSession, flight_request_id: int, agency_name: str) -> bool:
    try:
        # Check if the flight request exists
        result = await db.execute(
            select(FlightRequestModel).where(
                FlightRequestModel.id == flight_request_id,
                FlightRequestModel.agency_name == agency_name
            )
        )
        flight_request = result.scalar_one_or_none()
        if not flight_request:
            return False

        # Delete the flight request
        await db.execute(
            delete(FlightRequestModel).where(
                FlightRequestModel.id == flight_request_id,
                FlightRequestModel.agency_name == agency_name
            )
        )
        await db.commit()
        return True

    except Exception as e:
        await db.rollback()
        raise e