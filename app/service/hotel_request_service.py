from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from app.core.utils.get_current_time import get_current_time
from app.service import admin_service
from data.repository import hotel_request_repository, admin_repository
from infrastructure.schema.hotel_request_schema import HotelRequestBase, HotelRequestResponseSchema, \
    HotelRequestListResponseSchema, HotelRequestUpdateSchema, HotelRequestMergedResponseSchema


async def create_hotel_request(db: AsyncSession, request: HotelRequestBase, agency_name: str):
    try:
        agency = await admin_repository.get_agency_by_agency_name(db, agency_name)
        if agency is None:
            raise HTTPException(status_code=400, detail="Agency not found")

        request_dict = request.model_dump(exclude_none=True)
        request_dict["agency_name"] = agency_name
        request_dict["created_by"] = agency_name
        request_dict["updated_by"] = agency_name
        request_dict["status"] = "SEND_TO_LEAD"
        request_dict["sar"] = agency.sar - request.pricing.with_vat
        request_dict["hotel_requested"] = agency.hotel_requested + request.number_of_haji
        request_dict['rfq_no'] = agency.rfq_no

        if request.tent == 'Tent A':
            request_dict['rfq_no'] = 7276

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
        hotel_requests = [
            HotelRequestMergedResponseSchema.model_validate(item)
            for item in result
        ]

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


async def update_hotel_request(db: AsyncSession, request: HotelRequestUpdateSchema, agency_name: str):
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
        request_dict['updated_by'] = agency_name
        request_dict['updated_at'] = get_current_time()
        request_dict['agency_name'] = result.agency_name

        if result.pricing['with_vat'] != request.pricing.with_vat:
            agency = await admin_repository.get_agency_by_agency_name(db, agency_name)
            request_dict["sar"] = agency.sar - request.pricing.with_vat + result.pricing['with_vat']

        if result.number_of_haji != request.number_of_haji:
            agency = await admin_repository.get_agency_by_agency_name(db, agency_name)
            request_dict["hotel_requested"] = agency.hotel_requested + request.number_of_haji - result.number_of_haji

        result = await hotel_request_repository.update_hotel_request(db=db, request_dict=request_dict)
        return HotelRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_hotel_request(db: AsyncSession, request_id: int, agency_name: str):
    try:
        result = await hotel_request_repository.get_hotel_request_by_id(db=db, request_id=request_id)
        if not result:
            raise HTTPException(status_code=400, detail="Hotel Request not found")

        admin = await admin_repository.get_agency_by_agency_name(db=db, agency_name=agency_name)

        price = result.pricing.get('with_vat') or 0
        new_sar = admin.sar + price
        new_hotel_requested = admin.hotel_requested - result.number_of_haji

        request_dict = {
            'agency_name': agency_name,
            'sar': new_sar,
            'hotel_requested': new_hotel_requested
        }

        result = await hotel_request_repository.delete_hotel_request(db=db, request_id=request_id,
                                                                     request_dict=request_dict)
        if not result:
            raise HTTPException(status_code=400, detail="Delete Hotel Request failed")
        return result
    except Exception as e:
        raise e


async def cancel_request(db: AsyncSession, request_id: int, agency_name: str):
    try:
        result = await hotel_request_repository.get_hotel_request_by_id(db=db, request_id=request_id)
        if not result:
            raise HTTPException(status_code=400, detail="Hotel Request not found")
        if result.status == 'SEND_TO_LEAD':
            raise HTTPException(status_code=400, detail="Can't Cancel Request. Edit/Delete it")
        if result.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Agency name does not match")

        request_dict = {
            'cancel_request_status': "REQUEST_FOR_CANCELLATION",
            'id': request_id,
            'updated_by': agency_name,
            'updated_at': get_current_time()
        }

        result = await hotel_request_repository.cancel_hotel_request(db=db, request_dict=request_dict)
        if not result:
            raise HTTPException(status_code=400, detail="Update Hotel Request failed")
        return result
    except Exception as e:
        raise e


async def cancel_request_lead_agency_action(db: AsyncSession, request_id: int, agency_name: str, status: str):
    try:
        result = await hotel_request_repository.get_hotel_request_by_id(db=db, request_id=request_id)
        if not result:
            raise HTTPException(status_code=400, detail="Hotel Request not found")
        if result.cancel_request_status != 'REQUEST_FOR_CANCELLATION':
            raise HTTPException(status_code=400, detail="Can't Approved or Rejected")

        is_lead_agency = await admin_repository.check_lead_agency_for_specific_sub_agency(db=db,
                                                                                          sub_agency=result.agency_name,
                                                                                          lead_agency=agency_name)
        if not is_lead_agency:
            raise HTTPException(status_code=400, detail="This is not your sub agency")

        request_dict = {
            'id': request_id,
            'updated_by': agency_name,
            'updated_at': get_current_time(),
            'cancel_request_status': status if status == "REJECTED" else None,
        }

        result = await hotel_request_repository.cancel_request_lead_agency_action(db=db, request_dict=request_dict)
        if not result:
            raise HTTPException(status_code=400, detail="Update Hotel Request failed")
        return result
    except Exception as e:
        raise e
