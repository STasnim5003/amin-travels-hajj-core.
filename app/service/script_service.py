import httpx
from async_timeout import timeout
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import script_repository
from infrastructure.schema.script_schema import AgencyHajjiCountFetchResponseSchema, PrpDataFetchRequestSchema

load_dotenv()


async def prp_data_fetch_update(current_user: dict, request: PrpDataFetchRequestSchema):
    try:
        url = "http://localhost:8001/fetch-prp-data"

        if current_user.get("role") == "SUPER_ADMIN":
            agency_name = (request.agency_name or "").strip()
            if not agency_name:
                raise HTTPException(status_code=400, detail="Select the agency these PRP credentials belong to")
        else:
            # agency users can only save/sync their own agency's login, whatever the body says
            agency_name = current_user.get("agency_name")
            if not agency_name:
                raise HTTPException(status_code=403, detail="Agency not found for current user")

        payload = {"email": request.email, "password": request.password, "agency_name": agency_name}

        timeout = httpx.Timeout(1800.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Remote API error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

async def prp_agency_names_fetch(db: AsyncSession):
    return await script_repository.prp_agency_names(db)

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



