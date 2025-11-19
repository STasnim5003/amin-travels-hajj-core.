from typing import List

from fastapi import HTTPException
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.hotel_request_model import HotelRequestModel


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

async def get_hotel_request_by_id(db:AsyncSession, request_id:int, agency_name:str):
    try:
        stmt = select(HotelRequestModel).where(HotelRequestModel.id == request_id, HotelRequestModel.agency_name == agency_name)
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
