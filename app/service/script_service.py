import httpx
from async_timeout import timeout
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import script_repository
from infrastructure.schema.script_schema import AgencyHajjiCountFetchResponseSchema

load_dotenv()


async def prp_data_fetch_update(current_user: dict):
    try:
        url = "http://localhost:8001/fetch-prp-data"

        # The PRP service returns every agency when agency_name is missing,
        # so non-SUPER_ADMIN callers must always be scoped to their own agency.
        payload = {}
        if current_user.get("role") != "SUPER_ADMIN":
            agency_name = current_user.get("agency_name")
            if not agency_name:
                raise HTTPException(status_code=403, detail="Agency not found for current user")
            payload["agency_name"] = agency_name

        timeout = httpx.Timeout(1800.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Remote API error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

async def agency_hajji_count_fetch(db:AsyncSession):
    try:
        results = await script_repository.agency_hajji_count_with_total_raw(db)
        response = []
        for row in results:
            response.append(
                AgencyHajjiCountFetchResponseSchema(
                    hl=row["hl"],
                    agency=row["agency"],
                    preregistered_pilgrim=row["preregistered_pilgrim"],
                    registered_pilgrim=row["registered_pilgrim"],
                    voucher_from_details=row["voucher_from_details"],
                    need_to_pay_voucher=row["need_to_pay_voucher"],
                    registered_percentage=row["percentage_registered"],  # ✅ map DB → API
                    total_pilgrims=row["total_pilgrims"],
                    created_at=row["created_at"]
                )
            )

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



