from fastapi import HTTPException
from sqlalchemy import insert, select, update, delete, text
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


async def sync_package_required_add_ons(db: AsyncSession, agency_name: str, old_name: str, new_name: str, new_price):
    # Packages keep a snapshot of add-on prices in required_add_ons ({name: price}); keep it in step with the catalog.
    # Keys are matched trimmed + case-insensitive so legacy keys like "Qurbani " are still found (and get cleaned).
    await db.execute(
        text("""
            UPDATE core.packages
            SET required_add_ons = (
                SELECT jsonb_object_agg(
                    CASE WHEN lower(btrim(e.key)) = :old_key THEN CAST(:new_name AS text) ELSE e.key END,
                    CASE WHEN lower(btrim(e.key)) = :old_key AND CAST(:new_price AS text) IS NOT NULL
                         THEN to_jsonb(CAST(CAST(:new_price AS text) AS numeric)) ELSE e.value END
                )
                FROM jsonb_each(required_add_ons) e
            )
            WHERE agency_name = :agency_name
              AND jsonb_typeof(required_add_ons) = 'object'
              AND EXISTS (
                  SELECT 1 FROM jsonb_object_keys(required_add_ons) k WHERE lower(btrim(k)) = :old_key
              )
        """),
        {
            "agency_name": agency_name,
            "old_key": old_name.strip().lower(),
            "new_name": new_name,
            "new_price": None if new_price is None else str(new_price),
        },
    )


async def update_add_ons_service(db, update_request_dict, package_sync: dict | None = None):
    try:
        if package_sync:
            await sync_package_required_add_ons(db, **package_sync)
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