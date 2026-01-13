from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import route_request_repository
from infrastructure.schema.route_request_schema import RouteRequestBaseSchema, RouteRequestResponseSchema


async def create_route_request(db:AsyncSession, request:RouteRequestBaseSchema, agency_name:str):
    try:
        request_dict = request.model_dump(exclude_none=True)
        route_request = await route_request_repository.find_route_by_route_mapping_id(db = db,route_mapping_id=request.route_mapping_id,agency_name=agency_name)

        request_dict['status'] = "SEND_TO_LEAD"
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = agency_name
        request_dict['updated_by'] = agency_name

        if len(route_request) == 1:
            if route_request[0].number_of_pax != request_dict['number_of_pax']:
                raise HTTPException(status_code=400, detail="Arrival and Departure are not the same")

        # TODO: fix from here

        result = await route_request_repository.create_route_request(db=db, request_dict=request_dict)
        return RouteRequestResponseSchema.model_validate(result)

    except Exception as e:
        raise e