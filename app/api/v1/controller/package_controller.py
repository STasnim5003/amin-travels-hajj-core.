import fastapi
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.service import package_service
from data.db.db_config import get_async_db
from infrastructure.schema.package_schema import PackagesResponseSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@router.get("/packages", response_model=PackagesResponseSchema, tags=["packages"])
async def get_packages_endpoint(
        name: str = None,
        search: str = None,
        hajj_year: int = 2026,
        package_type: str = "HAJJ",
        duration: int = None,
        description_type: str = None,
        hajj_month: str = None,
        db: AsyncSession = Depends(get_async_db)
):
    response = await package_service.get_packages(name=name,
                                                  search=search,
                                                  hajj_year=hajj_year,
                                                  package_type=package_type,
                                                  duration=duration,
                                                  description_type=description_type,
                                                  hajj_month=hajj_month,
                                                  db=db)
    return JSONResponse(content=jsonable_encoder(response))
