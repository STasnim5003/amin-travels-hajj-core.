import logging
from contextlib import asynccontextmanager

from tenacity import retry, wait_fixed, stop_after_attempt

from app.core.constant.log_constants import get_fast_api_ascii
from data.db.db_config import test_db_connection


@retry(wait=wait_fixed(2), stop=stop_after_attempt(5), reraise=True)
async def ensure_connection(service):
    await service()


@asynccontextmanager
async def lifespan(app):
    # FASTAPI Logging
    logging.info(get_fast_api_ascii())

    # PostgreSQL
    try:
        await ensure_connection(test_db_connection)
        logging.info("--------------------------- Connected to PostgreSQL ----------------------------")
    except Exception as e:
        logging.error(f"Failed to connect to PostgreSQL: {e}")
        raise e

    try:
        yield
    finally:
        logging.info("------------------- Disconnected from PostgreSQL -------------------")
