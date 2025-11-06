import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import flight_request_service
from data.db.db_config import get_async_db
from infrastructure.schema.flight_request_schema import FlightRequestResponseSchema, FlightRequestCreateSchema, \
    FlightRequestUpdateSchema, FlightRequestListResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/flight-request", response_model=FlightRequestResponseSchema, tags=["Flight Request"])
async def create_flight_request(
        request: FlightRequestCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> FlightRequestResponseSchema:

    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await flight_request_service.create_flight_request(db=db, request=request ,agency_name=agency_name)

@private_router.put("/flight-request", response_model=FlightRequestResponseSchema, tags=["Flight Request"])
async def update_flight_request(
        request: FlightRequestUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> FlightRequestResponseSchema:

    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await flight_request_service.update_flight_request(db=db, request=request, agency_name=agency_name)

@private_router.get("/flight-request", response_model=FlightRequestListResponseSchema, tags=["Flight Request"])
async def get_flight_requests(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> FlightRequestListResponseSchema:

    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await flight_request_service.get_flight_requests(db=db, agency_name=agency_name)


@private_router.get("/flight-request/{flight_request_id}", response_model=FlightRequestResponseSchema, tags=['Flight Request'])
async def get_flight_request_by_id(
        flight_request_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
)-> FlightRequestResponseSchema:

    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await flight_request_service.get_flight_request_by_id(db=db, flight_request_id=flight_request_id, agency_name=agency_name)