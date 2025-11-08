from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.transport_model import TransportServiceModel


async def create_transport_service(db: AsyncSession, request_dict: dict):
    stmt = (
        insert(TransportServiceModel)
        .values(**request_dict)
        .returning(TransportServiceModel)
    )
    result = await db.execute(stmt)
    await db.commit()
    row = result.scalar_one_or_none()
    return row



async def get_transport_services(db: AsyncSession, agency_name: str):
    stmt = select(TransportServiceModel).where(TransportServiceModel.agency_name == agency_name, TransportServiceModel.is_active == True)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_transport_service_by_id(db:AsyncSession, service_id : int, agency_name : str):
    stmt = select(TransportServiceModel).where(TransportServiceModel.id == service_id, TransportServiceModel.agency_name == agency_name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_transport_service(db: AsyncSession, transport_id: int, update_data: dict):
    stmt = (
        update(TransportServiceModel)
        .where(TransportServiceModel.id == transport_id)
        .values(**update_data)
        .returning(TransportServiceModel)
    )
    result = await db.execute(stmt)
    await db.commit()
    row = result.scalar_one_or_none()
    return row

async def delete_transport_service(db: AsyncSession, transport_id: int):
    stmt = delete(TransportServiceModel).where(TransportServiceModel.id == transport_id)
    await db.execute(stmt)
    await db.commit()
    return True
