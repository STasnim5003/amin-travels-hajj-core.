from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.customer_schema import CustomerCreateSchema


async def create_customer(db:AsyncSession, customer : CustomerCreateSchema, group_name : str):
    try:
        if customer.mobile_no:
            stmt = select(PilgrimDataModel).where(
                (PilgrimDataModel.mobile_no == customer.mobile_no) |
                (PilgrimDataModel.nid == customer.nid)
            )
        else:
            stmt = select(PilgrimDataModel).where(PilgrimDataModel.nid == customer.nid)

        result = await db.execute(stmt)
        existing = result.scalars().first()

        if existing:
            if customer.mobile_no and existing.mobile_no == customer.mobile_no:
                raise HTTPException(
                    status_code=400,
                    detail=f"User with mobile_no {customer.mobile_no} already exists."
                )
            if customer.nid and existing.nid == customer.nid:
                raise HTTPException(
                    status_code=400,
                    detail=f"User with nid {customer.nid} already exists."
                )

        pilgrim = PilgrimDataModel(
            **customer.model_dump(),
            group_name=group_name,
            created_by=group_name,
            updated_by=group_name,
            allocation_status="WALK_IN",
            is_assigned=False,
            registration_status="WALK_IN",
        )

        db.add(pilgrim)
        await db.commit()
        await db.refresh(pilgrim)

        return pilgrim

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )