from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from app.core.utils.umrah_requisition_utils import generate_amin_office_code
from data.repository import umrah_requisition_repository, umrah_b2b_payment_repository, admin_user_repository
from infrastructure.schema.umrah_requisition_schema import UmrahRequisitionBase, UmrahRequisitionResponseSchema, \
    UmrahRequisitionListResponseSchema, UmrahRequisitionAssignedService, UmrahRequisitionUpdateSchema, \
    UmrahVendorsPriceCreateSchema, UmrahVendorsPriceResponseSchema, \
    UmrahRequisitionWithVendorsPrice


async def create_requisition(db: AsyncSession, request: UmrahRequisitionBase, agency_name: str, username: str):
    try:
        amin_office_code = await generate_amin_office_code(db=db)
        b2b_payment_dict={}

        request_dict = request.model_dump()
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username
        request_dict['amin_office_code'] = amin_office_code
        request_dict['is_confirmed'] = False

        if request.b2b_type and request.b2b_type == 'PARTIAL':
            request_dict['is_confirmed'] = True
            request_dict['is_child_included_with_bed_transport'] = False
            request_dict['total_due'] = request.total_price

            b2b_payment_dict.update({
                'b2b_agent_name': request.b2b_agent_name,
                'office_code': amin_office_code,
                'amount': request.total_price,
                'paid_amount': 0,
                'due': request.total_price,
                'agency_name': agency_name,
                'created_by': username,
                'updated_by': username
            })



        saved = await umrah_requisition_repository.create(db=db, request_dict=request_dict, b2b_payment_dict=b2b_payment_dict)
        return UmrahRequisitionResponseSchema.model_validate(saved)
    except Exception as e:
        raise e


async def get_umrah_requisitions(db: AsyncSession, agency_name: str):
    try:
        result = await umrah_requisition_repository.get_umrah_requisitions(db, agency_name)

        umrah_requisitions = [UmrahRequisitionResponseSchema.model_validate(r) for r in result]
        return UmrahRequisitionListResponseSchema(umrah_requisitions=umrah_requisitions)
    except Exception as e:
        raise e


async def get_umrah_requisition_by_id(db, requisition_id, agency_name):
    try:
        result = await umrah_requisition_repository.get_requisition_by_id(db, requisition_id, agency_name)
        return UmrahRequisitionResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def umrah_requisition_assign_service(db: AsyncSession, request: UmrahRequisitionAssignedService,
                                           agency_name: str, username: str):
    try:
        requisition = await umrah_requisition_repository.get_requisition_by_id(db, request.id, agency_name)

        if not requisition:
            raise HTTPException(status_code=400, detail='Umrah Requisition not found')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()
        request_dict['is_confirmed'] = False
        request_dict['total_due'] = max(0, request_dict['total_price'] - (
                requisition.total_payment + request_dict['discount']))

        result = await umrah_requisition_repository.umrah_requisition_assign_service(db, request_dict)
        return UmrahRequisitionResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def umrah_requisition_update(db: AsyncSession, request: UmrahRequisitionUpdateSchema, agency_name: str,
                                   username: str):
    try:
        await requisition_availability_check(db=db, requisition_id=request.id, agency_name=agency_name)

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()

        requisition = await umrah_requisition_repository.get_requisition_by_id(db=db, requisition_id=request.id, agency_name=agency_name)
        b2b_partial_invoice_finance_update={}
        if request.b2b_type and request.b2b_type == 'PARTIAL':
            umrah_b2b_payment_invoice = await umrah_b2b_payment_repository.get_umrah_b2b_invoices_by_office_code(db=db, office_code=requisition.amin_office_code)

            new_amount = request.total_price
            paid_amount = umrah_b2b_payment_invoice.paid_amount

            b2b_partial_invoice_finance_update.update({
                "office_code": requisition.amin_office_code,
                "amount": new_amount,
                "due": max(0, new_amount - paid_amount),
                "updated_by": username,
            })

        new_requisition = await umrah_requisition_repository.update_umrah_requisition(db, request_dict, b2b_partial_invoice_finance_update)
        return UmrahRequisitionResponseSchema.model_validate(new_requisition)
    except Exception as e:
        raise e


async def create_vendors_price(db: AsyncSession, request: UmrahVendorsPriceCreateSchema, agency_name: str,
                               username: str):
    try:
        await requisition_availability_check(db=db, requisition_id=request.umrah_requisition_id,
                                             agency_name=agency_name)
        request_dict = request.model_dump(exclude_none=True)
        request_dict['created_by'] = username
        request_dict['updated_by'] = username

        result = await umrah_requisition_repository.create_vendors_price(db=db, request_dict=request_dict)
        return UmrahVendorsPriceResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def requisition_availability_check(db: AsyncSession, requisition_id: int, agency_name: str):
    try:
        requisition = await umrah_requisition_repository.check_requisition_availability(db, requisition_id, agency_name)

        if not requisition:
            raise HTTPException(status_code=400, detail='Umrah Requisition not found')

    except Exception as e:
        raise e


async def get_requisitions_with_vendors_price(db: AsyncSession, requisition_id: int, agency_name: str):
    try:
        requisition, vendors_price = await umrah_requisition_repository.get_requisition_with_vendor_price(db=db,
                                                                                                          requisition_id=requisition_id)

        return UmrahRequisitionWithVendorsPrice(
            requisition=UmrahRequisitionResponseSchema.model_validate(requisition),
            vendors_price=(
                UmrahVendorsPriceResponseSchema.model_validate(vendors_price)
                if vendors_price else None
            )
        )
    except Exception as e:
        raise e


async def create_public_requisition(db, request, agency_name):
    try:
        amin_office_code = await generate_amin_office_code(db=db)

        agency_staffs = await admin_user_repository.get_agency_staffs(db=db, agency_name=agency_name)

        if not agency_staffs:
            raise ValueError(
                f"No agency staff found for agency: {agency_name}"
            )

        # Round-robin:
        # 1. Staff with latest_assign_time = None gets priority
        # 2. Otherwise, staff with the earliest assignment time gets priority
        latest_assigned_staff = min(
            agency_staffs,
            key=lambda staff: (
                staff.latest_assign_time is not None,
                staff.latest_assign_time or datetime.min.replace(tzinfo=timezone.utc)
            )
        )

        assign_to = latest_assigned_staff.username

        request_dict = request.model_dump()
        request_dict["agency_name"] = agency_name
        request_dict["amin_office_code"] = amin_office_code
        request_dict["is_confirmed"] = False
        request_dict["assign_to"] = assign_to
        request_dict["created_by"] = "public"
        request_dict["updated_by"] = "public"

        saved = await umrah_requisition_repository.create_public_requisition(db=db, request_dict=request_dict)

        return {
            "message": "Umrah requisition created successfully",
            "assign_to": saved.name,
            "contract_no": saved.mobile_no
        }
    except Exception as e:
        raise e