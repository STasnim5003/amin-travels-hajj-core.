from sqlalchemy import select, update, insert
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


async def get_requisition_by_id(db:AsyncSession, requisition_id:int, agency_name:str):
    try:
        stmt = (
            select(UmrahRequisitionModel)
            .where(UmrahRequisitionModel.id == requisition_id, UmrahRequisitionModel.agency_name == agency_name)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def umrah_requisition_assign_service(db: AsyncSession, request_dict: dict):
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


async def create_vendors_price(db: AsyncSession, request_dict: dict):
    try:
        child_service = request_dict.pop('child_service')
        infant_service = request_dict.pop('infant_service')
        discount = request_dict.pop('discount')

        stmt = (
            insert(UmrahVendorsPriceModel)
            .values(**request_dict)
            .returning(UmrahVendorsPriceModel)
        )
        result = await db.execute(stmt)
        vendor_price = result.scalar_one_or_none()

        stmt = (
            update(UmrahRequisitionModel)
            .values(
                child_service=child_service,
                infant_service=infant_service,
                discount=discount
            )
            .where(UmrahRequisitionModel.id == request_dict.get('umrah_requisition_id'))
        )
        await db.execute(stmt)

        await db.commit()

        if vendor_price:
            vendor_price.child_service = child_service
            vendor_price.infant_service = infant_service
            vendor_price.discount = discount

        return vendor_price

    except Exception as e:
        await db.rollback()
        raise e


async def get_requisition_with_vendor_price(db: AsyncSession, requisition_id: int):
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


async def get_requisition_by_office_code(db: AsyncSession, office_code: str):
    try:
        stmt = (
            select(UmrahRequisitionModel.amin_office_code, UmrahRequisitionModel.total_price,
                   UmrahRequisitionModel.total_payment, UmrahRequisitionModel.discount)
            .where(UmrahRequisitionModel.amin_office_code == office_code)
        )
        result = await db.execute(stmt)
        return result.first()
    except Exception as e:
        raise e


async def check_requisition_availability(db:AsyncSession, requisition_id:int, agency_name:str):
    stmt = (
        select(UmrahRequisitionModel.id)
        .where(UmrahRequisitionModel.id == requisition_id, UmrahRequisitionModel.agency_name==agency_name)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
