from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import route_request_repository
from infrastructure.schema.route_request_schema import RouteRequestBaseSchema


async def create_route_request(db:AsyncSession, request:RouteRequestBaseSchema, agency_name:str):
    # try:
    #     if request.route_type == 'DEPARTURE_ROUTE':
    #         route_request = await route_request_repository.count_hajji_on_route_type_and_name(db = db,
    #                                                                                           route_type = request.route_type,
    #                                                                                           route_name=request.route_name,
    #                                                                                           agency_name=agency_name)
    pass