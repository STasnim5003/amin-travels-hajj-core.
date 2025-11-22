import json

import fastapi
from fastapi import Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
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
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await hotel_request_service.create_hotel_request(db, request, agency_name)

@private_router.get("/hotel-request", response_model=HotelRequestListResponseSchema)
async def get_hotel_requests(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await hotel_request_service.get_hotel_requests(db, agency_name)

@private_router.put("/hotel-request", response_model=HotelRequestResponseSchema)
async def update_hotel_request(
        # request: HotelRequestUpdateSchema,
        id: int = Form(...),
        city: str = Form(None),
        type: str = Form(None),
        name: str = Form(None),
        tasria_number: int = Form(None),
        check_in: str = Form(None),
        check_out: str = Form(None),
        number_of_haji: int = Form(None),
        room_allocation: str = Form(None),
        hotel_contact_person: str = Form(None),
        status: str = Form(None),
        nusuk_request_id: str = Form(None),
        is_active: bool = Form(None),
        pricing: str = Form(None),
        document: UploadFile = File(None),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    def parse_json(field):
        if field is None:
            return None
        try:
            return json.loads(field)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON for field: {field}"
            )

    hotel_request_update = HotelRequestUpdateSchema(
        id=id,
        city=city,
        type=type,
        name=name,
        tasria_number=tasria_number,
        check_in=parse_json(check_in),
        check_out=parse_json(check_out),
        number_of_haji=number_of_haji,
        room_allocation=parse_json(room_allocation),
        hotel_contact_person=parse_json(hotel_contact_person),
        status=status,
        nusuk_request_id=nusuk_request_id,
        is_active=is_active,
        pricing=parse_json(pricing),
        document=None  # You likely handle file separately
    )
    return await hotel_request_service.update_hotel_request(db, hotel_request_update, agency_name, document)

@private_router.get("/hotel-request/{request_id}", response_model=HotelRequestResponseSchema)
async def get_request_by_id(
        request_id : int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await hotel_request_service.get_hotel_request_by_id(db, request_id, agency_name)

@private_router.delete("/hotel-request/{request_id}")
async def delete_hotel_request(
        request_id : int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await hotel_request_service.delete_hotel_request(db, request_id, agency_name)