from typing import Optional

import fastapi
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import vendor_service
from data.db.db_config import get_async_db
from infrastructure.schema.vendor_schema import VendorResponseSchema, VendorCreateSchema, VendorListResponseSchema, \
    VendorUpdateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=['Vendor'])

@private_router.post("/vendor", response_model=VendorResponseSchema)
async def create_vendor(
        request: VendorCreateSchema,
        db:AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> VendorResponseSchema:
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user['agency_name']

    return await vendor_service.create_vendor(db=db, request=request, agency_name=agency_name)

@private_router.get("/vendor", response_model=VendorListResponseSchema)
async def get_vendor(
        category: Optional[str] = None,
        db:AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> VendorListResponseSchema:
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user['agency_name']
    return await vendor_service.get_vendors(db=db, category = category, agency_name=agency_name)

@private_router.get("/vendor/{vendor_id}", response_model=VendorResponseSchema)
async def get_vendor(
        vendor_id: int,
        db:AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> VendorResponseSchema:
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user['agency_name']
    return await vendor_service.get_vendor(db=db, vendor_id=vendor_id, agency_name=agency_name)

@private_router.put("/vendor", response_model=VendorResponseSchema)
async def update_vendor(
        request: VendorUpdateSchema,
        db:AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> VendorResponseSchema:
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user['agency_name']
    return await vendor_service.update_vendor(db=db, request=request, agency_name=agency_name)

@private_router.delete("/vendor/{vendor_id}")
async def delete_vendor(
        vendor_id: int,
        db:AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user['agency_name']
    return await vendor_service.delete_vendor(db=db, vendor_id=vendor_id, agency_name=agency_name)