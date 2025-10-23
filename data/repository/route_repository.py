from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from fastapi import HTTPException

from data.model.route_model import RouteModel
from infrastructure.schema.route_schema import RouteCreateSchema


async def create_route(db: AsyncSession, route: RouteCreateSchema) -> RouteModel:

    existing_route = await db.execute(
        select(RouteModel).where(
            RouteModel.route_name == route.route_name,
            RouteModel.agency_name == route.agency_name
        )
    )
    existing_route = existing_route.scalar_one_or_none()

    if existing_route:
        raise HTTPException(status_code=400,detail=f"Route with name '{route.route_name}' already exists for agency '{route.agency_name}'.")
    new_route = RouteModel(**route.model_dump())
    db.add(new_route)
    await db.commit()
    await db.refresh(new_route)
    return new_route


async def get_route_by_id(db: AsyncSession, route_id: int, agency_name:str) -> RouteModel:
    result = await db.execute(select(RouteModel).where(RouteModel.id == route_id))
    route = result.scalar_one_or_none()
    if not route:
        raise HTTPException(status_code=400, detail="Route not found")
    if route.agency_name != agency_name:
        raise HTTPException(status_code=400, detail="Agency names do not match")
    return route


async def get_all_routes(db: AsyncSession,agency_name:str) -> list[RouteModel]:
    stmt = select(RouteModel).where(RouteModel.is_publish == True, RouteModel.agency_name == agency_name)
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_route(db:AsyncSession, update_request_dict:dict):
    try:
        result = await db.execute(
            update(RouteModel).where(RouteModel.id == update_request_dict.get('id'))
            .values(**update_request_dict)
            .returning(RouteModel)
        )

        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def delete_route(db:AsyncSession, route_id:int):
    try:
        await db.execute(
            delete(RouteModel).where(RouteModel.id == route_id)
        )

        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))