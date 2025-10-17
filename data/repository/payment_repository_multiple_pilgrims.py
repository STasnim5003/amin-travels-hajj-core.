from fastapi import HTTPException
from sqlalchemy import select, case, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.payment_model import PaymentModel
from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.payment_schema import GroupLeaderPayableBaseSchema, GroupLeaderPaymentBaseSchema, \
    PaymentUpdateSchema, PayableInfoUpdateSchema


async def create_payable_for_multiple_pilgrims(
        db: AsyncSession, payment_request: dict, agency_name: str, payable_info: PayableInfoUpdateSchema
):
    try:
        tracking_ids = payment_request["pilgrims_tracking_id"]

        per_pilgrim_amount = 0
        if len(tracking_ids) > 0:
            per_pilgrim_amount = int(payment_request["amount"] / len(tracking_ids))

        pilgrims_result = await db.execute(
            select(PilgrimDataModel).where(PilgrimDataModel.tracking_id.in_(tracking_ids))
        )
        pilgrims = pilgrims_result.scalars().all()

        if not pilgrims:
            raise HTTPException(status_code=400, detail="No pilgrims found for the given tracking IDs")

        for pilgrim in pilgrims:
            if pilgrim.group_name != agency_name or pilgrim.group_leader != payment_request["group_leader"]:
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

        stmt = insert(PaymentModel).values(**payment_request).returning(PaymentModel)
        result = await db.execute(stmt)

        await db.execute(
            update(AdminUserModel)
            .where(AdminUserModel.code == payable_info.group_leader_code)
            .values(
                updated_by=agency_name,
                total_payable=payable_info.total_payable,
                total_due=payable_info.total_due,
                total_available_amount=payable_info.total_available_amount
            )
        )

        await db.commit()
        return result.scalars().one_or_none()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

async def create_payment_for_multiple_pilgrims(db: AsyncSession, payment_request:dict, agency_name:str, payment_info:PayableInfoUpdateSchema):
    try:
        tracking_ids = payment_request["pilgrims_tracking_id"]

        per_pilgrim_amount = 0
        if len(tracking_ids) > 0:
            per_pilgrim_amount = int(payment_request["amount"] / len(tracking_ids))

        pilgrims_result = await db.execute(
            select(PilgrimDataModel).where(PilgrimDataModel.tracking_id.in_(tracking_ids))
        )
        pilgrims = pilgrims_result.scalars().all()

        if not pilgrims:
            raise HTTPException(status_code=400, detail="No pilgrims found for the given tracking IDs")

        for pilgrim in pilgrims:
            if pilgrim.group_name != agency_name or pilgrim.group_leader != payment_request["group_leader"]:
                raise HTTPException(status_code=403, detail=f"Agency or group leader mismatched for {pilgrim.tracking_id}")

        case_total_payment = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                pilgrim.total_payment + per_pilgrim_amount
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_payment
        )

        case_total_due = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                max(0, pilgrim.total_payable - (per_pilgrim_amount + pilgrim.total_payment or 0))
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_due
        )

        case_total_available = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                max(0, (per_pilgrim_amount + pilgrim.total_payment or 0) - pilgrim.total_payable)
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_available_amount
        )


        await db.execute(
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id.in_(tracking_ids))
            .values(
                updated_by=agency_name,
                total_payment=case_total_payment,
                total_due=case_total_due,
                total_available_amount=case_total_available
            )
        )

        stmt = insert(PaymentModel).values(**payment_request).returning(PaymentModel)
        result = await db.execute(stmt)

        await db.execute(
            update(AdminUserModel)
            .where(AdminUserModel.code == payment_info.group_leader_code)
            .values(
                updated_by=agency_name,
                total_payment=payment_info.total_payment,
                total_due=payment_info.total_due,
                total_available_amount=payment_info.total_available_amount
            )
        )

        await db.commit()
        return result.scalars().one_or_none()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

