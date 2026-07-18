from fastapi import HTTPException
from sqlalchemy import insert, update, select, text, func, exists
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.payment_model import PaymentModel
from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.payment_schema import PayableInfoUpdateSchema


async def create_payable_for_pilgrim(
        db: AsyncSession,
        payment_request: dict,
        payable_update_info: PayableInfoUpdateSchema
):
    try:
        # Create Payable
        stmt = (
            insert(PaymentModel)
            .values(**payment_request)
            .returning(PaymentModel)
        )
        result = await db.execute(stmt)
        created_payment = result.scalar_one()

        # Update Payment Info for Pilgrim
        update_stmt = (
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id == payment_request["tracking_id"])
            .values(
                total_payable=payable_update_info.total_payable,
                total_due=payable_update_info.total_due,
                total_available_amount=payable_update_info.total_available_amount,
                actual_payable=payable_update_info.actual_payable,
                updated_by=payment_request["updated_by"]
            )
        )
        await db.execute(update_stmt)
        await db.commit()
        return created_payment
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def create_payment_for_pilgrim(
        db: AsyncSession,
        payment_request: dict
):
    try:
        stmt = (
            insert(PaymentModel)
            .values(**payment_request)
            .returning(PaymentModel)
        )
        result = await db.execute(stmt)

        # stmt = (
        #     update(PilgrimDataModel)
        #     .values(
        #         total_payment=payment_info.total_payment,
        #         total_due=payment_info.total_due,
        #         total_available_amount=payment_info.total_available_amount,
        #         tracking_id=payment_info.tracking_id,
        #     )
        #     .where(PilgrimDataModel.tracking_id == payment_info.tracking_id)
        # )
        # res = await db.execute(stmt)
        await db.commit()
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise e


async def get_payments_by_tracking_id(
        db: AsyncSession,
        tracking_id: str,
        page: int = 1,
        size: int = 100
):
    try:
        offset = (page - 1) * size

        query = text("""
            SELECT
                p.id AS id,
                p.description AS description,
                p.date AS date,
                p.amount AS amount,
                p.category AS category,
                p.tracking_id,
                p.group_leader,
                p.transaction_id AS transaction_id,
                p.created_at AS created_at,
                p.created_by AS created_by,
                p.updated_at AS updated_at,
                p.updated_by AS updated_by,
                p.agency_name AS agency_name,
                pd.total_payable AS pilgrim_total_payable,
                pd.total_payment AS pilgrim_total_payment,
                pd.total_due AS pilgrim_total_due,
                pd.total_available_amount AS pilgrim_total_available_amount
            FROM core.payment p
            LEFT JOIN core.pilgrim_data pd
                ON pd.tracking_id = p.tracking_id
            WHERE p.tracking_id = :tracking_id
            GROUP BY p.id, pd.tracking_id, pd.total_payable, pd.total_available_amount, pd.total_due, pd.total_payment
            ORDER BY p.id DESC
            LIMIT :size OFFSET :offset;
        """)

        result = await db.execute(
            query,
            {"tracking_id": tracking_id, "size": size, "offset": offset}
        )

        payments = result.mappings().all()  # returns a list of dict-like rows

        if not payments:
            raise HTTPException(status_code=400, detail="No payments found for this tracking ID")

        total_query = text("""
                    SELECT COUNT(*) FROM core.payment
                    WHERE tracking_id = :tracking_id
                """)
        total_result = await db.execute(total_query, {"tracking_id": tracking_id})
        total = total_result.scalar() or 0

        first = payments[0]
        pilgrim_total_payable = first["pilgrim_total_payable"]
        pilgrim_total_payment = first["pilgrim_total_payment"]
        pilgrim_total_due = first["pilgrim_total_due"]
        pilgrim_total_available_amount = first["pilgrim_total_available_amount"]

        return payments, total, pilgrim_total_payable, pilgrim_total_payment, pilgrim_total_due, pilgrim_total_available_amount

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def create_payable_for_package_change(db: AsyncSession, payable_info: dict):
    try:
        stmt = (
            update(PaymentModel)
            .where(PaymentModel.tracking_id == payable_info.get('tracking_id'), PaymentModel.category == 'Payable')
            .values(**payable_info)
        )
        await db.execute(stmt)
    except Exception as e:
        raise e


async def get_group_leader_payable_report_data(db: AsyncSession, group_leader: str):
    try:
        stmt = (
            select(
                PilgrimDataModel.package_name,
                PilgrimDataModel.package_duration,
                PilgrimDataModel.package_bed_types,
                func.count().label("total_haji"),
                func.sum(PilgrimDataModel.actual_payable).label("total_actual_payable")
            )
            .where(PilgrimDataModel.group_leader == group_leader)
            .group_by(
                PilgrimDataModel.package_name,
                PilgrimDataModel.package_duration,
                PilgrimDataModel.package_bed_types
            )
            .order_by(
                PilgrimDataModel.package_name
            )
        )

        result = await db.execute(stmt)
        return result.all()
    except Exception as e:
        raise e


async def get_pilgrim_payment_ledger(db: AsyncSession, tracking_id: str):
    try:
        stmt = (
            select(PaymentModel)
            .where(PaymentModel.tracking_id == tracking_id)
        )

        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e


async def is_voucher_no_exist(db: AsyncSession, voucher_no: str) -> bool:
    stmt = select(
        exists().where(PaymentModel.voucher_no == voucher_no)
    )

    result = await db.execute(stmt)
    return result.scalar()


async def get_pilgrims_payment_summary(db: AsyncSession, agency_name: str):
    try:
        query = text("""
            SELECT 
                tracking_id,
                name_en,
                mobile_no,
                actual_payable,
                total_payment,
                total_due,
                family_code
            FROM core.pilgrim_data
            WHERE group_name = :agency_name
            AND registration_status = 'REGISTERED'
            ORDER BY family_code
        """)

        result = await db.execute(query, {"agency_name": agency_name})
        rows = result.mappings().all()

        return rows

    except Exception as e:
        raise e
