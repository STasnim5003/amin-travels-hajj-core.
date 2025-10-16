from fastapi import HTTPException
from sqlalchemy import select, case, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.payment_model import PaymentModel
from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.payment_schema import GroupLeaderPayableBaseSchema


async def create_payable_for_multiple_pilgrims(
        db: AsyncSession, payment_request: GroupLeaderPayableBaseSchema, agency_name: str
):
    try:
        tracking_ids = payment_request.pilgrims_tracking_id

        per_pilgrim_amount = 0
        if len(tracking_ids) > 0:
            per_pilgrim_amount = int(payment_request.amount / len(tracking_ids))

        pilgrims_result = await db.execute(
            select(PilgrimDataModel).where(PilgrimDataModel.tracking_id.in_(tracking_ids))
        )
        pilgrims = pilgrims_result.scalars().all()

        if not pilgrims:
            raise HTTPException(status_code=400, detail="No pilgrims found for the given tracking IDs")

        for pilgrim in pilgrims:
            if pilgrim.group_name != agency_name or pilgrim.group_leader != payment_request.group_leader:
                raise HTTPException(status_code=403, detail=f"Agency or group leader mismatched for {pilgrim.tracking_id}")

        case_total_payable = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                pilgrim.total_payable + per_pilgrim_amount
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_payable
        )

        case_total_due = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                max(0, (pilgrim.total_payable + per_pilgrim_amount) - (pilgrim.total_payment or 0))
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_due
        )

        case_total_available = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                max(0, (pilgrim.total_payment or 0) - (pilgrim.total_payable + per_pilgrim_amount))
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_available_amount
        )

        case_actual_payable = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                (pilgrim.actual_payable + per_pilgrim_amount)
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.actual_payable
        )

        await db.execute(
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id.in_(tracking_ids))
            .values(
                updated_by=agency_name,
                total_payable=case_total_payable,
                total_due=case_total_due,
                total_available_amount=case_total_available,
                actual_payable=case_actual_payable
            )
        )

        payment_request_dict = payment_request.model_dump()
        stmt = insert(PaymentModel).values(**payment_request_dict).returning(PaymentModel)
        result = await db.execute(stmt)

        await db.commit()
        return result.scalars().one_or_none()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

