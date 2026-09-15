import os

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import agency_profile_repository
from infrastructure.schema.agency_profile_schema import AgencyProfileItemSchema, AgencyProfileListResponseSchema

EXTERNAL_AGENCY_PROFILE_API_URL = os.environ.get(
    "EXTERNAL_AGENCY_PROFILE_API_URL", "http://187.127.220.201:8001/agency-profile"
)


async def sync_agency_profiles(db: AsyncSession) -> int:
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

    rows = [
        {
            "sl_no": row.get("sl_no"),
            "hl": row.get("hl"),
            "agency_name": row.get("agency_name"),
            "email": row.get("email"),
            "address": row.get("address"),
            "phone": row.get("phone"),
            "pre_reg": row.get("pre_reg"),
            "reg": row.get("reg"),
            "total": row.get("total"),
            "source_updated_at": row.get("updated_at"),
        }
        for row in payload.get("data", [])
        if row.get("hl")
    ]

    await agency_profile_repository.upsert_agency_profiles(db, rows)
    return len(rows)


async def get_agency_profiles(db: AsyncSession) -> AgencyProfileListResponseSchema:
    await sync_agency_profiles(db)
    profiles = await agency_profile_repository.get_all_agency_profiles(db)

    data = [
        AgencyProfileItemSchema(
            sl_no=profile.sl_no,
            hl=profile.hl,
            agency_name=profile.agency_name,
            email=profile.email,
            address=profile.address,
            phone=profile.phone,
            pre_reg=profile.pre_reg,
            reg=profile.reg,
            total=profile.total,
            updated_at=profile.source_updated_at,
        )
        for profile in profiles
    ]

    return AgencyProfileListResponseSchema(success=True, count=len(data), data=data)
