import fastapi
from fastapi import Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user, STAFF_ROLES
from app.service import hotel_request_service
from data.db.db_config import get_async_db
from infrastructure.schema.hotel_request_schema import HotelRequestResponseSchema, HotelRequestBase, \
    HotelRequestUpdateSchema, HotelRequestListResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Hotel Request"])


@private_router.post("/hotel-request", response_model=HotelRequestResponseSchema)
async def create_hotel_request(
        request: HotelRequestBase,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user['username']
    return await hotel_request_service.create_hotel_request(db, request, agency_name, username)


@private_router.get("/hotel-request", response_model=HotelRequestListResponseSchema)
async def get_hotel_requests(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await hotel_request_service.get_hotel_requests(db, agency_name)


@private_router.put("/hotel-request", response_model=HotelRequestResponseSchema)
async def update_hotel_request(
        request: HotelRequestUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user['username']
    return await hotel_request_service.update_hotel_request(db, request, agency_name, username)


@private_router.get("/hotel-request/{request_id}", response_model=HotelRequestResponseSchema)
async def get_request_by_id(
        request_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await hotel_request_service.get_hotel_request_by_id(db, request_id, agency_name)


@private_router.delete("/hotel-request/{request_id}")
async def delete_hotel_request(
        request_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await hotel_request_service.delete_hotel_request(db, request_id, agency_name)


@private_router.put("/hotel-request/cancel/{request_id}")
async def cancel_hotel_request(
        request_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user['username']
    return await hotel_request_service.cancel_request(db, request_id, agency_name, username)


@private_router.put("/hotel-request/cancel/lead-agency-action/{request_id}")
async def cancel_hotel_request(
        request_id: int,
        status: str = Form(None),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["AGENCY", *STAFF_ROLES]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    username = current_user['username']
    return await hotel_request_service.cancel_request_lead_agency_action(db, request_id, agency_name, status, username)
