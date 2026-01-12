from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from app.core.utils.get_current_time import get_current_time
from app.service import admin_service
from data.repository import hotel_request_repository, file_repository, admin_repository
from infrastructure.schema.hotel_request_schema import HotelRequestBase, HotelRequestResponseSchema, \
    HotelRequestListResponseSchema, HotelRequestUpdateSchema


async def create_hotel_request(db: AsyncSession, request: HotelRequestBase, agency_name: str, tasria_copy:Optional[UploadFile]):
    try:
        agency = await admin_repository.get_agency_by_agency_name(db,agency_name)
        if agency is None:
            raise HTTPException(status_code=400, detail="Agency not found")

        if agency.sar < request.pricing.with_vat:
            raise HTTPException(status_code=400, detail="You have not enough amount in SAR")

        if request.city == 'Madinah':
            madinah_hotel_allocated_and_total_seat = await hotel_request_repository.get_madinah_allocated_and_total_seat(db, agency_name)
            allocated_seat = madinah_hotel_allocated_and_total_seat.get('hotel_allocated_hajji')
            total_seat = madinah_hotel_allocated_and_total_seat.get('total_pilgrims')
            if allocated_seat + request.number_of_haji > total_seat:
                raise HTTPException(status_code=400, detail="Number of Haji exceeds total seat")

        request_dict = request.model_dump(exclude_none=True)
        request_dict["agency_name"] = agency_name
        request_dict["created_by"] = agency_name
        request_dict["updated_by"] = agency_name
        request_dict["status"] = "SEND_TO_LEAD"
        request_dict["sar"] = agency.sar - request.pricing.with_vat

        document_data = []
        if tasria_copy:
            try:
                document_resp = await file_repository.upload_file(file=tasria_copy, name="tasria_copy_files")
                document_data.append(document_resp.model_dump())
                request_dict['tasria_copy'] = document_data
            except Exception as e:
                raise e


        result = await hotel_request_repository.create_hotel_request(db=db, request_dict=request_dict)
        return HotelRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def get_hotel_requests(db: AsyncSession, agency_name: str):
    try:
        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        result = await hotel_request_repository.get_hotel_requests(db=db, agency_name=child_agencies)
        hotel_requests = []
        for hotel_request in result:
            hotel_requests.append(HotelRequestResponseSchema.model_validate(hotel_request))

        return HotelRequestListResponseSchema(
            hotel_requests=hotel_requests
        )
    except Exception as e:
        raise e


async def get_hotel_request_by_id(db: AsyncSession, request_id: int, agency_name: str):
    try:
        result = await hotel_request_repository.get_hotel_request_by_id(db=db, request_id=request_id)
        if result.document:
            result.document = await generate_downloadable_urls(result.document)

        if result.tasria_copy:
            result.tasria_copy = await generate_downloadable_urls(result.tasria_copy)

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if result.agency_name not in child_agencies:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        return HotelRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def update_hotel_request(db: AsyncSession, request: HotelRequestUpdateSchema, agency_name: str,
                               document: Optional[UploadFile]):
    try:
        result = await hotel_request_repository.get_hotel_request_by_id(db=db, request_id=request.id)
        if not result:
            raise HTTPException(status_code=400, detail="Hotel Request not found")

        is_lead_agency = await admin_repository.check_lead_agency(db, agency_name)

        if not is_lead_agency and result.status != 'SEND_TO_LEAD':
            raise HTTPException(status_code=400, detail="Lead Agency Makes Some changes. you can't update now!")

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
        request_dict['updated_at'] = get_current_time()

        result = await hotel_request_repository.update_hotel_request(db=db, request_dict=request_dict)
        return HotelRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_hotel_request(db: AsyncSession, request_id: int, agency_name: str):
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


async def cancel_request(db:AsyncSession, request_id:int, agency_name:str):
    try:
        result = await hotel_request_repository.get_hotel_request_by_id(db=db, request_id=request_id)
        if not result:
            raise HTTPException(status_code=400, detail="Hotel Request not found")
        if result.status == 'SEND_TO_LEAD':
            raise HTTPException(status_code=400, detail="Can't Cancel Request. Edit/Delete it")
        if result.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Agency name does not match")

        request_dict = {
            'cancel_request_status' : "REQUEST_FOR_CANCELLATION",
            'id' : request_id,
            'updated_by' : agency_name,
            'updated_at' : get_current_time()
        }

        result = await hotel_request_repository.cancel_hotel_request(db=db, request_dict = request_dict)
        if not result:
            raise HTTPException(status_code=400, detail="Update Hotel Request failed")
        return result
    except Exception as e:
        raise e


async def cancel_request_lead_agency_action(db:AsyncSession, request_id:int, agency_name:str, status:str):
    try:
        result = await hotel_request_repository.get_hotel_request_by_id(db=db, request_id=request_id)
        if not result:
            raise HTTPException(status_code=400, detail="Hotel Request not found")
        if result.cancel_request_status != 'REQUEST_FOR_CANCELLATION':
            raise HTTPException(status_code=400, detail="Can't Approved or Rejected")

        is_lead_agency = await admin_repository.check_lead_agency_for_specific_sub_agency(db=db, sub_agency=result.agency_name, lead_agency=agency_name)
        if not is_lead_agency:
            raise HTTPException(status_code=400, detail="This is not your sub agency")

        request_dict = {
            'id' : request_id,
            'updated_by' : agency_name,
            'updated_at' : get_current_time(),
            'cancel_request_status' : status if status == "REJECTED" else None,
        }

        result = await hotel_request_repository.cancel_request_lead_agency_action(db=db, request_dict=request_dict)
        if not result:
            raise HTTPException(status_code=400, detail="Update Hotel Request failed")
        return result
    except Exception as e:
        raise e