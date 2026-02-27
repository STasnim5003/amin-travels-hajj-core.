from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import demand_repository
from infrastructure.schema.demand_schema import FlightDemandListResponse, FlightDemandResponse, RouteDemandResponse, \
    RouteDemandListResponse, FoodDemandResponse, FoodDemandListResponse


async def get_flight_demand(db:AsyncSession, agency_name:str):
    try:
        result = await demand_repository.get_flight_demand(db=db, agency_name=agency_name)

        flight_demands: List[FlightDemandResponse] = [
            FlightDemandResponse(
                flight_date_start = {
                    'english_calendar': r['english_start'],
                    'arabic_calendar': r['arabic_start'],
                },
                flight_date_end = {
                    'english_calendar': r['english_end'],
                    'arabic_calendar': r['arabic_end'],
                },
                number_of_hajji=r["pilgrim_count"],
                # package_name = r['package_name'],
                # package_duration = r['package_duration'],
            )
            for r in result
        ]

        return FlightDemandListResponse(flight_demands=flight_demands)
    except Exception as e:
        raise e

async def get_route_demand(db: AsyncSession, agency_name: str):
    try:
        rows = await demand_repository.get_route_demand(db=db, agency_name=agency_name)

        route_demands: List[RouteDemandResponse] = [
            RouteDemandResponse(
                route_name=row["description"],
                package_name=row["package_name"],
                package_duration=row["package_duration"],
                number_of_hajji=row["pilgrim_count"]
            )
            for row in rows
        ]

        return RouteDemandListResponse(route_demands=route_demands)

    except Exception as e:
        raise e

async def get_food_demand(db: AsyncSession, agency_name: str):
    try:
        rows = await demand_repository.get_food_demand(db=db, agency_name=agency_name)
        food_demands: List[FoodDemandResponse] = [
            FoodDemandResponse(
                food_name=row['food_menu_name'],
                items = row['food_items'],
                number_of_hajji = row['menu_count']
            )
            for row in rows
        ]

        return FoodDemandListResponse(food_demands=food_demands)
    except Exception as e:
        raise e