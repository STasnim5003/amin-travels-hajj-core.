
import fastapi
from fastapi import Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import dashboard_service
from data.db.db_config import get_async_db
from infrastructure.schema.dashboard_schema import DashboardResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["dashboard"])
@private_router.get("/dashboard", response_model=DashboardResponseSchema)
async def get_dashboard_data(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await dashboard_service.get_dashboard_data(db=db, agency_name=agency_name)
