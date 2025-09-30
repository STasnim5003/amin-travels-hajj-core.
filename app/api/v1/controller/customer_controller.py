import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import customer_service
from data.db.db_config import get_async_db
from infrastructure.schema.customer_schema import CustomerCreateSchema
from infrastructure.schema.pilgrim_data_schema import PilgrimDataResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/customer", response_model=PilgrimDataResponseSchema, tags=["Customer"])
async def create_customer(
        customer: CustomerCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PilgrimDataResponseSchema:

    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    group_name = current_user["agency_name"]
    return await customer_service.create_customer(db, customer, group_name)