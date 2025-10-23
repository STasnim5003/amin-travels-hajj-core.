from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import route_repository
from infrastructure.schema.route_schema import RouteCreateSchema, RouteResponseSchema, RouteBaseSchema, \
    RouteUpdateSchema


async def create_route_service(db: AsyncSession, route: RouteBaseSchema, agency_name: str) -> RouteResponseSchema:
    try:
        route_data = route.model_dump()
        route_data["agency_name"] = agency_name
        route_data["created_by"] = agency_name
        route_data["updated_by"] = agency_name

        new_route = await route_repository.create_route(db, RouteCreateSchema(**route_data))
        return RouteResponseSchema.model_validate(new_route)
    except Exception as e:
        raise e

async def get_route_service(db: AsyncSession, route_id: int, agency_name: str) -> RouteResponseSchema:
    try:
        route = await route_repository.get_route_by_id(db, route_id, agency_name)
        return RouteResponseSchema.model_validate(route)
    except Exception as e:
        raise


async def get_all_routes_service(db: AsyncSession, agency_name : str) -> list[RouteResponseSchema]:
    try:
        routes = await route_repository.get_all_routes(db,agency_name)
        return [RouteResponseSchema.model_validate(r) for r in routes]
    except Exception as e:
        raise e


async def update_route(db: AsyncSession, update_request: RouteUpdateSchema, agency_name: str):
    try:
        route = await route_repository.get_route_by_id(db, update_request.id, agency_name)
        if not route:
            raise HTTPException(status_code=400, detail="Route not found")
        update_request_dict = update_request.model_dump(exclude_unset=True)
        update_request_dict['updated_by'] = agency_name

        result = await route_repository.update_route(db, update_request_dict)
        return RouteResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_route(db:AsyncSession, route_id:int, agency_name:str):
    try:
        route = await route_repository.get_route_by_id(db, route_id, agency_name)
        if not route:
            raise HTTPException(status_code=400, detail="Route not found")
        await route_repository.delete_route(db, route_id)

        routes = await route_repository.get_all_routes(db,agency_name)
        return [RouteResponseSchema.model_validate(route) for route in routes]
    except Exception as e:
        raise e