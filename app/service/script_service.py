import httpx
from async_timeout import timeout
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import script_repository
from infrastructure.schema.script_schema import AgencyHajjiCountFetchResponseSchema

load_dotenv()


async def prp_data_fetch_update(request_schema):
    try:
        # Define the target API URL
        url = "http://localhost:8001/fetch-prp-data"



        login_data = {
            "email": request_schema.email,
            "password": request_schema.password
        }
        timeout = httpx.Timeout(600.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=login_data)
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Remote API error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

async def agency_hajji_count_fetch(db:AsyncSession):
    results = await script_repository.agency_hajji_count(db)
    response = []
    for row in results:
        response.append(
            AgencyHajjiCountFetchResponseSchema(
                hl=row.hl,
                agency=row.agency,
                preregistered_pilgrim=row.preregistered_pilgrim,
                registered_pilgrim=row.registered_pilgrim,
                voucher_from_details=row.voucher_from_details,
                need_to_pay_voucher=row.need_to_pay_voucher,
                registered_percentage=row.percentage_registered,  # ✅ map DB → API
                total_pilgrims=row.total_pilgrims,
                created_at=row.created_at
            )
        )

    return response



