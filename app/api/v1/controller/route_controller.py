from typing import List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import route_service
from data.db.db_config import get_async_db
from infrastructure.schema.route_schema import RouteResponseSchema, RouteCreateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/route", response_model=RouteResponseSchema, tags=["Route"])
async def create_route(route: RouteCreateSchema, db: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_service.create_route_service(db, route, agency_name)


@private_router.get("/route/{route_id}", response_model=RouteResponseSchema, tags=["Route"])
async def get_route(route_id: int, db: AsyncSession = Depends(get_async_db),current_user: dict = Depends(get_current_user)):
    return await route_service.get_route_service(db, route_id)


@private_router.get("/route", response_model=List[RouteResponseSchema], tags=["Route"])
async def get_routes(db: AsyncSession = Depends(get_async_db),current_user: dict = Depends(get_current_user)):
    return await route_service.get_all_routes_service(db)