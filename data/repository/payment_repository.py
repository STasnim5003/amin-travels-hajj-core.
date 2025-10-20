from datetime import datetime, timedelta

import pytz
from fastapi import HTTPException
from sqlalchemy import insert, select, update, text, desc, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.bank_info_model import BankInfoModel
from data.model.payment_model import PaymentModel
from infrastructure.schema.payment_schema import PayableInfoUpdateSchema


async def create_payable_for_group_leader(db: AsyncSession, payment_request: dict,
                                          payable_info: PayableInfoUpdateSchema, agency_name: str):
    try:
        # Insert into payment_info
        stmt = (
            insert(PaymentModel)
            .values(**payment_request)
            .returning(PaymentModel)
        )
        result = await db.execute(stmt)

        stmt = (
            update(AdminUserModel)
            .values(
                updated_by=agency_name,
                total_payable=payable_info.total_payable,
                total_due=payable_info.total_due,
                total_available_amount=payable_info.total_available_amount
            )
            .where(AdminUserModel.code == payable_info.group_leader_code)
        )

        await db.execute(stmt)
        await db.commit()

        created_payment = result.scalar_one()
        return created_payment

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error creating payment record")


async def create_payment_for_group_leader(db: AsyncSession, payment_data: dict, agency_name: str,
                                          payment_info: PayableInfoUpdateSchema):
    try:

        #  Insert into payment table
        stmt = (
            insert(PaymentModel)
            .values(**payment_data)
            .returning(PaymentModel)
        )

        result = await db.execute(stmt)
        created_payment = result.scalar_one()

        await db.execute(
            update(AdminUserModel)
            .values(
                total_payment=payment_info.total_payment,
                total_due=payment_info.total_due,
                total_available_amount=payment_info.total_available_amount,
                updated_by=agency_name
            )
            .where(AdminUserModel.code == payment_info.group_leader_code)
        )
        await db.commit()
        return created_payment

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating group leader payment: {str(e)}")


async def get_payments_by_group_leader(
        db: AsyncSession,
        group_leader: str,
        category: str | None,
        page: int,
        size: int
):
    try:
        offset = (page - 1) * size

        query = text("""
        SELECT
            p.id AS id,
                p.group_leader,
                p.description,
                p.date,
                p.amount,
                p.category,
                p.no_of_hajji,
                p.pilgrims_tracking_id,
                p.way_of_payment,
                p.transfer_no,
                p.transaction_id,
                p.created_at,
                p.created_by,
                p.updated_at,
                p.updated_by,
                a.total_payable AS admin_user_total_payable,
                a.total_payment AS admin_user_total_payment,
                a.total_due AS admin_user_total_due,
                a.total_available_amount AS admin_user_total_available_amount
            FROM core.payment p
            LEFT JOIN core.admin_user a
                ON a.code = p.group_leader
            WHERE p.group_leader = :group_leader
            GROUP BY p.id, a.code, a.total_payable, a.total_available_amount, a.total_due, a.total_payment
            ORDER BY p.id DESC
            LIMIT :size OFFSET :offset;
        """)
        result = await db.execute(
            query,
            {"group_leader": group_leader, "size": size, "offset": offset}
        )

        payments = result.mappings().all()  # returns a list of dict-like rows

        if not payments:
            raise HTTPException(status_code=400, detail="No payments found for this tracking ID")

        total_query = text("""
                            SELECT COUNT(*) FROM core.payment
                            WHERE group_leader = :group_leader
                        """)
        total_result = await db.execute(total_query, {"group_leader": group_leader})
        total = total_result.scalar() or 0

        first = payments[0]
        admin_user_total_payable = first["admin_user_total_payable"]
        admin_user_total_payment = first["admin_user_total_payment"]
        admin_user_total_due = first["admin_user_total_due"]
        admin_user_total_available_amount = first["admin_user_total_available_amount"]

        return payments, total, admin_user_total_payable, admin_user_total_payment, admin_user_total_due, admin_user_total_available_amount

    except Exception as e:
        raise Exception(f"Error fetching group leader payments: {str(e)}")


async def get_payment_summary_for_agency(
        db: AsyncSession,
        agency_name: str,
        page: int,
        size: int,
        group_leader: str = None,
        tracking_id: str = None,
):
    try:
        offset = (page - 1) * size

        # Get current time in Bangladesh timezone
        tz = pytz.timezone("Asia/Dhaka")
        now = datetime.now(tz)

        # Calculate time ranges (convert to naive datetime to match DB)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999).replace(tzinfo=None)

        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = today_start

        seven_days_ago = (now - timedelta(days=7)).replace(tzinfo=None)

        query = text("""
            WITH payment_data AS (
                SELECT 
                    p.*,
                    b.name AS bank_name,
                    b.branch AS bank_branch,
                    b.account_no AS bank_account
                FROM core.payment p
                LEFT JOIN core.bank_info b ON p.bank_info_id = b.id
                WHERE p.created_by = :agency_name
                  AND (CAST(:group_leader AS TEXT) IS NULL OR p.group_leader = :group_leader)
                  AND (CAST(:tracking_id AS TEXT) IS NULL OR p.tracking_id = :tracking_id)
            ),
            total_count AS (
                SELECT COUNT(*) AS count
                FROM payment_data
            ),
            paginated_payments AS (
                SELECT *
                FROM payment_data
                ORDER BY created_at DESC
                OFFSET :offset LIMIT :size
            ),
            bank_summary AS (
                SELECT
                    bank_info_id,
                    bank_name,
                    bank_branch,
                    bank_account,
                    SUM(amount) AS total_payment
                FROM payment_data
                WHERE bank_info_id IS NOT NULL AND category = 'Payment'
                GROUP BY bank_info_id, bank_name, bank_branch, bank_account
            ),
            summary AS (
                SELECT
                    COALESCE(SUM(amount) FILTER (WHERE category = 'Payment'), 0) AS total_payment,
                    COALESCE(SUM(amount) FILTER (WHERE category = 'Payment' AND created_at >= :seven_days_ago), 0) AS last_7_days_payment,
                    COALESCE(SUM(amount) FILTER (WHERE category = 'Payment' AND created_at >= :today_start AND created_at < :today_end), 0) AS today_payment,
                    COALESCE(SUM(amount) FILTER (WHERE category = 'Payment' AND created_at >= :yesterday_start AND created_at < :yesterday_end), 0) AS yesterday_payment
                FROM payment_data
            )
            SELECT json_build_object(
                'payments', COALESCE((SELECT json_agg(row_to_json(p)) FROM paginated_payments p), '[]'::json),
                'total_count', (SELECT count FROM total_count),
                'bank_summary', COALESCE((
                    SELECT json_agg(
                        json_build_object(
                            'bank_info_id', bank_info_id,
                            'bank_name', bank_name,
                            'bank_branch', bank_branch,
                            'bank_account', bank_account,
                            'total_payment', total_payment
                        )
                    )
                    FROM bank_summary
                ), '[]'::json),
                'overall_summary', COALESCE((SELECT row_to_json(s) FROM summary s), '{}'::json)
            ) AS result;
        """)

        params = {
            "agency_name": agency_name,
            "group_leader": group_leader,
            "tracking_id": tracking_id,
            "seven_days_ago": seven_days_ago,
            "today_start": today_start,
            "today_end": today_end,
            "yesterday_start": yesterday_start,
            "yesterday_end": yesterday_end,
            "offset": offset,
            "size": size
        }

        result = await db.execute(query, params)
        row = result.fetchone()

        query = text("""
            WITH filtered AS (
                SELECT p.*, b
                FROM core.payment p
                LEFT JOIN core.bank_info b ON p.bank_info_id = b.id
                WHERE p.created_by = :agency_name
                  AND (CAST(:group_leader AS TEXT) IS NULL OR p.group_leader = :group_leader)
                  AND (CAST(:tracking_id AS TEXT) IS NULL OR p.tracking_id = :tracking_id)
            ),
            grouped AS (
                SELECT
                    COALESCE(f.group_leader, f.tracking_id) AS key,
                    json_agg(
                        json_build_object(
                            'id', f.id,
                            'tracking_id', f.tracking_id,
                            'group_leader', f.group_leader,
                            'category', f.category,
                            'amount', f.amount,
                            'created_at', f.created_at,
                            'bank_info', to_jsonb(f.b)
                        ) ORDER BY f.created_at DESC
                    ) AS payments,
                    CASE WHEN f.group_leader IS NOT NULL THEN 1 ELSE 2 END AS sort_order
                FROM filtered f
                GROUP BY sort_order, COALESCE(f.group_leader, f.tracking_id)
            ),
            ordered AS (
                SELECT key, payments
                FROM grouped
                ORDER BY sort_order, key
                OFFSET :offset LIMIT :size
            )
            SELECT json_object_agg(key, payments) AS result
            FROM ordered;
        """)

        params = {
            "agency_name": agency_name,
            "group_leader": group_leader or None,
            "tracking_id": tracking_id or None,
            "offset": offset,
            "size": size,
        }

        response = await db.execute(query, params)
        another_row = response.fetchone()

        if row and row[0] and another_row and another_row[0]:
            return row[0], another_row[0]
        else:
            return {
                "payments": [],
                "total_count": 0,
                "bank_summary": [],
                "overall_summary": {
                    "total_payment": 0,
                    "last_7_days_payment": 0,
                    "today_payment": 0,
                    "yesterday_payment": 0
                }
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_by_id(db: AsyncSession, payable_id: int):
    result = await db.execute(
        select(PaymentModel).where(PaymentModel.id == payable_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=400, detail="Payable not found")
    return payment


async def update_payable(db: AsyncSession, payable_id: int, update_data: dict):
    try:
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided to update")

        query = (
            update(PaymentModel)
            .where(PaymentModel.id == payable_id)
            .values(**update_data)
            .returning(PaymentModel)
        )
        result = await db.execute(query)
        updated_payment = result.scalar_one_or_none()

        if not updated_payment:
            raise HTTPException(status_code=400, detail="Update failed — Payable not found")

        await db.commit()
        return updated_payment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def get_payment_by_id(db:AsyncSession, payment_id:int):
    try:
        result = await db.execute(
            select(PaymentModel, BankInfoModel)
            .join(
                BankInfoModel,
                BankInfoModel.id == PaymentModel.bank_info_id,
                isouter=True
            )
            .where(PaymentModel.id == payment_id)
        )

        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Payment not found")

        payment, bank_info = row

        # Combine data into a single dictionary
        return {
            "payment": payment,
            "bank_info": bank_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Payment not found")

