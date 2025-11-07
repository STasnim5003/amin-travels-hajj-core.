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