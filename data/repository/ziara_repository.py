from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from data.model.ziara_model import ZiaraModel
from infrastructure.schema.ziara_schema import ZiaraCreateSchema


async def create_ziara(db: AsyncSession, ziara: ZiaraCreateSchema) -> ZiaraModel:
    new_ziara = ZiaraModel(**ziara.model_dump())
    db.add(new_ziara)
    await db.commit()
    await db.refresh(new_ziara)
    return new_ziara


async def get_ziara_by_id(db: AsyncSession, ziara_id: int) -> ZiaraModel:
    result = await db.execute(select(ZiaraModel).where(ZiaraModel.id == ziara_id))
    return result.scalar_one_or_none()



async def get_all_ziaras(db: AsyncSession, agency_name: str):
    result = await db.execute(select(ZiaraModel).where(ZiaraModel.agency_name == agency_name))
    return result.scalars().all()
