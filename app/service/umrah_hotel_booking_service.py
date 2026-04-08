from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.repository import umrah_hotel_booking_repository
from infrastructure.schema.umrah_hotel_booking_schema import UmrahHotelBookingCreate, UmrahHotelBookingResponse, \
    UmrahHotelBookingUpdate


async def create_hotel_booking(db:AsyncSession, request: UmrahHotelBookingCreate, agency_name:str, username:str):
    try:
        request_dict = request.model_dump(exclude_none=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username

        result = await umrah_hotel_booking_repository.create_umrah_hotel_booking(db=db, request_dict=request_dict)
        return UmrahHotelBookingResponse.model_validate(result)
    except Exception as e:
        raise e

async def get_umrah_hotel_booking(db:AsyncSession, agency_name:str):
    try:
        result = await umrah_hotel_booking_repository.get_umrah_hotel_booking(db=db, agency_name=agency_name)
        return [UmrahHotelBookingResponse.model_validate(r) for r in result]
    except Exception as e:
        raise e

async def get_umrah_hotel_booking_by_id(db:AsyncSession, hotel_booking_id:int, agency_name:str):
    try:
        result = await check_hotel_booking(db=db, hotel_booking_id=hotel_booking_id, agency_name=agency_name)

        return UmrahHotelBookingResponse.model_validate(result)
    except Exception as e:
        raise e

async def update_umrah_hotel_booking(db:AsyncSession, request: UmrahHotelBookingUpdate, agency_name:str, username:str):
    try:
        await check_hotel_booking(db=db, hotel_booking_id=request.id, agency_name=agency_name)

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()

        result = await umrah_hotel_booking_repository.update_umrah_hotel_booking(db=db, request_dict=request_dict)
        return UmrahHotelBookingResponse.model_validate(result)
    except Exception as e:
        raise e

async def delete_umrah_hotel_booking(db:AsyncSession, hotel_booking_id:int, agency_name:str):
    try:
        await check_hotel_booking(db=db, hotel_booking_id=hotel_booking_id, agency_name=agency_name)

        return await umrah_hotel_booking_repository.delete_umrah_hotel_booking(db=db, hotel_booking_id=hotel_booking_id)
    except Exception as e:
        raise e

async def check_hotel_booking(db:AsyncSession, hotel_booking_id:int, agency_name:str):
    try:
        hotel_booking = await umrah_hotel_booking_repository.get_umrah_hotel_booking_by_id(db=db,
                                                                                           hotel_booking_id=hotel_booking_id)

        if not hotel_booking:
            raise HTTPException(status_code=400, detail="Hotel Booking Not Found")

        if hotel_booking.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Agency Name Mismatch")

        return hotel_booking
    except Exception as e:
        raise e