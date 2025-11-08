from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import transport_repository
from infrastructure.schema.transport_schema import TransportServiceCreateSchema, TransportServiceResponseSchema, \
    TransportServiceListResponseSchema


async def create_transport_service(db: AsyncSession, request: TransportServiceCreateSchema, agency_name: str):
    payload = request.model_dump()
    payload.update({
        "agency_name": agency_name,
        "created_by": agency_name,
        "updated_by": agency_name
    })

    result = await transport_repository.create_transport_service(db, payload)
    return TransportServiceResponseSchema.model_validate(result)


async def get_transport_service_list(db: AsyncSession, agency_name: str):
    result = await transport_repository.get_transport_services(db, agency_name)
    services = [TransportServiceResponseSchema.model_validate(row) for row in result]
    return TransportServiceListResponseSchema(transport_services=services)


async def update_transport_service(db, request, agency_name):
    request_dict = request.model_dump(exclude_unset=True, exclude_none=True)
    request_dict["updated_by"] = agency_name
    request_dict['updated_at'] = datetime.utcnow() + timedelta(hours=6)

    transport = await transport_repository.get_transport_service_by_id(db, request.id, agency_name)
    if not transport:
        raise HTTPException(status_code=400, detail="Transport Service Not Found")

    result = await transport_repository.update_transport_service(db, request.id, request_dict)
    return TransportServiceResponseSchema.model_validate(result)