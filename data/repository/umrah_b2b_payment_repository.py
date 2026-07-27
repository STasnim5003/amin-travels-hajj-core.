from sqlalchemy import insert, update, select, delete, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.umrah_b2b_agent_model import UmrahB2BAgentModel
from data.model.umrah_b2b_payment_model import UmrahB2BPayment
from data.model.umrah_requisition_model import UmrahRequisitionModel


async def create_umrah_b2b_payment(db: AsyncSession, request_dict: dict):
    try:
        b2b_agent_name = request_dict['b2b_agent_name']
        amount = request_dict["amount"]
        stmt = (
            insert(UmrahB2BPayment)
            .values(**request_dict)
            .returning(UmrahB2BPayment)
        )

        result = await db.execute(stmt)

        update_stmt = (
            update(UmrahB2BAgentModel)
            .where(
                UmrahB2BAgentModel.name == b2b_agent_name,
                UmrahB2BAgentModel.agency_name == request_dict["agency_name"]
            )
            .values(
                total_credit=UmrahB2BAgentModel.total_credit + amount,
                total_due=func.greatest(
                    0,
                    UmrahB2BAgentModel.total_bill - UmrahB2BAgentModel.total_credit - amount
                )
            )
        )
        await db.execute(update_stmt)

        invoice_no_and_paid_amount = request_dict.get('invoice_no_and_paid_amount')
        if invoice_no_and_paid_amount:
            values = ", ".join(
                f"(CAST(:invoice_no_{i} AS TEXT), CAST(:paid_amount_{i} AS DOUBLE PRECISION), CAST(:due_{i} AS DOUBLE PRECISION))"
                for i in range(len(invoice_no_and_paid_amount))
            )
            params = {}
            for i, item in enumerate(invoice_no_and_paid_amount):
                params[f"invoice_no_{i}"] = item["invoice_no"]
                params[f"paid_amount_{i}"] = float(item["paid_amount"])
                params[f"due_{i}"] = float(item["due"])

            query = text(f"""
                UPDATE core.umrah_b2b_payements p
                SET
                    paid_amount = v.paid_amount,
                    due = v.due
                FROM (
                    VALUES
                        {values}
                ) AS v(invoice_no, paid_amount, due)
                WHERE p.invoice_no = v.invoice_no
            """)
            await db.execute(query, params)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_b2b_payments(db: AsyncSession, agency_name: str):
    try:
        query = text("""
                        SELECT
                            ubp.b2b_agent_name,
                        
                            -- Total Bill (only requisitions)
                            COALESCE(
                                SUM(ubp.amount) FILTER (
                                    WHERE ubp.office_code IS NOT NULL
                                ),
                                0
                            ) AS total_bill,
                        
                            -- Total Credit (only payments)
                            COALESCE(
                                SUM(ubp.amount) FILTER (
                                    WHERE ubp.office_code IS NULL
                                ),
                                0
                            ) AS total_credit,
                        
                            -- Due = Bill - Credit (minimum 0)
                            GREATEST(
                                COALESCE(
                                    SUM(ubp.amount) FILTER (
                                        WHERE ubp.office_code IS NOT NULL
                                    ),
                                    0
                                ) -
                                COALESCE(
                                    SUM(ubp.amount) FILTER (
                                        WHERE ubp.office_code IS NULL
                                    ),
                                    0
                                ),
                                0
                            ) AS due,
                        
                            -- Available Balance = Credit - Bill (minimum 0)
                            GREATEST(
                                COALESCE(
                                    SUM(ubp.amount) FILTER (
                                        WHERE ubp.office_code IS NULL
                                    ),
                                    0
                                ) -
                                COALESCE(
                                    SUM(ubp.amount) FILTER (
                                        WHERE ubp.office_code IS NOT NULL
                                    ),
                                    0
                                ),
                                0
                            ) AS available_balance,
                        
                            COALESCE(
                                json_agg(
                                    json_build_object(
                                        'office_code', ubp.office_code,
                                        'invoice_no', ubp.invoice_no,
                                        'amount', ubp.amount,
                                        'paid_amount', ubp.paid_amount,
                                        'due', ubp.due,
                                        'way_of_payment', ubp.way_of_payment,
                                        'payment_date', ubp.payment_date,
                                        'id', ubp.id,
                                        'description', ubp.description,
                                        'invoice_no_and_paid_amount', ubp.invoice_no_and_paid_amount
                                    )
                                    ORDER BY ubp.payment_date DESC
                                ),
                                '[]'::json
                            ) AS payments
                        
                        FROM core.umrah_b2b_payements AS ubp
                        WHERE ubp.agency_name = :agency_name
                        GROUP BY ubp.b2b_agent_name
                        ORDER BY ubp.b2b_agent_name;
                """)

        result = await db.execute(query, {"agency_name": agency_name})
        return result.mappings().all()
    except Exception as e:
        raise e


async def get_umrah_b2b_payment_by_id(db: AsyncSession, payment_id: int):
    result = await db.execute(
        select(UmrahB2BPayment).where(UmrahB2BPayment.id == payment_id)
    )
    return result.scalars().first()


async def update_umrah_b2b_payment(db: AsyncSession, request_dict: dict, b2b_finance_update: dict):
    try:
        agency_name = b2b_finance_update.pop('agency_name')
        stmt = (
            update(UmrahB2BPayment)
            .values(**request_dict)
            .where(UmrahB2BPayment.id == request_dict['id'])
            .returning(UmrahB2BPayment)
        )

        result = await db.execute(stmt)

        stmt = (
            update(UmrahB2BAgentModel)
            .values(**b2b_finance_update)
            .where(UmrahB2BAgentModel.name == request_dict['b2b_agent_name'],
                   UmrahB2BAgentModel.agency_name == agency_name)
        )
        await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_umrah_b2b_payment(db: AsyncSession, payment_id: int, b2b_finance_update: dict):
    try:
        b2b_agent_name = b2b_finance_update.pop('name')
        agency_name = b2b_finance_update.pop('agency_name')
        stmt = (
            delete(UmrahB2BPayment)
            .where(UmrahB2BPayment.id == payment_id)
        )
        await db.execute(stmt)

        stmt = (
            update(UmrahB2BAgentModel)
            .values(**b2b_finance_update)
            .where(UmrahB2BAgentModel.name == b2b_agent_name, UmrahB2BAgentModel.agency_name == agency_name)
        )

        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_payments_for_b2b_agent(db: AsyncSession, agency_name: str, b2b_agent_name: str):
    try:
        query = text("""
                    SELECT
                        uba.name as b2b_agent_name,
                        uba.total_bill,
                        uba.total_credit,
                        uba.total_due,
                        uba.agency_name,

                        (
                            SELECT json_agg(item ORDER BY item_created_at DESC)
                            FROM (
                                SELECT
                                    json_build_object(
                                        'type', 'requisition',
                                        'amin_office_code', ur.amin_office_code,
                                        'name', ur.name,
                                        'sales_person', ur.sales_person,
                                        'total_price', ur.total_price,
                                        'discount', ur.discount,
                                        'created_at', ur.created_at
                                    ) AS item,
                                    ur.created_at AS item_created_at
                                FROM core.umrah_requisition ur
                                WHERE ur.b2b_agent_name = uba.name 
                                    and ur.agency_name = :agency_name 
                                    and ur.requisition_type = 'B2B' 
                                    and ur.is_confirmed = TRUE

                                UNION ALL

                                SELECT
                                    json_build_object(
                                        'type', 'payment',
                                        'invoice_no', ubp.invoice_no,
                                        'payment_date', ubp.payment_date,
                                        'amount', ubp.amount,
                                        'payment_way', ubp.way_of_payment,
                                        'created_at', ubp.created_at
                                    ) AS item,
                                    ubp.created_at AS item_created_at
                                FROM core.umrah_b2b_payements ubp
                                WHERE ubp.b2b_agent_name = uba.name
                                    and ubp.agency_name = :agency_name
                            ) t
                        ) AS transactions

                    FROM core.umrah_b2b_agents uba
                    WHERE uba.agency_name = :agency_name and uba.name = :b2b_agent_name;
            """)

        result = await db.execute(query, {
            "agency_name": agency_name,
            "b2b_agent_name": b2b_agent_name
        })

        return result.mappings().first()
    except Exception as e:
        raise e


async def get_umrah_b2b_billing_invoice(
        db: AsyncSession,
        amin_office_code: str,
):
    try:
        stmt = (
            select(
                UmrahRequisitionModel,
                UmrahB2BPayment.invoice_no,
            )
            .join(
                UmrahB2BPayment,
                UmrahB2BPayment.office_code == UmrahRequisitionModel.amin_office_code,
            )
            .where(
                UmrahRequisitionModel.amin_office_code == amin_office_code,
                UmrahRequisitionModel.requisition_type == "B2B",
                UmrahRequisitionModel.is_confirmed.is_(True),
            )
        )

        result = await db.execute(stmt)
        return result.first()  # Returns (UmrahRequisitionModel, invoice_no)

    except Exception as e:
        raise e


async def get_umrah_b2b_due_requisitions(db: AsyncSession, b2b_agent_name: str, agency_name: str):
    try:
        query = text(
            """
                select * from core.umrah_b2b_payements ubp
                where ubp.office_code is NOT NULL 
                and ubp.due > 0 
                and ubp.agency_name=:agency_name 
                and ubp.b2b_agent_name=:b2b_agent_name;
            """
        )

        params = {
            'agency_name': agency_name,
            'b2b_agent_name': b2b_agent_name
        }

        result = await db.execute(query, params)
        return result.mappings().all()
    except Exception as e:
        raise e


async def get_umrah_b2b_invoices_by_office_code(db: AsyncSession, office_code: str):
    try:
        stmt = (
            select(UmrahB2BPayment)
            .where(UmrahB2BPayment.office_code == office_code)
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    except Exception as e:
        raise e
