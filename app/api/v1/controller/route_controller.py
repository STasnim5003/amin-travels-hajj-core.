from typing import List

import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import route_service
from data.db.db_config import get_async_db
from infrastructure.schema.route_schema import RouteResponseSchema, RouteBaseSchema, \
    RouteUpdateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/route", response_model=RouteResponseSchema, tags=["Route"])
async def create_route(route: RouteBaseSchema, db: AsyncSession = Depends(get_async_db),
                       current_user: dict = Depends(get_current_user)):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await route_service.create_route_service(db, route, agency_name, username)


@private_router.get("/route", response_model=List[RouteResponseSchema], tags=["Route"])
async def get_routes(db: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await route_service.get_all_routes_service(db, agency_name)


@private_router.put("/route", response_model=RouteResponseSchema, tags=["Route"])
async def update_route(
        update_request: RouteUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user['username']
    return await route_service.update_route(db, update_request, agency_name, username)


@private_router.get("/route/{route_id}", response_model=RouteResponseSchema, tags=["Route"])
async def get_route_by_id(route_id: int, db: AsyncSession = Depends(get_async_db),
                          current_user: dict = Depends(get_current_user)):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await route_service.get_route_service(db, route_id, agency_name)


@private_router.delete("/route/{route_id}", response_model=List[RouteResponseSchema], tags=["Route"])
async def delete_route(
        route_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await route_service.delete_route(db, route_id, agency_name)
