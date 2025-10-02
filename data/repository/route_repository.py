from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from fastapi import HTTPException

from data.model.route_model import RouteModel
from infrastructure.schema.route_schema import RouteCreateSchema


async def create_route(db: AsyncSession, route: RouteCreateSchema) -> RouteModel:
    new_route = RouteModel(**route.model_dump())
    db.add(new_route)
    await db.commit()
    await db.refresh(new_route)
    return new_route


async def get_route_by_id(db: AsyncSession, route_id: int) -> RouteModel:
    result = await db.execute(select(RouteModel).where(RouteModel.id == route_id))
    route = result.scalar_one_or_none()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


async def get_all_routes(db: AsyncSession) -> list[RouteModel]:
    result = await db.execute(select(RouteModel))
    return result.scalars().all()