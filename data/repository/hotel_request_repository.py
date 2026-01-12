from typing import List

from fastapi import HTTPException
from sqlalchemy import insert, select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.hotel_request_model import HotelRequestModel
from data.model.pilgrim_data_model import PilgrimDataModel


async def create_hotel_request(db: AsyncSession, request_dict : dict):
    try:
        stmt = insert(HotelRequestModel).values(**request_dict).returning(HotelRequestModel)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error Creating Hotel Request")

async def get_hotel_requests(db: AsyncSession, agency_name: List[str]):
    try:
        stmt = select(HotelRequestModel).where(HotelRequestModel.agency_name.in_(agency_name)).order_by(HotelRequestModel.id.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e

async def get_hotel_request_by_id(db:AsyncSession, request_id:int):
    try:
        stmt = select(HotelRequestModel).where(HotelRequestModel.id == request_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e

async def update_hotel_request(db:AsyncSession, request_dict: dict):
    try:
        stmt = (update(HotelRequestModel)
                .where(HotelRequestModel.id == request_dict['id'])
                .values(**request_dict)
                .returning(HotelRequestModel))
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_hotel_request(db:AsyncSession, request_id:int):
    try:
        stmt = delete(HotelRequestModel).where(HotelRequestModel.id == request_id)
        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e

async def get_madinah_allocated_and_total_seat(db:AsyncSession, agency_name:str):
    try:
        # Query 1: Allocated Hotel Seat
        hotel_stmt = (
            select(
                HotelRequestModel.city,
                HotelRequestModel.agency_name,
                func.sum(HotelRequestModel.number_of_haji).label("hotel_allocated_hajji")
            )
            .where(
                HotelRequestModel.city == "Madinah",
                HotelRequestModel.agency_name == agency_name
            )
            .group_by(
                HotelRequestModel.city,
                HotelRequestModel.agency_name
            )
        )

        hotel_result = await db.execute(hotel_stmt)
        hotel_row = hotel_result.first()

        # Query 2: Total pilgrims
        pilgrim_stmt = (
            select(
                PilgrimDataModel.group_name,
                func.count(PilgrimDataModel.tracking_id).label("total_pilgrims")
            )
            .where(PilgrimDataModel.group_name == agency_name)
            .group_by(PilgrimDataModel.group_name)
        )

        pilgrim_result = await db.execute(pilgrim_stmt)
        pilgrim_row = pilgrim_result.first()

        # Build JSON-safe response
        return {
            "city": hotel_row.city if hotel_row else "Madinah",
            "agency_name": agency_name,
            "hotel_allocated_hajji": hotel_row.hotel_allocated_hajji if hotel_row else 0,
            "total_pilgrims": pilgrim_row.total_pilgrims if pilgrim_row else 0
        }

    except Exception as e:
        raise e


async def cancel_hotel_request(db:AsyncSession, request_dict : dict):
    try:
        stmt = (update(HotelRequestModel)
                .where(HotelRequestModel.id == request_dict['id'])
                .values(**request_dict)
                .returning(HotelRequestModel))
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e