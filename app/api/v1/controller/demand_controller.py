import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import demand_service
from data.db.db_config import get_async_db
from infrastructure.schema.demand_schema import FlightDemandListResponse, RouteDemandListResponse, \
    FoodDemandListResponse

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Package Demand"])


@private_router.get("/flight-demand", response_model=FlightDemandListResponse)
async def get_flight_demand(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await demand_service.get_flight_demand(db=db, agency_name=agency_name)


@private_router.get("/route-demand", response_model=RouteDemandListResponse)
async def get_route_demand(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await demand_service.get_route_demand(db=db, agency_name=agency_name)


@private_router.get("/food-demand", response_model=FoodDemandListResponse)
async def get_food_demand(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await demand_service.get_food_demand(db=db, agency_name=agency_name)


@private_router.get("/hotel-demand")
async def get_hotel_demand(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await demand_service.get_hotel_demand(db=db, agency_name=agency_name)
