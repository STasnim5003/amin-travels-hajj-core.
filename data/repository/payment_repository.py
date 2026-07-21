from datetime import datetime, timedelta

import pytz
from fastapi import HTTPException
from sqlalchemy import insert, select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.bank_info_model import BankInfoModel
from data.model.payment_model import PaymentModel
from data.model.pilgrim_data_model import PilgrimDataModel
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
                p.agency_name,
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
        user_type: str,
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
        tz = pytz.timezone('Asia/Dhaka')  # or your timezone
        now = datetime.now(tz)

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Yesterday's date range
        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = today_start

        # Last 7 days
        seven_days_ago = today_start - timedelta(days=7)

        query = text("""
            WITH all_payments AS (
                SELECT 
                    p.*,
                    b.name AS bank_name,
                    b.branch AS bank_branch,
                    b.account_no AS bank_account,
                    CASE 
                        WHEN p.group_leader IS NOT NULL THEN au.name
                        ELSE pd.name_en
                    END AS name,
                    CASE 
                        WHEN p.group_leader IS NOT NULL THEN au.mobile_no
                        ELSE pd.mobile_no
                    END AS mobile_no,
                    pd.actual_payable AS actual_payable,
                    pd.total_payment AS actual_payment,
                    pd.total_due AS actual_due
                FROM core.payment p
                LEFT JOIN core.bank_info b 
                    ON p.bank_info_id = b.id
                LEFT JOIN core.admin_user au 
                    ON p.group_leader = au.code
                LEFT JOIN core.pilgrim_data pd 
                    ON p.tracking_id = pd.tracking_id
                WHERE p.agency_name = :agency_name
            ),
            filtered AS (
                SELECT *
                FROM all_payments
                WHERE (CAST(:group_leader AS TEXT) IS NULL OR group_leader = :group_leader)
                  AND (CAST(:tracking_id AS TEXT) IS NULL OR tracking_id = :tracking_id)
                  AND (
                        (:user_type = 'GROUP_LEADER' AND group_leader IS NOT NULL)
                     OR (:user_type = 'PILGRIM' AND group_leader IS NULL AND tracking_id IS NOT NULL)
                     OR :user_type IS NULL
                  )
            ),
            total_count AS (
                SELECT COUNT(*) AS count FROM filtered
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
                            'way_of_payment', f.way_of_payment,
                            'transaction_id', f.transaction_id,
                            'created_at', f.created_at,
                            'username', f.name,
                            'mobile_no', f.mobile_no,
                            'actual_payable', f.actual_payable,
                            'actual_payment', f.actual_payment,
                            'actual_due', f.actual_due,
                            'voucher_no', f.voucher_no,
                            'cheque_no', f.cheque_no,
                            'cheque_bank', f.cheque_bank,
                            'agency_name', f.agency_name,
                            'bank_info', json_build_object(
                                'bank_info_id', f.bank_info_id,
                                'bank_name', f.bank_name,
                                'bank_branch', f.bank_branch,
                                'bank_account', f.bank_account
                            )
                        ) ORDER BY f.created_at DESC
                    ) AS payments,
                    CASE WHEN f.group_leader IS NOT NULL THEN 1 ELSE 2 END AS sort_order,
                    MAX(f.created_at) AS latest_payment_time
                FROM filtered f
                GROUP BY sort_order, COALESCE(f.group_leader, f.tracking_id)
            ),
            ordered AS (
                SELECT key, payments
                FROM grouped
                ORDER BY sort_order, latest_payment_time DESC, key
                OFFSET :offset LIMIT :size
            ),
            bank_summary AS (
                SELECT
                    bank_info_id,
                    bank_name,
                    bank_branch,
                    bank_account,
                    SUM(amount) AS total_payment
                FROM all_payments
                WHERE bank_info_id IS NOT NULL
                  AND category = 'Payment'
                GROUP BY bank_info_id, bank_name, bank_branch, bank_account
            ),
            summary AS (
                SELECT
                    COALESCE(SUM(amount), 0) AS total_payment,
                    COALESCE(SUM(amount) FILTER (WHERE created_at >= :seven_days_ago), 0) AS last_7_days_payment,
                    COALESCE(SUM(amount) FILTER (WHERE DATE(created_at) = DATE(:today_start)), 0) AS today_payment,
                    COALESCE(SUM(amount) FILTER (WHERE DATE(created_at) = DATE(:yesterday_start)), 0) AS yesterday_payment
                FROM all_payments
                WHERE category = 'Payment'
            )
            SELECT json_build_object(
                'grouped_payments', COALESCE((SELECT json_object_agg(key, payments) FROM ordered), '{}'::json),
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
                    ) FROM bank_summary
                ), '[]'::json),
                'overall_summary', COALESCE((SELECT row_to_json(s) FROM summary s), '{}'::json)
            ) AS result;
        """)

        params = {
            "agency_name": agency_name,
            "group_leader": group_leader or None,
            "tracking_id": tracking_id or None,
            "user_type": user_type,
            "seven_days_ago": seven_days_ago.replace(tzinfo=None),
            "today_start": today_start.replace(tzinfo=None),
            "today_end": today_end.replace(tzinfo=None),
            "yesterday_start": yesterday_start.replace(tzinfo=None),
            "yesterday_end": yesterday_end.replace(tzinfo=None),
            "offset": offset,
            "size": size,
        }

        result = await db.execute(query, params)
        row = result.fetchone()

        if row and row[0]:
            return row[0]
        else:
            return {
                "grouped_payments": [],
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
    stmt = (
        select(
            PaymentModel,
            PilgrimDataModel.id.label("pilgrim_id")
        )
        .join(
            PilgrimDataModel,
            PilgrimDataModel.tracking_id == PaymentModel.tracking_id,
            isouter=True
        )
        .where(PaymentModel.id == payable_id)
    )

    result = await db.execute(stmt)
    row = result.one_or_none()

    if not row:
        raise HTTPException(status_code=400, detail="Payable not found")

    payment, pilgrim_id = row

    # Attach pilgrim_id to the SQLAlchemy model instance
    setattr(payment, "pilgrim_id", pilgrim_id)

    return payment


async def update_payable_payment(db: AsyncSession, update_data: dict, finance_info: dict):
    try:
        payment_payable_update_id = None
        if update_data.get('payable_id'):
            payment_payable_update_id = update_data['payable_id']
            update_data.pop('payable_id')
        elif update_data.get('payment_id'):
            payment_payable_update_id = update_data['payment_id']
            update_data.pop('payment_id')

        query = (
            update(PaymentModel)
            .where(PaymentModel.id == payment_payable_update_id)
            .values(**update_data)
            .returning(PaymentModel)
        )
        result = await db.execute(query)

        if finance_info.get('tracking_id'):
            query = (
                update(PilgrimDataModel)
                .where(PilgrimDataModel.tracking_id == finance_info['tracking_id'])
                .values(**finance_info)
            )
            await db.execute(query)
        elif finance_info.get('code'):
            query = (
                update(AdminUserModel)
                .where(AdminUserModel.code == finance_info['code'])
                .values(**finance_info)
            )
            await db.execute(query)

        updated_payment = result.scalar_one_or_none()
        await db.commit()

        if not updated_payment:
            raise HTTPException(status_code=400, detail="Update failed")

        return updated_payment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_payment_by_id(db: AsyncSession, payment_id: int):
    try:
        result = await db.execute(
            select(
                PaymentModel,
                BankInfoModel,
                PilgrimDataModel.id.label("pilgrim_id")
            )
            .join(
                BankInfoModel,
                BankInfoModel.id == PaymentModel.bank_info_id,
                isouter=True
            )
            .join(
                PilgrimDataModel,
                PilgrimDataModel.tracking_id == PaymentModel.tracking_id,
                isouter=True
            )
            .where(PaymentModel.id == payment_id)
        )

        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Payment not found")

        payment, bank_info, pilgrim_id = row

        setattr(payment, "pilgrim_id", pilgrim_id)

        return {
            "payment": payment,
            "bank_info": bank_info
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_day_wise_payment(db: AsyncSession, agency_name: str):
    try:
        tz = pytz.timezone('Asia/Dhaka')
        now = datetime.now(tz)

        today = now.date()
        yesterday = today - timedelta(days=1)
        seven_days_ago = today - timedelta(days=7)

        query = """
            SELECT json_build_object(
                'today', (
                    SELECT json_agg(p.*)
                    FROM core.payment p
                    WHERE DATE(p.updated_at) = :today
                      AND p.category = 'Payment'
                      AND p.agency_name = :agency_name
                ),
                'yesterday', (
                    SELECT json_agg(p.*)
                    FROM core.payment p
                    WHERE DATE(p.updated_at) = :yesterday
                      AND p.category = 'Payment'
                      AND p.agency_name = :agency_name
                ),
                'last_7_days', (
                    SELECT json_agg(p.*)
                    FROM core.payment p
                    WHERE DATE(p.updated_at) >= :seven_days_ago
                      AND DATE(p.updated_at) <= :today
                      AND p.category = 'Payment'
                      AND p.agency_name = :agency_name
                )
            ) AS payments_json;
        """

        result = await db.execute(
            text(query),
            {
                "today": today,
                "yesterday": yesterday,
                "seven_days_ago": seven_days_ago,
                "agency_name": agency_name
            }
        )

        return result.scalar_one()
    except Exception as e:
        raise e


async def get_group_leader_ledger(db: AsyncSession, group_leader: str):
    try:
        stmt = (
            select(PaymentModel)
            .where(PaymentModel.group_leader == group_leader)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_agency_pilgrims_payment_info(db:AsyncSession, agency_name:str, hajj_year:int):
    try:
        query = text("""
                WITH pilgrim_data AS (
                    SELECT
                        tracking_id,
                        nid,
                        passport_no,
                        name_en,
                        mobile_no,
                        family_code,
                        total_payable,
                        actual_payable,
                        package_price_discount
                    FROM core.pilgrim_data
                    WHERE
                        hajj_year = :hajj_year
                        AND group_name = :agency_name
                ),
                
                payment_normalized AS (
                    SELECT
                        COALESCE(
                            pd_tracking.tracking_id,
                            pd_nid.tracking_id,
                            pd_passport.tracking_id
                        ) AS tracking_id,
                        p.id,
                        p.nid              AS payment_nid,
                        p.passport_no      AS payment_passport_no,
                        p.amount,
                        p.category,
                        p.description,
                        p.date,
                        p.way_of_payment,
                        p.created_at
                    FROM core.payment p
                
                    -- direct tracking_id match
                    LEFT JOIN pilgrim_data pd_tracking
                        ON pd_tracking.tracking_id = p.tracking_id
                
                    -- nid lookup
                    LEFT JOIN pilgrim_data pd_nid
                        ON p.tracking_id IS NULL
                        AND pd_nid.nid = p.nid
                
                    -- passport lookup
                    LEFT JOIN pilgrim_data pd_passport
                        ON p.tracking_id IS NULL
                        AND p.nid IS NULL
                        AND pd_passport.passport_no = p.passport_no
                
                    WHERE
                        p.hajj_year = :hajj_year
                        AND p.agency_name = :agency_name
                ),
                
                -- payments that DID resolve to a pilgrim
                payment_summary AS (
                    SELECT
                        pn.tracking_id,
                
                        COALESCE(
                            SUM(pn.amount) FILTER (WHERE pn.category = 'Payment'),
                            0
                        ) AS total_payment,
                
                        jsonb_agg(
                            jsonb_build_object(
                                'id', pn.id,
                                'amount', pn.amount,
                                'category', pn.category,
                                'description', pn.description,
                                'date', pn.date,
                                'way_of_payment', pn.way_of_payment
                            )
                            ORDER BY pn.created_at
                        ) AS payment_list
                
                    FROM payment_normalized pn
                    WHERE pn.tracking_id IS NOT NULL
                    GROUP BY pn.tracking_id
                ),
                
                -- payments that did NOT resolve to any pilgrim (orphans)
                orphan_payment_summary AS (
                    SELECT
                        COALESCE(
                            pn.payment_nid,
                            pn.payment_passport_no,
                            'no_ref_' || pn.id::text
                        ) AS orphan_key,
                        pn.payment_nid,
                        pn.payment_passport_no,
                
                        COALESCE(
                            SUM(pn.amount) FILTER (WHERE pn.category = 'Payment'),
                            0
                        ) AS total_payment,
                
                        jsonb_agg(
                            jsonb_build_object(
                                'id', pn.id,
                                'amount', pn.amount,
                                'category', pn.category,
                                'description', pn.description,
                                'date', pn.date,
                                'way_of_payment', pn.way_of_payment
                            )
                            ORDER BY pn.created_at
                        ) AS payment_list
                
                    FROM payment_normalized pn
                    WHERE pn.tracking_id IS NULL
                    GROUP BY
                        COALESCE(pn.payment_nid, pn.payment_passport_no, 'no_ref_' || pn.id::text),
                        pn.payment_nid,
                        pn.payment_passport_no
                )
                
                -- matched pilgrims + their payments (original behavior)
                SELECT
                    pd.tracking_id,
                    pd.nid,
                    pd.passport_no,
                    pd.name_en,
                    pd.mobile_no,
                    pd.family_code,
                    pd.total_payable,
                    pd.actual_payable,
                    pd.package_price_discount,
                    COALESCE(ps.total_payment, 0) AS total_payment,
                    GREATEST(pd.actual_payable - COALESCE(ps.total_payment, 0), 0) AS due,
                    ps.payment_list
                FROM pilgrim_data pd
                LEFT JOIN payment_summary ps
                    ON ps.tracking_id = pd.tracking_id
                
                UNION ALL
                
                -- orphan payments: no matching pilgrim record at all
                SELECT
                    NULL::text            AS tracking_id,
                    ops.payment_nid        AS nid,
                    ops.payment_passport_no AS passport_no,
                    NULL AS name_en,
                    NULL AS mobile_no,
                    NULL AS family_code,
                    NULL AS total_payable,
                    NULL AS actual_payable,
                    NULL AS package_price_discount,
                    ops.total_payment,
                    NULL AS due,           -- no actual_payable to compare against
                    ops.payment_list
                FROM orphan_payment_summary ops;
                """)

        result = await db.execute(
            query,
            {"agency_name": agency_name, "hajj_year":hajj_year},
        )

        return result.mappings().all()
    except Exception as e:
        raise e


async def get_agency_pilgrims_for_payment(db:AsyncSession, agency_name:str, hajj_year:int):
    try:
        query= text("""
            WITH payment_summary AS (
                SELECT
                    tracking_id,
                    nid,
                    passport_no,
                    SUM(amount) AS total_payment
                FROM core.payment
                WHERE category = 'Payment' and agency_name = :group_name
                GROUP BY
                    tracking_id,
                    nid,
                    passport_no
            )
            SELECT
                pd.tracking_id,
                pd.name_en,
                pd.nid,
                pd.passport_no,
                pd.mobile_no,
                pd.family_code,
                pd.sub_group,
                pd.total_payable,
                pd.actual_payable,
                pd.package_price_discount,
                COALESCE(SUM(ps.total_payment), 0) AS total_payment,
                GREATEST(
                    pd.actual_payable - COALESCE(SUM(ps.total_payment), 0),
                    0
                ) AS total_due
            FROM core.pilgrim_data pd
            LEFT JOIN payment_summary ps
                ON (
                    pd.tracking_id IS NOT NULL
                    AND ps.tracking_id = pd.tracking_id
                )
                OR (
                    pd.nid IS NOT NULL
                    AND ps.nid = pd.nid
                )
                OR (
                    pd.passport_no IS NOT NULL
                    AND ps.passport_no = pd.passport_no
                )
            WHERE
                pd.hajj_year = :hajj_year
                AND pd.group_name = :group_name
            GROUP BY
                pd.name_en,
                pd.tracking_id,
                pd.nid,
                pd.passport_no,
                pd.mobile_no,
                pd.family_code,
                pd.sub_group,
                pd.total_payable,
                pd.actual_payable,
                pd.package_price_discount;
        """)

        result = await db.execute(
            query,
            {"group_name": agency_name, "hajj_year": hajj_year},
        )

        return result.mappings().all()

    except Exception as e:
        raise e


async def get_payment_by_id_for_receipt(db:AsyncSession, payment_id:int, agency_name:str):
    try:
        query = text("""
            WITH payment_normalized AS (
                SELECT
                    p.*,
            
                    COALESCE(p.tracking_id, pd.tracking_id) AS tracking_id,
                    COALESCE(p.nid, pd.nid) AS nid,
                    COALESCE(p.passport_no, pd.passport_no) AS passport_no,
            
                    pd.name_en,
                    pd.mobile_no,
                    pd.family_code,
            
                    CASE
                        WHEN b.id IS NULL THEN NULL
                        ELSE jsonb_build_object(
                            'id', b.id,
                            'name', b.name,
                            'account_no', b.account_no
                        )
                    END AS bank_info
            
                FROM core.payment p
            
                LEFT JOIN LATERAL (
                    SELECT
                        tracking_id,
                        nid,
                        passport_no,
                        name_en,
                        mobile_no,
                        family_code
                    FROM core.pilgrim_data pd
                    WHERE
                        pd.group_name = :agency_name
                        AND (
                            pd.tracking_id = p.tracking_id
                            OR pd.nid = p.nid
                            OR pd.passport_no = p.passport_no
                        )
                    LIMIT 1
                ) pd ON TRUE
            
                LEFT JOIN core.bank_info b
                    ON b.id = p.bank_info_id
            
                WHERE
                    p.id = :payment_id
            )
            
            SELECT *
            FROM payment_normalized;
        """)

        result = await db.execute(
            query, {"agency_name": agency_name, "payment_id":payment_id}
        )
        return result.mappings().all()
    except Exception as e:
        raise e