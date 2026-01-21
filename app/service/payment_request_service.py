from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from app.core.utils.get_current_time import get_current_time
from app.service import admin_service
from data.repository import payment_request_repository, admin_repository
from infrastructure.schema.payment_request_schema import PaymentRequestResponse, \
    PaymentRequestListResponseSchema, PaymentRequestCreateSchema, PaymentRequestUpdateSchema


async def create_payment_request(db: AsyncSession, request: PaymentRequestCreateSchema, agency_name: str):
    try:
        request_dict = request.model_dump(exclude_none=True)
        request_dict['status'] = 'PENDING'
        request_dict['agency_name'] = agency_name
        request_dict['updated_by'] = agency_name
        request_dict['created_by'] = agency_name

        result = await payment_request_repository.create_payment_request(db=db, request_dict=request_dict)
        return PaymentRequestResponse.model_validate(result)
    except Exception as e:
        raise e


async def get_payment_requests(db: AsyncSession, agency_name: str):
    try:
        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        result = await payment_request_repository.get_payment_requests(db=db, agency_names=child_agencies)
        payment_requests = []

        for payment_request in result:
            payment_requests.append(PaymentRequestResponse.model_validate(payment_request))

        return PaymentRequestListResponseSchema(payment_requests=payment_requests)
    except Exception as e:
        raise e


async def get_payment_request_by_id(db: AsyncSession, payment_request_id: int, agency_name: str):
    try:
        result = await payment_request_repository.get_payment_request_by_id(db=db,
                                                                            payment_request_id=payment_request_id)
        if not result:
            raise HTTPException(status_code=400, detail='Payment request not found')

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if result.agency_name not in child_agencies:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        if result.money_receipt_payment_slip_file:
            result.money_receipt_payment_slip_file = await generate_downloadable_urls(
                result.money_receipt_payment_slip_file)

        return PaymentRequestResponse.model_validate(result)
    except Exception as e:
        raise e


async def update_payment_request(db: AsyncSession, request: PaymentRequestUpdateSchema, agency_name: str):
    try:
        result = await payment_request_repository.get_payment_request_by_id(db=db,
                                                                            payment_request_id=request.id)
        if not result:
            raise HTTPException(status_code=400, detail='Payment request not found')

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if result.agency_name not in child_agencies:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        agency = await admin_repository.get_agency_by_agency_name(db=db, agency_name=result.agency_name)
        if not agency:
            raise HTTPException(status_code=400, detail='No Agency Found')

        request_dict = request.model_dump(exclude_none=True)

        is_lead_agency = await admin_repository.check_lead_agency(db=db, agency_name=agency_name)
        status = request.status
        if not is_lead_agency and status in ['APPROVED', 'REJECTED']:
            raise HTTPException(status_code=400, detail='You are not lead agency')

        if is_lead_agency and request.status == 'APPROVED':
            if request.purpose == 'BDT':
                new_bdt = agency.bdt + request.amount
                request_dict['bdt'] = new_bdt
            elif request.purpose == 'SAR':
                new_sar = agency.sar + request.exchanged_amount
                request_dict['sar'] = new_sar

        request_dict['agency_name'] = result.agency_name
        request_dict['updated_by'] = agency_name
        request_dict['updated_at'] = get_current_time()

        result = await payment_request_repository.update_payment_request(db=db, request_dict=request_dict)
        return PaymentRequestResponse.model_validate(result)
    except Exception as e:
        raise e


async def delete_payment_request(db: AsyncSession, payment_request_id: int, agency_name: str):
    try:
        payment_request = await payment_request_repository.get_payment_request_by_id(db, payment_request_id)
        if not payment_request:
            raise HTTPException(status_code=400, detail='Payment request not found')
        if payment_request.agency_name != agency_name:
            raise HTTPException(status_code=400, detail='You can not delete other payment request')

        return await payment_request_repository.delete_payment_request(db=db, payment_request_id=payment_request_id)

    except Exception as e:
        raise e
