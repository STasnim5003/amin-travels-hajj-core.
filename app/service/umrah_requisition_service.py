from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import umrah_requisition_repository
from infrastructure.schema.umrah_requisition_schema import UmrahRequisitionBase, UmrahRequisitionResponseSchema, \
    UmrahRequisitionListResponseSchema, UmrahRequisitionAssignedService, UmrahRequisitionConfirmationSchema, \
    UmrahRequisitionUpdateSchema


async def create_requisition(db: AsyncSession, request: UmrahRequisitionBase, agency_name: str):
    try:
        request_dict = request.model_dump()
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = agency_name
        request_dict['updated_by'] = agency_name

        saved = await umrah_requisition_repository.create(db, request_dict)
        return UmrahRequisitionResponseSchema.model_validate(saved)
    except Exception as e:
        raise e


async def get_umrah_requisitions(db:AsyncSession, agency_name:str):
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


async def umrah_requisition_assign_service(db:AsyncSession, request:UmrahRequisitionAssignedService, agency_name:str):
    try:
        requisition = await umrah_requisition_repository.get_requisition_by_id(db, request.id, agency_name)
        if not requisition:
            raise HTTPException(status_code=400, detail='Umrah Requisition not found')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = agency_name
        request_dict['updated_at'] = datetime.now() + timedelta(hours=6)

        result = await umrah_requisition_repository.umrah_requisition_assign_service(db, request_dict)
        return UmrahRequisitionResponseSchema.model_validate(result)
    except Exception as e:
        raise e

async def umrah_requisition_update(db:AsyncSession, request:UmrahRequisitionUpdateSchema, agency_name:str):
    try:
        requisition = await umrah_requisition_repository.get_requisition_by_id(db, request.id, agency_name)
        if not requisition:
            raise HTTPException(status_code=400, detail='Umrah Requisition not found')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = agency_name
        request_dict['updated_at'] = datetime.now() + timedelta(hours=6)

        new_requisition = await umrah_requisition_repository.update_umrah_requisition(db, request_dict)
        return UmrahRequisitionResponseSchema.model_validate(new_requisition)
    except Exception as e:
        raise e


async def umrah_requisition_confirmation(db:AsyncSession, request:UmrahRequisitionConfirmationSchema, agency_name:str):
    try:
        requisition = await umrah_requisition_repository.get_requisition_by_id(db, request.id, agency_name)

        if not requisition:
            raise HTTPException(status_code=400, detail='Umrah Requisition not found')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = agency_name
        request_dict['updated_at'] = datetime.now() + timedelta(hours=6)

        result = await umrah_requisition_repository.umrah_requisition_confirmation(db, request_dict)
        return UmrahRequisitionResponseSchema.model_validate(result)

    except Exception as e:
        raise e