from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import dashboard_repository
from infrastructure.schema.dashboard_schema import DashboardResponseSchema


async def get_dashboard_data(db: AsyncSession, agency_name: str):
    try:
        row = await dashboard_repository.get_dashboard_data(
            db=db,
            agency_name=agency_name
        )

        if not row:
            return None

        data = row._mapping  # 🔑 important

        return DashboardResponseSchema(
            agency_name=data["agency_name"],
            flight_requested=data["flight_requested"],
            route_requested=data["route_requested"],
            hotel_requested=data["hotel_requested"],
            number_of_hajji=data["number_of_hajji"],
            bdt=data["bdt"],
            sar=data["sar"],
        )

    except Exception as e:
        raise e
