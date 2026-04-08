from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from data.model.umrah_hotel_booking_model import UmrahHotelBooking


async def create_umrah_hotel_booking(db: AsyncSession, request_dict: dict):
    try:
        stmt = (
            insert(UmrahHotelBooking)
            .values(**request_dict)
            .returning(UmrahHotelBooking)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e

async def get_umrah_hotel_booking(db:AsyncSession, agency_name:str):
    try:
        stmt = (
            select(UmrahHotelBooking)
            .where(
                UmrahHotelBooking.agency_name == agency_name
            )
            .order_by(UmrahHotelBooking.id.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e

async def get_umrah_hotel_booking_by_id(db:AsyncSession, hotel_booking_id:int):
    try:
        stmt = (
            select(UmrahHotelBooking)
            .where(UmrahHotelBooking.id == hotel_booking_id)
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e

async def update_umrah_hotel_booking(db:AsyncSession, request_dict:dict):
    try:
        stmt = (
            update(UmrahHotelBooking)
            .values(**request_dict)
            .where(UmrahHotelBooking.id == request_dict['id'])
            .returning(UmrahHotelBooking)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e

async def delete_umrah_hotel_booking(db:AsyncSession, hotel_booking_id:int):
    try:
        stmt = (
            delete(UmrahHotelBooking)
            .where(UmrahHotelBooking.id == hotel_booking_id)
        )
        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e