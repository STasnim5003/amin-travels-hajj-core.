from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_model import AdminModel
from data.model.pilgrim_data_model import PilgrimDataModel


async def get_dashboard_data(db: AsyncSession, agency_name: str):
    try:
        # subquery, not a join: an agency with no pilgrims yet still gets its row (0 hajji)
        number_of_hajji = (
            select(func.count(PilgrimDataModel.tracking_id))
            .where(PilgrimDataModel.group_name == AdminModel.agency_name)
            .scalar_subquery()
        )
        stmt = (
            select(
                AdminModel.agency_name,
                AdminModel.flight_requested,
                AdminModel.route_requested,
                AdminModel.hotel_requested,
                AdminModel.bdt,
                AdminModel.sar,
                number_of_hajji.label("number_of_hajji"),
            )
            .where(AdminModel.agency_name == agency_name)
        )

        result = await db.execute(stmt)
        return result.one_or_none()

    except Exception as e:
        raise e


async def get_all_agencies_dashboard_data(db: AsyncSession):
    """Totals across every agency, for SUPER_ADMIN (whose own agency_name isn't a real agency)."""
    totals = (
        await db.execute(
            select(
                func.coalesce(func.sum(AdminModel.flight_requested), 0).label("flight_requested"),
                func.coalesce(func.sum(AdminModel.route_requested), 0).label("route_requested"),
                func.coalesce(func.sum(AdminModel.hotel_requested), 0).label("hotel_requested"),
                func.coalesce(func.sum(AdminModel.bdt), 0).label("bdt"),
                func.coalesce(func.sum(AdminModel.sar), 0).label("sar"),
            )
        )
    ).one()
    number_of_hajji = await db.scalar(
        select(func.count(PilgrimDataModel.tracking_id))
        .where(PilgrimDataModel.group_name.in_(select(AdminModel.agency_name)))
    )
    return {**totals._mapping, "number_of_hajji": number_of_hajji}
