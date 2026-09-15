from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.agency_profile_model import AgencyProfileModel


async def upsert_agency_profiles(db: AsyncSession, rows: List[Dict[str, Any]]):
    try:
        if not rows:
            return

        stmt = insert(AgencyProfileModel).values(rows)
        update_columns = {
            col: stmt.excluded[col]
            for col in rows[0].keys()
            if col != "hl"
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=[AgencyProfileModel.hl],
            set_=update_columns,
        )

        await db.execute(stmt)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e


async def get_all_agency_profiles(db: AsyncSession):
    try:
        result = await db.execute(
            select(AgencyProfileModel).order_by(AgencyProfileModel.sl_no)
        )
        return result.scalars().all()
    except Exception as e:
        raise e
