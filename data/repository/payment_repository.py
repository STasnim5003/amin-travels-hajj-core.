import random
import string
from typing import Optional, List

from fastapi import HTTPException, UploadFile
from sqlalchemy import insert, select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.payment_model import PaymentModel
from infrastructure.schema.payment_schema import PaymentSchema, AgencyPaymentSchemaForGroupLeader, \
    GroupLeaderPayableBaseSchema, PayableInfoUpdateSchema, PaymentUpdateSchema


async def create_payable_for_group_leader(db: AsyncSession, payment_request: dict, payable_info : PayableInfoUpdateSchema, agency_name: str):
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
                total_payable = payable_info.total_payable,
                total_due = payable_info.total_due,
                total_available_amount = payable_info.total_available_amount
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


async def create_payment_for_group_leader(db: AsyncSession, payment_data: dict,agency_name: str, payment_info:PayableInfoUpdateSchema):
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
                p.description AS description,
                p.date AS date,
                p.amount AS amount,
                p.category AS category,
                p.no_of_hajji as no_of_hajji,
                p.pilgrims_id as pilgrims_id,
                p.total_payment AS total_paid,
                p.total_due AS total_due,
                p.tracking_id,
                p.group_leader,
                p.transaction_id AS transaction_id,
                p.created_at AS created_at,
                p.created_by AS created_by,
                p.updated_at AS updated_at,
                p.updated_by AS updated_by,
                a.total_payable AS admin_user_total_payable,
                a.total_payment AS admin_user_total_payment,
                a.total_due AS admin_user_total_due,
                a.total_available_amount AS admin_user_total_available_amount,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'id', c.id,
                            'description', c.description,
                            'date', c.date,
                            'amount', c.amount,
                            'category', c.category,
                            'tracking_id', c.tracking_id,
                            'group_leader', c.group_leader,
                            'transaction_id', c.transaction_id,
                            'created_at', c.created_at,
                            'created_by', c.created_by,
                            'updated_at', c.updated_at,
                            'updated_by', c.updated_by,
                            'total_payable', c.total_payable,
                            'total_paid', c.total_payment,
                            'total_due', c.total_due
                        )
                    ) FILTER (WHERE c.id IS NOT NULL),
                    '[]'
                ) AS payments
            FROM core.payment p
            LEFT JOIN core.payment c
                ON c.payable_id = p.id AND c.category = 'Payment'
            LEFT JOIN core.admin_user a
                ON a.code = p.group_leader
            WHERE p.category = 'Payable' AND p.group_leader = :group_leader
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
                            AND category = 'Payable'
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


async def get_payments_by_agency(
    db: AsyncSession,
    agency_name: str,
    group_leader: str = None,
    tracking_id: str = None,
    page: int = 1,
    size: int = 20
):
    try:
        offset = (page - 1) * size

        # ✅ Base filters and params
        filters = ["p.created_by = :agency_name"]
        params = {
            "agency_name": agency_name,
            "size": size,
            "offset": offset
        }

        # ✅ Add optional filters dynamically
        if group_leader:
            filters.append("p.group_leader = :group_leader")
            params["group_leader"] = group_leader
        if tracking_id:
            filters.append("p.tracking_id = :tracking_id")
            params["tracking_id"] = tracking_id

        # ✅ Convert to SQL string
        filter_clause = " AND ".join(filters)

        # ✅ Single query with group leaders first, then tracking IDs
        query = text(f"""
            SELECT
                key,
                json_agg(to_jsonb(p) - 'id') AS payments
            FROM (
                SELECT 
                    p.group_leader AS key,
                    p.*,
                    1 AS type_order
                FROM core.payment p
                WHERE p.group_leader IS NOT NULL 
                  AND {filter_clause}

                UNION ALL

                SELECT 
                    p.tracking_id AS key,
                    p.*,
                    2 AS type_order
                FROM core.payment p
                WHERE p.tracking_id IS NOT NULL 
                  AND {filter_clause}
            ) AS p
            GROUP BY key, type_order
            ORDER BY type_order, key, MAX(p.created_at) DESC
            LIMIT :size OFFSET :offset
        """)

        result = await db.execute(query, params)
        rows = result.mappings().all()

        if not rows:
            raise HTTPException(status_code=400, detail="No payments found for this agency")

        grouped_payments = {row["key"]: row["payments"] for row in rows}

        # ✅ Count total for pagination
        total_query = text("""
            SELECT COUNT(*) 
            FROM core.payment 
            WHERE created_by = :agency_name
        """)
        total_result = await db.execute(total_query, {
            "agency_name": agency_name
        })
        total = total_result.scalar() or 0

        return grouped_payments, total

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
