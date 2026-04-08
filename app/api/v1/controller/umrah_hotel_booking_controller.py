from typing import List

import fastapi
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import umrah_hotel_booking_service
from data.db.db_config import get_async_db
from infrastructure.schema.umrah_hotel_booking_schema import UmrahHotelBookingResponse, UmrahHotelBookingCreate, \
    UmrahHotelBookingUpdate

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Umrah Hotel Booking"])


@private_router.post("/umrah/hotel-booking", response_model=UmrahHotelBookingResponse)
async def create_umrah_hotel_booking(
        request: UmrahHotelBookingCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user['agency_name']
    username = current_user['username']

    return await umrah_hotel_booking_service.create_hotel_booking(db=db, request=request, agency_name=agency_name,
                                                                  username=username)


@private_router.get("/umrah/hotel-booking", response_model=List[UmrahHotelBookingResponse])
async def get_umrah_hotel_booking(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user['agency_name']
    return await umrah_hotel_booking_service.get_umrah_hotel_booking(db=db, agency_name=agency_name)


@private_router.put("/umrah/hotel-booking", response_model=UmrahHotelBookingResponse)
async def update_umrah_hotel_booking(
        request: UmrahHotelBookingUpdate,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user['agency_name']
    username = current_user['username']

    return await umrah_hotel_booking_service.update_umrah_hotel_booking(db=db, request=request, agency_name=agency_name,
                                                                        username=username)


@private_router.get("/umrah/hotel-booking/{hotel_booking_id}", response_model=UmrahHotelBookingResponse)
async def get_umrah_hotel_booking_by_id(
        hotel_booking_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user['agency_name']

    return await umrah_hotel_booking_service.get_umrah_hotel_booking_by_id(db=db, hotel_booking_id=hotel_booking_id,
                                                                           agency_name=agency_name)


@private_router.delete("/umrah/hotel-booking/{hotel_booking_id}")
async def get_umrah_hotel_booking_by_id(
        hotel_booking_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user['agency_name']
    return await umrah_hotel_booking_service.delete_umrah_hotel_booking(db=db, hotel_booking_id=hotel_booking_id,
                                                                        agency_name=agency_name)
