from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.umrah_requisition_model import UmrahRequisitionModel


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