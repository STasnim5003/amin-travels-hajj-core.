import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.middleware.middleware import get_current_user
from app.service import route_request_service
from data.db.db_config import get_async_db
from infrastructure.schema.route_request_schema import RouteRequestResponseSchema, RouteRequestBaseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

private_router.post("/route-request", response_model=RouteRequestResponseSchema, tags=["route request"])
async def create_route_request(
        request: RouteRequestBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await route_request_service.create_route_request(db=db, request=request, agency_name=agency_name)