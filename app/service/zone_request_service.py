from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from app.service import admin_service
from data.repository import zone_request_repository, admin_repository
from infrastructure.schema.zone_request_schema import ZoneRequestCreateSchema, ZoneRequestResponseSchema, \
    ZoneRequestUpdateSchema, ZoneRequestListResponseSchema


async def create_zone_request(db: AsyncSession, request: ZoneRequestCreateSchema, agency_name: str, username:str):
    request_dict = request.model_dump()
    request_dict['agency_name'] = agency_name
    request_dict['updated_by'] = username
    request_dict['created_by'] = username

    result = await zone_request_repository.create(db, request_dict)
    return ZoneRequestResponseSchema.model_validate(result)


async def update_zone_request(db: AsyncSession, request: ZoneRequestUpdateSchema, agency_name: str, username:str):
    try:
        zone_request = await zone_request_repository.get_by_id(db, request.id)

        if not zone_request:
            raise HTTPException(status_code=400, detail='Zone request not found')

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if zone_request.agency_name not in child_agencies:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        update_data = request.model_dump(exclude_unset=True, exclude_none=True)
        update_data["updated_by"] = username
        update_data["updated_at"] = get_current_time()

        result = await zone_request_repository.update_zone_request(db, request.id, update_data)
        return ZoneRequestResponseSchema.model_validate(result)

    except Exception as e:
        raise e


async def get_zone_requests(db: AsyncSession, agency_name: str):
    try:
        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        result = await zone_request_repository.get_all_zone_requests(db, child_agencies)


        zone_requests = [ZoneRequestResponseSchema.model_validate(zr) for zr in result]
        return ZoneRequestListResponseSchema(zone_requests=zone_requests)

    except Exception as e:
        raise e


async def get_zone_request_by_id(db: AsyncSession, zone_request_id: int, agency_name: str):
    try:
        result = await zone_request_repository.get_by_id(db, zone_request_id)

        if not result:
            raise HTTPException(status_code=400, detail='Zone request not found')

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if result.agency_name not in child_agencies:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        return ZoneRequestResponseSchema.model_validate(result)

    except Exception as e:
        raise e

async def delete_zone_request(db: AsyncSession, zone_request_id: int, agency_name: str):
    success = await zone_request_repository.delete_zone_request(
        db=db,
        zone_request_id=zone_request_id,
        agency_name=agency_name
    )

    if not success:
        raise HTTPException(status_code=400, detail="Zone request not found or could not be deleted")

    return {"message" : "Zone Request deleted successfully"}
