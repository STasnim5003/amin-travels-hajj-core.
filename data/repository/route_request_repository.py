from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.model.route_request_model import RouteRequestModel


async def count_hajji_on_route_type_and_name(db:AsyncSession, route_type : str, route_name : str, agency_name : str):
    try:
        stmt = (
            select(RouteRequestModel)
            .where(RouteRequestModel.route_type == route_type,
                   RouteRequestModel.route_name == route_name,
                   RouteRequestModel.agency_name == agency_name)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e