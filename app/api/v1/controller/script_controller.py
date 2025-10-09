import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import script_service
from data.db.db_config import get_async_db
from infrastructure.schema.script_schema import RunScriptRequestSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/fetch-prp-data",response_model=None, tags=["prp"])
async def prp_data_fetch_update(
        request_schema : RunScriptRequestSchema,
        current_user: dict = Depends(get_current_user)
):

    if current_user["role"] not in ["SUPER_ADMIN", "AGENCY"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return await script_service.prp_data_fetch_update(request_schema)
