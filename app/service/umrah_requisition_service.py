from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from app.core.utils.umrah_requisition_utils import generate_amin_office_code
from data.repository import umrah_requisition_repository
from infrastructure.schema.umrah_requisition_schema import UmrahRequisitionBase, UmrahRequisitionResponseSchema, \
    UmrahRequisitionListResponseSchema, UmrahRequisitionAssignedService, UmrahRequisitionUpdateSchema, \
    UmrahVendorsPriceCreateSchema, UmrahVendorsPriceResponseSchema, \
    UmrahRequisitionWithVendorsPrice, UmrahRequisitionConfirmedPilgrimsInfoSchema


async def create_requisition(db: AsyncSession, request: UmrahRequisitionBase, agency_name: str, username: str):
    try:
        request_dict = request.model_dump()
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username
        request_dict['amin_office_code'] = await generate_amin_office_code(db=db)
        saved = await umrah_requisition_repository.create(db, request_dict)
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

        new_requisition = await umrah_requisition_repository.update_umrah_requisition(db, request_dict)
        return UmrahRequisitionResponseSchema.model_validate(new_requisition)
    except Exception as e:
        raise e


async def umrah_requisition_confirmation(db: AsyncSession, request: UmrahRequisitionConfirmedPilgrimsInfoSchema,
                                         agency_name: str, username: str):
    try:
        await requisition_availability_check(db=db, requisition_id=request.id, agency_name=agency_name)

        request_dict = request.model_dump(exclude_none=True)
        request_dict['is_confirmed'] = True
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()

        result = await umrah_requisition_repository.umrah_requisition_confirmation(db, request_dict)
        return UmrahRequisitionResponseSchema.model_validate(result)

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
        requisition = await umrah_requisition_repository.get_requisition_by_id(db, requisition_id, agency_name)

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


async def get_confirmed_pilgrims(db:AsyncSession, agency_name:str):
    try:
        result = await umrah_requisition_repository.get_confirmed_pilgrims(db=db, agency_name=agency_name)
    except Exception as e:
        raise e
