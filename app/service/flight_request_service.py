from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import flight_request_repository, admin_repository
from infrastructure.schema.flight_request_schema import FlightRequestCreateSchema, FlightRequestResponseSchema, \
    FlightRequestUpdateSchema, FlightRequestListResponseSchema


async def create_flight_request(db: AsyncSession, request: FlightRequestCreateSchema, agency_name: str):
    request_dict = request.model_dump()
    request_dict['agency_name'] = agency_name
    request_dict['updated_by'] = agency_name
    request_dict['created_by'] = agency_name
    result = await flight_request_repository.create(db, request_dict)
    return FlightRequestResponseSchema.model_validate(result)


async def update_flight_request(db: AsyncSession, request: FlightRequestUpdateSchema, agency_name: str):
    try:
        flight_request = await flight_request_repository.get_by_id(db, request.id, agency_name)

        if not flight_request:
            raise HTTPException(status_code=400, detail='Flight request not found')

        update_data = request.model_dump(exclude_unset=True, exclude_none=True)
        update_data["updated_by"] = agency_name
        update_data["updated_at"] = datetime.utcnow() + timedelta(hours=6)

        result = await flight_request_repository.update_flight_request(db, request.id, update_data)
        return FlightRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def get_flight_requests(db:AsyncSession, agency_name:str):
    try:
        result = await flight_request_repository.get_all_flight_requests(db, agency_name)

        if not result:
            raise HTTPException(status_code=400, detail='Flight request not found')
        flight_requests = []
        for flight_request in result:
            flight_requests.append(FlightRequestResponseSchema.model_validate(flight_request))
        return FlightRequestListResponseSchema(flight_requests = flight_requests)
    except Exception as e:
        raise e


async def get_flight_request_by_id(db:AsyncSession, flight_request_id:int, agency_name:str):
    try:
        result = await flight_request_repository.get_by_id(db=db, flight_request_id= flight_request_id, agency_name=agency_name)

        if not result:
            raise HTTPException(status_code=400, detail='Flight request not found')

        return FlightRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e