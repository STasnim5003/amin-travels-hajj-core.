from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from data.model.route_request_model import RouteRequestModel


async def find_route_by_route_mapping_id(db:AsyncSession, route_mapping_id:str, agency_name : str):
    try:
        stmt = (
            select(RouteRequestModel)
            .where(RouteRequestModel.route_mapping_id == route_mapping_id,
                   RouteRequestModel.agency_name == agency_name)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e


async def create_route_request(db:AsyncSession, request_dict:dict):
    try:
        stmt = (
            insert(RouteRequestModel)
            .values(**request_dict)
            .returning(RouteRequestModel)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e