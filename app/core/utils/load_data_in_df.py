from os import getenv

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine

load_dotenv()
DB_PARAMS = {
    "host": getenv("DB_HOST"),
    "dbname": getenv("DB_NAME"),
    "user": getenv("DB_USERNAME"),
    "password": getenv("DB_PASSWORD"),
    "port": getenv("DB_PORT"),
}


# def load_pilgrim_data_from_db():
#     conn = None
#     df = pd.DataFrame()
#     try:
#
#         conn = psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)
#
#         query = "SELECT * FROM core.pilgrim_data;"
#
#         df = pd.read_sql(query, conn)
#         print("✅ Data loaded successfully")
#
#     except Exception as e:
#         print("❌ Error loading data:", e)
#
#     finally:
#         if conn:
#             conn.close()
#             print("🔒 Connection closed")
#
#     return df


def load_pilgrim_data_from_db():
    engine = create_engine(
        f"postgresql+psycopg2://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['dbname']}"
    )
    try:
        query = "SELECT * FROM core.pilgrim_data;"
        df = pd.read_sql(query, engine)
        print("✅ Data loaded successfully")
        engine.dispose()
        return df
    except Exception as e:
        print("❌ Error loading data:", e)
        engine.dispose()
        return pd.DataFrame()


def read_json(file_path):
    df = pd.read_json(file_path, dtype={"NID": str})
    return df
