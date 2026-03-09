import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import zone_request_service
from data.db.db_config import get_async_db
from infrastructure.schema.zone_request_schema import ZoneRequestResponseSchema, ZoneRequestCreateSchema, \
    ZoneRequestUpdateSchema, ZoneRequestListResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Zone Request"])


@private_router.post("/zone-request", response_model=ZoneRequestResponseSchema, tags=["Zone Request"])
async def create_zone_request(
        request: ZoneRequestCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> ZoneRequestResponseSchema:
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user['username']
    return await zone_request_service.create_zone_request(db=db, request=request, agency_name=agency_name,
                                                          username=username)


@private_router.put("/zone-request", response_model=ZoneRequestResponseSchema, tags=["Zone Request"])
async def update_zone_request(
        request: ZoneRequestUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> ZoneRequestResponseSchema:
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user['username']
    return await zone_request_service.update_zone_request(db=db, request=request, agency_name=agency_name,
                                                          username=username)


@private_router.get("/zone-request", response_model=ZoneRequestListResponseSchema, tags=["Zone Request"])
async def get_zone_requests(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> ZoneRequestListResponseSchema:
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await zone_request_service.get_zone_requests(db=db, agency_name=agency_name)


@private_router.get("/zone-request/{zone_request_id}", response_model=ZoneRequestResponseSchema, tags=["Zone Request"])
async def get_zone_request_by_id(
        zone_request_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> ZoneRequestResponseSchema:
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await zone_request_service.get_zone_request_by_id(
        db=db,
        zone_request_id=zone_request_id,
        agency_name=agency_name
    )


@private_router.delete("/zone-request/{zone_request_id}", response_model=dict, tags=["Zone Request"])
async def delete_zone_request(
        zone_request_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await zone_request_service.delete_zone_request(
        db=db,
        zone_request_id=zone_request_id,
        agency_name=agency_name
    )
