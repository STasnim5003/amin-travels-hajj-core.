from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from app.service import admin_service
from data.repository import hotel_request_repository, file_repository, admin_repository
from infrastructure.schema.hotel_request_schema import HotelRequestBase, HotelRequestResponseSchema, \
    HotelRequestListResponseSchema, HotelRequestUpdateSchema


async def create_hotel_request(db: AsyncSession, request: HotelRequestBase, agency_name :str):
    try:
        request_dict = request.model_dump(exclude_none=True)
        request_dict["agency_name"] = agency_name
        request_dict["created_by"] = agency_name
        request_dict["updated_by"] = agency_name

        result = await hotel_request_repository.create_hotel_request(db=db, request_dict=request_dict)
        return HotelRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e

async def get_hotel_requests(db: AsyncSession, agency_name : str):
    try:
        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        result = await hotel_request_repository.get_hotel_requests(db=db, agency_name=child_agencies)
        hotel_requests = []
        for hotel_request in result:
            hotel_requests.append(HotelRequestResponseSchema.model_validate(hotel_request))

        return HotelRequestListResponseSchema(
            hotel_requests = hotel_requests
        )
    except Exception as e:
        raise e

async def get_hotel_request_by_id(db:AsyncSession, request_id:int, agency_name:str):
    try:
        result = await hotel_request_repository.get_hotel_request_by_id(db=db, request_id=request_id)
        if result.document:
            result.document = await generate_downloadable_urls(result.document)

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if result.agency_name not in child_agencies:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        return HotelRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e

async def update_hotel_request(db:AsyncSession, request: HotelRequestUpdateSchema, agency_name : str, document: Optional[UploadFile]):
    try:
        result = await hotel_request_repository.get_hotel_request_by_id(db=db, request_id=request.id)
        if not result:
            raise HTTPException(status_code=400, detail="Hotel Request not found")

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if result.agency_name not in child_agencies:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        request_dict = request.model_dump(exclude_none=True)
        document_data = []
        if document:
            try:
                document_resp = await file_repository.upload_file(file=document, name="hotel_request_files")
                document_data.append(document_resp.model_dump())
                request_dict['document'] = document_data
            except Exception as e:
                raise e

        request_dict['updated_by'] = agency_name
        request_dict["updated_at"] = datetime.now() + timedelta(hours=6)


        result = await hotel_request_repository.update_hotel_request(db=db, request_dict=request_dict)
        return HotelRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_hotel_request(db:AsyncSession, request_id:int, agency_name:str):
    try:
        result = await hotel_request_repository.get_hotel_request_by_id(db=db, request_id=request_id)
        if not result:
            raise HTTPException(status_code=400, detail="Hotel Request not found")

        result = await hotel_request_repository.delete_hotel_request(db=db, request_id=request_id)
        if not result:
            raise HTTPException(status_code=400, detail="Delete Hotel Request failed")
        return result
    except Exception as e:
        raise e