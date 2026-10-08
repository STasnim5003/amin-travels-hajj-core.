from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.customer_schema import CustomerCreateSchema, CustomerAppliedForRegistrationSchema


async def create_customer(db: AsyncSession, customer: CustomerCreateSchema, group_name: str, username:str):
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
            created_by=username,
            updated_by=username,
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


async def customer_applied_for_registration(db: AsyncSession, tracking_ids: CustomerAppliedForRegistrationSchema,
                                            group_name: str, username:str):
    try:
        ids = tracking_ids.tracking_ids

        check_stmt = select(PilgrimDataModel).where(
            PilgrimDataModel.tracking_id.in_(ids),
            or_(
                PilgrimDataModel.registration_status != "PREREGISTERED",
                PilgrimDataModel.allocation_status.not_in(("ASSIGNED", "UNASSIGNED")),
                PilgrimDataModel.group_name != group_name,
            )
        )
        result = await db.execute(check_stmt)
        invalid_rows = result.scalars().all()

        if invalid_rows:
            invalid_ids = [row.tracking_id for row in invalid_rows]
            raise HTTPException(status_code=400, detail=f"Error in this tracking ids: {invalid_ids}")

        stmt = (
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id.in_(ids))
            .values(
                registration_status="APPLIED",
                updated_by=username,
                updated_at=get_current_time(),
            )
            .returning(PilgrimDataModel)
        )
        result = await db.execute(stmt)
        updated_pilgrims = result.scalars().all()

        await db.commit()

        return updated_pilgrims

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating pilgrims: {str(e)}")
