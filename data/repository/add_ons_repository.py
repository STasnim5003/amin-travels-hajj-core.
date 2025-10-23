from fastapi import HTTPException
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.add_ons_service_model import AddOnsServiceModel


async def create_add_on_service(db: AsyncSession, service_data: dict):
    try:
        stmt = insert(AddOnsServiceModel).values(**service_data).returning(AddOnsServiceModel)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating add-on service: {str(e)}")


async def get_all_add_on_services(db: AsyncSession, agency_name: str):
    try:
        stmt = select(AddOnsServiceModel).where(AddOnsServiceModel.agency_name == agency_name)
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error getting all add-on services: {str(e)}")


async def get_add_on_service_by_id(db: AsyncSession, service_id: int, agency_name: str):
    stmt = select(AddOnsServiceModel).where(AddOnsServiceModel.id == service_id)
    result = await db.execute(stmt)
    service = result.scalar_one_or_none()
    if not service or service.agency_name != agency_name:
        raise HTTPException(status_code=400, detail=f"Add-on service with ID {service_id} not found")
    return service


async def update_add_ons_service(db, update_request_dict):
    try:
        result = await db.execute(
            update(AddOnsServiceModel)
            .where(AddOnsServiceModel.id == update_request_dict['id'])
            .values(**update_request_dict)
            .returning(AddOnsServiceModel)
        )

        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating add-on service: {str(e)}")

async def delete_add_ons_service(db:AsyncSession, service_id:int):
    try:
        await db.execute(
            delete(AddOnsServiceModel).where(AddOnsServiceModel.id == service_id)
        )

        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))