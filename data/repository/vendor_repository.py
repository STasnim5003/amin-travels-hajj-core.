from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.vendor_model import VendorModel


async def vendor_create(db:AsyncSession, request_dict: dict):
    try:
        result = await db.execute(
            insert(VendorModel)
            .values(**request_dict)
            .returning(VendorModel)
        )

        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_vendors(db:AsyncSession, category: str,agency_name:str):
    try:
        query = select(VendorModel).where(VendorModel.agency_name == agency_name)

        if category:
            query = query.where(VendorModel.category == category)

        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise e

async def get_vendor_by_id(db:AsyncSession, vendor_id: int, agency_name: str):
    try:
        query = (select(VendorModel)
                 .where(VendorModel.agency_name == agency_name, VendorModel.id == vendor_id))

        result = await db.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def update_vendor(db:AsyncSession, request_dict:dict):
    try:
        stmt = update(VendorModel).where(VendorModel.id == request_dict.get('id')).values(**request_dict).returning(VendorModel)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e

async def delete_vendor(db:AsyncSession, vendor_id: int):
    try:
        stmt = delete(VendorModel).where(VendorModel.id == vendor_id)
        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e