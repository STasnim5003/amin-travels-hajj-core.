from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def agency_hajji_count_with_total_raw(db: AsyncSession):
    try:
        query = text("""
        SELECT hl,
               agency,
               preregistered_pilgrim,
               registered_pilgrim,
               voucher_from_details,
               need_to_pay_voucher,
               percentage_registered,
               total_pilgrims,
               created_at
        FROM core.hajj_agency_vouchers

        UNION ALL

        SELECT 'TOTAL' AS hl,
               NULL AS agency,
               SUM(preregistered_pilgrim) AS preregistered_pilgrim,
               SUM(registered_pilgrim) AS registered_pilgrim,
               SUM(voucher_from_details) AS voucher_from_details,
               SUM(need_to_pay_voucher) AS need_to_pay_voucher,
               NULL AS percentage_registered,
               SUM(total_pilgrims) AS total_pilgrims,
               NULL AS created_at
        FROM core.hajj_agency_vouchers;
        """)

        result = await db.execute(query)
        final_list = [dict(row._mapping) for row in result.fetchall()]
        return final_list

    except Exception as e:
        await db.rollback()
        raise e
