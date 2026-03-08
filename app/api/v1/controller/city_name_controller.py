import fastapi
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import city_name_service
from data.db.db_config import get_async_db
from infrastructure.schema.city_name_schema import CityNameResponseSchema, CityNameCreateSchema, CityNameBaseSchema, \
    CityNameListResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/city-name", response_model=CityNameResponseSchema, tags=['City Name'])
async def create_city_name(
        request: CityNameCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> CityNameResponseSchema:
    if current_user["role"] not in ["AGENCY","STAFF"]:
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user['agency_name']
    username = current_user["username"]
    return await city_name_service.create_city_name(db, request,agency_name, username)

@private_router.get("/city-name", response_model=CityNameListResponseSchema, tags=['City Name'])
async def get_city_names(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> CityNameListResponseSchema:
    if current_user["role"] not in ["AGENCY","STAFF"]:
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user['agency_name']

    return await city_name_service.get_city_name(db, agency_name)