from datetime import datetime

import pytz
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def generate_amin_office_code(db: AsyncSession):
    try:
        tz = pytz.timezone("Asia/Dhaka")
        now = datetime.now(tz)

        # 2. Format date as DDMMYY
        date_part = now.strftime("%d%m%y")  # 07 04 26 -> 070426

        # 3. Get next sequence value from DB
        result = await db.execute(text("SELECT nextval('core.amin_office_seq')"))
        seq_val = result.scalar()

        # 4. Build code
        amin_office_code = f"UMR-{date_part}{seq_val}"

        return amin_office_code
    except Exception as e:
        raise e
