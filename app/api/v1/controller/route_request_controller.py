import fastapi
from fastapi import Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.middleware.middleware import get_current_user
from app.service import route_request_service
from data.db.db_config import get_async_db
from infrastructure.schema.route_request_schema import RouteRequestResponseSchema, RouteRequestBaseSchema, \
    RouteRequestListResponseSchema, RouteRequestUpdateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private" , tags=["Route Request"])

@private_router.post("/route-request", response_model=RouteRequestResponseSchema)
async def create_route_request(
        request: RouteRequestBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_request_service.create_route_request(db=db, request=request, agency_name=agency_name)

@private_router.get("/route-request/hajji-count")
async def route_wise_hajji_count(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_request_service.get_route_wise_hajji_count(db=db, agency_name=agency_name)

@private_router.get("/route-request", response_model=RouteRequestListResponseSchema)
async def get_route_requests(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_request_service.get_route_requests(db=db, agency_name=agency_name)

@private_router.get("/route-request/{request_id}", response_model=RouteRequestResponseSchema)
async def get_route_request(
        request_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_request_service.get_route_request_by_id(db=db, request_id=request_id,agency_name=agency_name)

@private_router.put("/route-request", response_model=RouteRequestResponseSchema)
async def update_route_request(
        request : RouteRequestUpdateSchema,
        db : AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_request_service.update_route_request(db=db, request=request, agency_name=agency_name)

@private_router.delete("/route-request/{requisition_id}")
async def delete_route_request(
        requisition_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_request_service.delete_route_request(db=db, requisition_id=requisition_id, agency_name=agency_name)

@private_router.put("/route-request/cancel/{request_id}")
async def cancel_route_request(
        request_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_request_service.cancel_request(db, request_id, agency_name)

@private_router.put("/route-request/cancel/lead-agency-action/{request_id}")
async def cancel_hotel_request(
        request_id: int,
        status : str = Form(None),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_request_service.cancel_request_lead_agency_action(db, request_id, agency_name, status)