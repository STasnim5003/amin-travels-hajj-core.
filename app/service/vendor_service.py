from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.repository import vendor_repository
from infrastructure.schema.vendor_schema import VendorCreateSchema, VendorResponseSchema, VendorListResponseSchema, \
    VendorUpdateSchema


async def create_vendor(db: AsyncSession, request: VendorCreateSchema, agency_name: str, username:str):
    try:
        request_dict = request.model_dump(exclude_none=True, exclude_unset=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username

        result = await vendor_repository.vendor_create(db=db, request_dict=request_dict)

        return VendorResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def get_vendors(db, category, agency_name):
    try:
        result = await vendor_repository.get_vendors(db=db, category=category, agency_name=agency_name)
        vendors = [VendorResponseSchema.model_validate(r) for r in result]

        return VendorListResponseSchema(vendors=vendors)
    except Exception as e:
        raise e


async def get_vendor(db: AsyncSession, vendor_id: int, agency_name: str):
    try:
        result = await vendor_repository.get_vendor_by_id(db=db, vendor_id=vendor_id, agency_name=agency_name)
        return VendorResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def update_vendor(db: AsyncSession, request: VendorUpdateSchema, agency_name: str, username:str):
    try:
        vendor = await vendor_repository.get_vendor_by_id(db=db, vendor_id=request.id, agency_name=agency_name)
        if not vendor:
            raise HTTPException(status_code=400, detail="Vendor Not found")

        request_dict = request.model_dump(exclude_none=True, exclude_unset=True)
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()

        result = await vendor_repository.update_vendor(db=db, request_dict=request_dict)
        return VendorResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_vendor(db: AsyncSession, vendor_id: int, agency_name: str):
    try:
        vendor = await vendor_repository.get_vendor_by_id(db=db, vendor_id=vendor_id, agency_name=agency_name)
        if not vendor:
            raise HTTPException(status_code=400, detail="Vendor Not found")

        result = await vendor_repository.delete_vendor(db=db, vendor_id=vendor_id)

        if result:
            return {"message": "Vendor Deleted Successfully"}
    except Exception as e:
        raise e
