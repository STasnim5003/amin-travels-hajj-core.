from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.umrah_requisition_model import UmrahRequisitionModel, UmrahVendorsPriceModel


async def create(db: AsyncSession, data: dict):
    try:
        stmt = (
            insert(UmrahRequisitionModel)
            .values(**data)
            .returning(UmrahRequisitionModel)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_requisitions(db, agency_name):
    try:
        stmt = (
            select(UmrahRequisitionModel)
            .where(UmrahRequisitionModel.agency_name == agency_name)
            .order_by(UmrahRequisitionModel.id.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_requisition_by_id(db, requisition_id, agency_name):
    try:
        stmt = (
            select(UmrahRequisitionModel)
            .where(UmrahRequisitionModel.id == requisition_id, UmrahRequisitionModel.agency_name == agency_name)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def umrah_requisition_assign_service(db:AsyncSession, request_dict:dict):
    try:
        stmt = (update(UmrahRequisitionModel)
                .where(UmrahRequisitionModel.id == request_dict.get('id'))
                .values(**request_dict)
                .returning(UmrahRequisitionModel))
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def umrah_requisition_confirmation(db:AsyncSession, request_dict:dict):
    try:
        stmt = (
            update(UmrahRequisitionModel)
            .where(UmrahRequisitionModel.id == request_dict.get('id'))
            .values(**request_dict)
            .returning(UmrahRequisitionModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def update_umrah_requisition(db: AsyncSession, request_dict: dict):
    try:
        stmt = (
            update(UmrahRequisitionModel)
            .where(UmrahRequisitionModel.id == request_dict.get("id"))
            .values(**request_dict)
            .returning(UmrahRequisitionModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()

    except Exception as e:
        await db.rollback()
        raise e


async def create_vendors_price(db:AsyncSession, request_dict: dict):
    try:
        stmt = (
            insert(UmrahVendorsPriceModel)
            .values(**request_dict)
            .returning(UmrahVendorsPriceModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def get_requisition_with_vendor_price(db:AsyncSession, requisition_id:int):
    try:
        stmt = (
            select(UmrahRequisitionModel, UmrahVendorsPriceModel)
            .join(
                UmrahVendorsPriceModel,
                UmrahVendorsPriceModel.umrah_requisition_id == UmrahRequisitionModel.id,
                isouter=True  # LEFT JOIN (so requisition still returns if no price)
            )
            .where(UmrahRequisitionModel.id == requisition_id)
        )

        result = await db.execute(stmt)
        row = result.first()

        requisition, vendors_price = row
        return requisition, vendors_price
    except Exception as e:
        raise e


async def get_requisition_by_requisition_code(db:AsyncSession, umrah_requisition_code:str):
    try:
        stmt = (
            select(UmrahRequisitionModel.umrah_requisition_code, UmrahRequisitionModel.total_price, UmrahRequisitionModel.total_payment)
            .where(UmrahRequisitionModel.umrah_requisition_code == umrah_requisition_code)
        )
        result = await db.execute(stmt)
        return result.first()
    except Exception as e:
        raise e


def get_confirmed_pilgrims(db, agency_name):
    return None