from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from app.service import admin_service
from data.repository import flight_request_repository, admin_repository
from infrastructure.schema.flight_request_schema import FlightRequestCreateSchema, FlightRequestResponseSchema, \
    FlightRequestUpdateSchema, FlightRequestListResponseSchema


async def create_flight_request(db: AsyncSession, request: FlightRequestCreateSchema, agency_name: str):
    try:
        request_dict = request.model_dump()
        request_dict['agency_name'] = agency_name
        request_dict['updated_by'] = agency_name
        request_dict['created_by'] = agency_name
        request_dict['flight_requested'] = request.total_seat

        result = await flight_request_repository.create(db, request_dict)
        return FlightRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def update_flight_request(db: AsyncSession, request: FlightRequestUpdateSchema, agency_name: str):
    try:
        flight_request = await flight_request_repository.get_by_id(db, request.id)

        if not flight_request:
            raise HTTPException(status_code=400, detail='Flight request not found')

        update_data = request.model_dump(exclude_unset=True, exclude_none=True)
        update_data["updated_by"] = agency_name
        update_data['updated_at'] = get_current_time()
        update_data['agency_name'] = flight_request['agency_name']

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if flight_request['agency_name'] not in child_agencies:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        if flight_request['total_seat'] != request.total_seat:
            update_data['flight_requested'] = request.total_seat - flight_request['total_seat']

        result = await flight_request_repository.update_flight_request(db, request.id, update_data)
        return FlightRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def get_flight_requests(db: AsyncSession, agency_name: str):
    try:
        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        result = await flight_request_repository.get_all_flight_requests(db, child_agencies)

        flight_requests = []
        for flight, arrival_desc, departure_desc in result:
            data = flight.__dict__.copy()
            data["arrival_route_description"] = arrival_desc
            data["departure_route_description"] = departure_desc
            flight_requests.append(data)

        return FlightRequestListResponseSchema(flight_requests=flight_requests)
    except Exception as e:
        raise e


async def get_flight_request_by_id(db: AsyncSession, flight_request_id: int, agency_name: str):
    try:
        result = await flight_request_repository.get_by_id(db=db, flight_request_id=flight_request_id)

        if not result:
            raise HTTPException(status_code=400, detail='Flight request not found')

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if result['agency_name'] not in child_agencies:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        return FlightRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_flight_request(db: AsyncSession, flight_request_id: int, agency_name: str):
    result = await flight_request_repository.get_by_id(db=db, flight_request_id=flight_request_id)

    if not result:
        raise HTTPException(status_code=400, detail='Flight request not found')

    success = await flight_request_repository.delete_flight_request(
        db=db,
        flight_request_id=flight_request_id,
        agency_name=agency_name,
        total_seat=result.total_seat
    )

    if not success:
        raise HTTPException(status_code=400, detail="Flight request not found or could not be deleted")

    return {"message": "Flight Request Deleted Successfully"}
