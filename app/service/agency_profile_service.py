import os

import httpx
from fastapi import HTTPException

from infrastructure.schema.agency_profile_schema import AgencyProfileItemSchema, AgencyProfileListResponseSchema

EXTERNAL_AGENCY_PROFILE_API_URL = os.environ.get(
    "EXTERNAL_AGENCY_PROFILE_API_URL", "http://187.127.220.201:8001/agency-profile"
)


async def get_agency_profiles() -> AgencyProfileListResponseSchema:
    try:
        timeout = httpx.Timeout(60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(EXTERNAL_AGENCY_PROFILE_API_URL)
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Remote API error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to reach agency profile source: {str(e)}")

    data = [AgencyProfileItemSchema(**row) for row in payload.get("data", [])]
    return AgencyProfileListResponseSchema(success=True, count=len(data), data=data)
