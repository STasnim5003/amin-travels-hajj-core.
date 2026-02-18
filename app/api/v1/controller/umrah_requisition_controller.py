import fastapi
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import umrah_requisition_service
from data.db.db_config import get_async_db
from infrastructure.schema.umrah_requisition_schema import UmrahRequisitionResponseSchema, UmrahRequisitionBase, \
    UmrahRequisitionListResponseSchema, UmrahRequisitionAssignedService, UmrahRequisitionConfirmationSchema, \
    UmrahRequisitionUpdateSchema, UmrahVendorsPriceResponseSchema, UmrahVendorsPriceCreateSchema, \
    UmrahRequisitionWithVendorsPrice

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/umrah-requisition", response_model=UmrahRequisitionResponseSchema, tags = ['Umrah Requisition'])
async def create_umrah_requisition(
        request : UmrahRequisitionBase,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
) -> UmrahRequisitionResponseSchema:
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail='Unauthorized')
    agency_name = current_user['agency_name']
    return await umrah_requisition_service.create_requisition(db=db, request=request, agency_name=agency_name)

@private_router.get("/umrah-requisition", response_model=UmrahRequisitionListResponseSchema, tags=['Umrah Requisition'])
async def get_umrah_requisitions(
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
) -> UmrahRequisitionListResponseSchema:
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail='Unauthorized')
    agency_name = current_user['agency_name']

    return await umrah_requisition_service.get_umrah_requisitions(db=db, agency_name=agency_name)


@private_router.put("/umrah-requisition/assigned-service", response_model=UmrahRequisitionResponseSchema ,tags= ['Umrah Requisition'] )
async def assign_service_umrah_requisition(
        request : UmrahRequisitionAssignedService,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail='Unauthorized')
    agency_name = current_user['agency_name']
    return await umrah_requisition_service.umrah_requisition_assign_service(db=db, request=request, agency_name=agency_name)

@private_router.put("/umrah-requisition/confirmation", response_model=UmrahRequisitionResponseSchema, tags=['Umrah Requisition'])
async def confirm_umrah_requisition(
        request: UmrahRequisitionConfirmationSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail='Unauthorized')
    agency_name = current_user['agency_name']
    return await umrah_requisition_service.umrah_requisition_confirmation(db=db, request=request, agency_name=agency_name)

@private_router.put("/umrah-requisition", response_model=UmrahRequisitionResponseSchema, tags=['Umrah Requisition'])
async def update_umrah_requisition(
        request: UmrahRequisitionUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
) -> UmrahRequisitionResponseSchema:
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail='Unauthorized')
    agency_name = current_user['agency_name']
    return await umrah_requisition_service.umrah_requisition_update(db, request, agency_name)

@private_router.get("/umrah-requisition/{requisition_id}", response_model=UmrahRequisitionResponseSchema, tags=['Umrah Requisition'])
async def get_umrah_requisition_by_id(
        requisition_id : int,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail='Unauthorized')
    agency_name = current_user['agency_name']

    return await umrah_requisition_service.get_umrah_requisition_by_id(db=db, requisition_id=requisition_id, agency_name=agency_name)

@private_router.post("/umrah-vendors-price", response_model=UmrahVendorsPriceResponseSchema, tags=['Umrah Requisition'])
async def create_vendors_price(
        request : UmrahVendorsPriceCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail='Unauthorized')
    agency_name = current_user['agency_name']

    return await umrah_requisition_service.create_vendors_price(db=db, request=request, agency_name=agency_name)

@private_router.get("/umrah-requisition-with-vendors-price/{umrah_requisition_id}", response_model=UmrahRequisitionWithVendorsPrice,tags=['Umrah Requisition'])
async def get_vendors_price_by_umrah_requisition_id(
        umrah_requisition_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail='Unauthorized')
    agency_name = current_user['agency_name']
    return await umrah_requisition_service.get_requisitions_with_vendors_price(db=db, requisition_id=umrah_requisition_id, agency_name=agency_name)