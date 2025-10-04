from os import getenv

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.load_data_in_df import load_pilgrim_data_from_db
from app.core.utils.prp_data_fetch import prp_data_fetch
from app.core.utils.save_fetched_data import save_new_preregistered_data, registered_data, \
    move_walkin_to_preregistration, update_draft_serial_no, update_refunded
from infrastructure.schema.script_schema import RunScriptRequestSchema

load_dotenv()


async def prp_data_fetch_update(db: AsyncSession, request_schema: RunScriptRequestSchema):
    registered_pilgrim, preregistered_pilgrim = await prp_data_fetch(request_schema.email, request_schema.password)
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USERNAME"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    df_pilgrims = load_pilgrim_data_from_db()
    df_registered = pd.DataFrame(registered_pilgrim)
    df_preregistered = pd.DataFrame(preregistered_pilgrim)
    save_new_preregistered_data(df_pilgrims, df_preregistered, conn)
    registered_data(df_registered, conn)
    move_walkin_to_preregistration(df_pilgrims, df_preregistered, conn)
    update_draft_serial_no(df_pilgrims, df_preregistered, conn)
    update_refunded(df_preregistered, conn)

    conn.close()

    return {"message": "Script updated"}
