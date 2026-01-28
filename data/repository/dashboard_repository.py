from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_model import AdminModel
from data.model.pilgrim_data_model import PilgrimDataModel


async def get_dashboard_data(db: AsyncSession, agency_name: str):
    try:
        stmt = (
            select(
                AdminModel.agency_name,
                AdminModel.flight_requested,
                AdminModel.route_requested,
                AdminModel.hotel_requested,
                AdminModel.bdt,
                AdminModel.sar,
                func.count(PilgrimDataModel.tracking_id).label("number_of_hajji"),
            )
            .join(
                PilgrimDataModel,
                AdminModel.agency_name == PilgrimDataModel.group_name
            )
            .where(AdminModel.agency_name == agency_name)
            .group_by(
                AdminModel.agency_name,
                AdminModel.flight_requested,
                AdminModel.route_requested,
                AdminModel.hotel_requested,
                AdminModel.bdt,
                AdminModel.sar
            )
        )

        result = await db.execute(stmt)
        return result.one_or_none()

    except Exception as e:
        raise e
