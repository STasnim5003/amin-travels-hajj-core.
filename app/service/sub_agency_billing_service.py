from typing import Optional

from fastapi import HTTPException

from app.core.utils.get_current_time import get_current_time
from app.service import admin_service
from data.repository import admin_repository, sub_agency_billing_repository
from infrastructure.schema.payment_request_schema import SubAgencyBillCreateSchema, PaymentRequestResponse, \
    PaymentRequestListResponseSchema, SubAgencyBillUpdateSchema
from sqlalchemy.ext.asyncio import AsyncSession


async def create_sub_agency_bill(db:AsyncSession, request: SubAgencyBillCreateSchema, agency_name:str):
    try:
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")

        is_lead_agency = await admin_repository.check_lead_agency_for_specific_sub_agency(db=db, sub_agency=request.agency_name, lead_agency=agency_name)
        if not is_lead_agency:
            raise HTTPException(status_code=400, detail="This is not your sub agency")


        agency = await admin_repository.get_agency_by_agency_name(db=db, agency_name=request.agency_name)
        request_dict = request.model_dump(exclude_none=True)

        if request.purpose == 'BDT':
            new_bdt = agency.bdt + request.amount
            request_dict['bdt'] = new_bdt
        elif request.purpose == 'SAR':
            new_sar = agency.sar + request.exchanged_amount
            request_dict['sar'] = new_sar

        request_dict['created_by'] = agency_name
        request_dict['updated_by'] = agency_name
        request_dict['payment_way'] = "Bill"

        result = await sub_agency_billing_repository.create_sub_agency_bill(db=db, request_dict=request_dict)
        return PaymentRequestResponse.model_validate(result)

    except Exception as e:
        raise e


async def get_sub_agency_bill(db:AsyncSession, agency_name:str):
    try:
        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        result = await sub_agency_billing_repository.get_sub_agency_bill(db=db, agency_names=child_agencies)
        payment_requests = []

        for payment_request in result:
            payment_requests.append(PaymentRequestResponse.model_validate(payment_request))

        return PaymentRequestListResponseSchema(payment_requests=payment_requests)
    except Exception as e:
        raise e


async def update_sub_agency_bill(db:AsyncSession, request:SubAgencyBillUpdateSchema, agency_name:str):
    try:
        sub_agency_bill = await sub_agency_billing_repository.get_sub_agency_bill_by_id(db=db, bill_id=request.id)
        if not sub_agency_bill:
            raise HTTPException(status_code=400, detail="Sub agency bill not found")

        is_lead_agency = await admin_repository.check_lead_agency_for_specific_sub_agency(db=db, sub_agency=request.agency_name, lead_agency=agency_name)
        if not is_lead_agency:
            raise HTTPException(status_code=400, detail="This is not your sub agency")

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = agency_name
        request_dict['updated_at'] = get_current_time()

        result = await sub_agency_billing_repository.update_sub_agency_bill(db=db, request_dict = request_dict)
        return PaymentRequestResponse.model_validate(result)
    except Exception as e:
        raise e


async def delete_sub_agency_bill(db:AsyncSession, bill_id:int, agency_name:str):
    try:
        sub_agency_bill = await sub_agency_billing_repository.get_sub_agency_bill_by_id(db=db, bill_id=bill_id)
        if not sub_agency_bill:
            raise HTTPException(status_code=400, detail="Sub agency bill not found")

        is_lead_agency = await admin_repository.check_lead_agency_for_specific_sub_agency(db=db,
                                                                                          sub_agency=sub_agency_bill.agency_name,
                                                                                          lead_agency=agency_name)
        if not is_lead_agency:
            raise HTTPException(status_code=400, detail="This is not your sub agency")

        return await sub_agency_billing_repository.delete_sub_agency_bill(db=db, bill_id=bill_id)

    except Exception as e:
        raise e