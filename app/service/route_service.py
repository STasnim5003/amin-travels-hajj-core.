from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import route_repository
from infrastructure.schema.route_schema import RouteCreateSchema, RouteResponseSchema


async def create_route_service(db: AsyncSession, route: RouteCreateSchema, agency_name: str) -> RouteResponseSchema:
    try:
        route_data = route.model_dump()
        route_data["agency_name"] = agency_name
        route_data["created_by"] = agency_name
        route_data["updated_by"] = agency_name

        new_route = await route_repository.create_route(db, RouteCreateSchema(**route_data))
        return RouteResponseSchema.model_validate(new_route)
    except Exception as e:
        raise

async def get_route_service(db: AsyncSession, route_id: int) -> RouteResponseSchema:
    try:
        route = await route_repository.get_route_by_id(db, route_id)
        return RouteResponseSchema.model_validate(route)
    except Exception as e:
        raise


async def get_all_routes_service(db: AsyncSession) -> list[RouteResponseSchema]:
    try:
        routes = await route_repository.get_all_routes(db)
        return [RouteResponseSchema.model_validate(r) for r in routes]
    except Exception as e:
        raise
