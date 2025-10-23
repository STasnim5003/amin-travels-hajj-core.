

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import current_user

from app.core.middleware.middleware import get_current_user
from app.service import bank_info_service
from data.db.db_config import get_async_db
from infrastructure.schema.bank_info_schema import BankInfoBaseSchema, BankInfoUpdateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/bank-info", tags=["payment"])
async def create_bank_info(
        request : BankInfoBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await bank_info_service.create_bank_info(db, request, agency_name)

@private_router.get("/bank-info", tags=["payment"])
async def get_bank_info(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await bank_info_service.get_bank_info(db, agency_name)

@private_router.put("/bank-info", tags=["payment"])
async def update_bank_info(
        update_request: BankInfoUpdateSchema,
        db:AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await bank_info_service.update_bank_info(db, update_request, agency_name)


@private_router.get("/bank-info/{bank_id}", tags=["payment"])
async def get_bank_info_by_id(
        bank_id: int,
        db:AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await bank_info_service.get_bank_info_by_id(db=db, bank_id=bank_id, agency_name=agency_name)



@private_router.delete("/bank-info/{bank_id}", tags=["payment"])
async def delete_bank_info(
        bank_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await bank_info_service.delete_bank_info(db=db, bank_id=bank_id, agency_name=agency_name)