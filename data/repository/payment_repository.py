import random
import string
from typing import Optional, List

from fastapi import HTTPException, UploadFile
from sqlalchemy import insert, select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.payment_model import PaymentModel
from infrastructure.schema.payment_schema import PaymentSchema, AgencyPaymentSchemaForGroupLeader


async def create_payable_for_group_leader(db: AsyncSession, payment_request: PaymentSchema, agency_name: str,
                                          receipt: Optional[List[UploadFile]]):
    try:
        # Generate an 8-character random alphanumeric transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # Prepare data for insertion
        payment_data = payment_request.model_dump(exclude_unset=True)
        payment_data.update({
            "transaction_id": transaction_id,
            "created_by": agency_name,
            "updated_by": agency_name,
            "no_of_hajji": len(payment_request.pilgrims_id),
            "receipt": receipt
        })

        # Insert into payment_info
        stmt = (
            insert(PaymentModel)
            .values(**payment_data)
            .returning(PaymentModel)
        )
        result = await db.execute(stmt)
        created_payment = result.scalar_one()

        group_leader_code = payment_data.get("group_leader")

        if group_leader_code:
            # Get current payable total for that group leader
            query = select(AdminUserModel).where(AdminUserModel.code == group_leader_code)
            res = await db.execute(query)
            admin_user = res.scalar_one_or_none()

            if admin_user:
                # Increase total_due by the payment amount
                prev_available_amount = admin_user.total_available_amount or 0
                payable_amount = payment_data["amount"]
                if payable_amount >= prev_available_amount:
                    new_available_amount = 0
                    new_total_due = admin_user.total_due + (payable_amount - prev_available_amount)
                else:
                    new_total_due = 0
                    new_available_amount = prev_available_amount - payable_amount

                new_total_payable = (admin_user.total_payable or 0) + payment_data["amount"]
                total_available_amount = new_available_amount
                await db.execute(
                    update(AdminUserModel)
                    .where(AdminUserModel.code == group_leader_code)
                    .values(total_due=new_total_due, total_payable=new_total_payable,
                            total_available_amount=total_available_amount)
                )

        await db.commit()
        return created_payment

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating payment record: {str(e)}")


async def create_payment_for_group_leader(db: AsyncSession, request: AgencyPaymentSchemaForGroupLeader,
                                          agency_name: str, receipt: Optional[List[dict]] = None):
    try:
        # Check payable
        payment_query = select(PaymentModel).where(PaymentModel.id == request.payable_id)
        payment_query_result = await db.execute(payment_query)
        payment_result = payment_query_result.scalar_one_or_none()
        if not payment_result:
            raise HTTPException(status_code=400, detail="Payable Id not found")

        # Check Group Leader
        admin_user = None
        if request.group_leader:
            query = select(AdminUserModel).where(AdminUserModel.code == request.group_leader)
            res = await db.execute(query)
            admin_user = res.scalar_one_or_none()

            if not admin_user:
                raise HTTPException(status_code=400, detail="Group Leader not found")
            if admin_user.agency_name != agency_name:
                raise HTTPException(status_code=400, detail="Agency Name does not match")

        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        payment_data = request.model_dump(exclude_unset=True)
        payment_data.update({
            "transaction_id": transaction_id,
            "created_by": agency_name,
            "updated_by": agency_name,
            "payable_id": request.payable_id,
            "no_of_hajji": len(request.pilgrims_id),
            "receipt": receipt
        })

        # Step 3: Insert into payment table
        stmt = (
            insert(PaymentModel)
            .values(**payment_data)
            .returning(PaymentModel)
        )

        result = await db.execute(stmt)
        created_payment = result.scalar_one()

        if admin_user:
            prev_due = admin_user.total_due or 0
            amount_paid = payment_data["amount"]
            if amount_paid >= prev_due:
                new_total_due = 0
                extra_amount = amount_paid - prev_due
            else:
                new_total_due = prev_due - amount_paid
                extra_amount = 0
            new_total_payment = (admin_user.total_payment or 0) + payment_data["amount"]
            new_total_available_amount = (admin_user.total_available_amount or 0) + extra_amount
            await db.execute(
                update(AdminUserModel)
                .where(AdminUserModel.code == request.group_leader)
                .values(total_due=new_total_due)
                .values(total_payment=new_total_payment)
                .values(total_available_amount=new_total_available_amount)
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
                COALESCE(p.receipt, '[]'::json) AS receipt,
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
                            'payable_id', c.payable_id,
                            'transaction_id', c.transaction_id,
                            'created_at', c.created_at,
                            'created_by', c.created_by,
                            'updated_at', c.updated_at,
                            'updated_by', c.updated_by,
                            'receipt', COALESCE(c.receipt, '[]'::json),
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


async def get_payments_by_agency(db: AsyncSession, agency_name: str, group_leader: str, tracking_id: str, category: str,
                                 page: int,
                                 size: int):
    try:
        offset = (page - 1) * size

        filters = ["p.category = 'Payable'", "p.created_by = :agency_name"]
        params = {"agency_name": agency_name, "size": size, "offset": offset}

        if group_leader:
            filters.append("p.group_leader = :group_leader")
            params["group_leader"] = group_leader
        if tracking_id:
            filters.append("p.tracking_id = :tracking_id")
            params["tracking_id"] = tracking_id

        filter_clause = " AND ".join(filters)

        # ✅ Use f-string here
        query = text(f"""
            SELECT
                p.id AS id,
                p.description AS description,
                p.date AS date,
                p.amount AS amount,
                p.category AS category,
                p.no_of_hajji AS no_of_hajji,
                p.pilgrims_id AS pilgrims_id,
                p.total_payment AS total_paid,
                p.total_due AS total_due,
                p.tracking_id,
                p.group_leader,
                p.transaction_id AS transaction_id,
                p.created_at AS created_at,
                p.created_by AS created_by,
                p.updated_at AS updated_at,
                p.updated_by AS updated_by,
                COALESCE(p.receipt, '[]'::json) AS receipt,
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
                            'payable_id', c.payable_id,
                            'transaction_id', c.transaction_id,
                            'created_at', c.created_at,
                            'created_by', c.created_by,
                            'updated_at', c.updated_at,
                            'updated_by', c.updated_by,
                            'receipt', COALESCE(c.receipt, '[]'::json),
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
            WHERE {filter_clause}
            GROUP BY p.id
            ORDER BY p.id DESC
            LIMIT :size OFFSET :offset
        """)

        result = await db.execute(query, params)
        payments = result.mappings().all()

        if not payments:
            raise HTTPException(status_code=400, detail="No payments found for this tracking ID")

        total_query = text("""
                            SELECT COUNT(*) FROM core.payment
                            WHERE created_by = :agency_name
                            AND category = 'Payable'
                        """)
        total_result = await db.execute(total_query, {"agency_name": agency_name})
        total = total_result.scalar() or 0

        return payments, total

    except Exception as e:
        raise Exception(f"Error fetching group leader payments: {str(e)}")


async def get_by_id(db: AsyncSession, payable_id: int):
    result = await db.execute(
        select(PaymentModel).where(PaymentModel.id == payable_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=400, detail="Payable not found")
    return payment


async def update_payable(db: AsyncSession, payable_id: int, update_data: dict):
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
