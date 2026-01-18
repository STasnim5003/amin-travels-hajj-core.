from typing import Optional

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import route_for_requisition_service
from data.db.db_config import get_async_db
from infrastructure.schema.route_for_requistion_schema import RouteForRequisitionResponseSchema, \
    RouteForRequisitionListResponseSchema, RouteForRequisitionUpdateSchema, \
    RouteForRequisitionCreateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Route For Requisition"])


@private_router.post("/route-for-requisition", response_model=RouteForRequisitionListResponseSchema)
async def create_route(
        route: RouteForRequisitionCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_for_requisition_service.create_route(db, route, agency_name)


@private_router.get("/route-for-requisition", response_model=RouteForRequisitionListResponseSchema)
async def get_route_for_requisition(
        route_type: Optional[str] = None,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_for_requisition_service.get_routes(db, route_type, agency_name)


@private_router.put("/route-for-requisition", response_model=RouteForRequisitionResponseSchema, )
async def update_route_for_requisition(
        request: RouteForRequisitionUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_for_requisition_service.update_route(db, request, agency_name)


@private_router.get("/route-for-requisition/summary")
async def get_route_for_requisition_summary(
        route_type: str,
        route_name: str,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_for_requisition_service.get_route_summary(db, route_type, route_name, agency_name)


@private_router.get("/route-for-requisition/{requisition_id}", response_model=RouteForRequisitionResponseSchema)
async def get_route_for_requisition(
        requisition_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_for_requisition_service.get_routes_by_id(db, requisition_id, agency_name)


@private_router.delete("/route-for-requisition/{requisition_id}")
async def delete_route_for_requisition(
        requisition_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_for_requisition_service.delete_routes(db, requisition_id, agency_name)
