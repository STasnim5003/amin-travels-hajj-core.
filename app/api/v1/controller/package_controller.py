import fastapi
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.middleware.middleware import get_current_user
from app.service import package_service
from data.db.db_config import get_async_db
from infrastructure.schema.package_schema import PackagesResponseSchema, PackageMasterDataForFilterListSchema, \
    PackageResponseSchema, PackageBaseSchema, PackageUpdateSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")
private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@router.get("/packages", response_model=PackagesResponseSchema, tags=["packages"])
async def get_packages_endpoint(
        name: str = None,
        search: str = None,
        hajj_year: int = 2026,
        package_type: str = "HAJJ",
        duration: int = None,
        description_type: str = None,
        hajj_month: str = None,
        agency_name:str = None,
        db: AsyncSession = Depends(get_async_db)
):
    response = await package_service.get_packages(name=name,
                                                  search=search,
                                                  hajj_year=hajj_year,
                                                  package_type=package_type,
                                                  duration=duration,
                                                  description_type=description_type,
                                                  hajj_month=hajj_month,
                                                  agency_name=agency_name,
                                                  db=db)
    return JSONResponse(content=jsonable_encoder(response))

@private_router.get("/packages", response_model=PackagesResponseSchema, tags=["packages"])
async def get_packages_endpoint(
        name: str = None,
        search: str = None,
        hajj_year: int = None,
        package_type: str = "HAJJ",
        duration: int = None,
        description_type: str = None,
        hajj_month: str = None,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    response = await package_service.get_packages(name=name,
                                                  search=search,
                                                  hajj_year=hajj_year,
                                                  package_type=package_type,
                                                  duration=duration,
                                                  description_type=description_type,
                                                  hajj_month=hajj_month,
                                                  agency_name=agency_name,
                                                  db=db)
    return JSONResponse(content=jsonable_encoder(response))

@router.get("/package-filtering", response_model=PackageMasterDataForFilterListSchema, tags=["packages"])
async def get_master_data_for_package_filtering(
        package_type: str = "HAJJ",
        description_type: str = "DETAILS",
        db: AsyncSession = Depends(get_async_db)
):
    response = await package_service.get_package_master_data_for_filter(db, package_type, description_type)
    return JSONResponse(content=jsonable_encoder(response))

@private_router.post("/package", response_model=PackageResponseSchema, tags=["packages"])
async def create_package(
        request_body : PackageBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PackageResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await package_service.create_package(db, request_body, agency_name)


@router.get("/package/{package_id}", response_model=PackageResponseSchema, tags=["packages"])
async def get_package(
        package_id: int,
        db: AsyncSession = Depends(get_async_db)
):
    return await package_service.get_package_by_id(db, package_id)

@private_router.get("/package/{package_id}", response_model=PackageResponseSchema, tags=["packages"])
async def get_package_by_id_for_agency(
        package_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await package_service.get_package_by_id_for_agency(db, package_id, agency_name)

@private_router.put("/package/{package_id}", response_model=PackageResponseSchema, tags=["packages"])
async def update_package(
        package_id: int,
        request_body : PackageUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PackageResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await package_service.update_package(db, package_id, request_body, agency_name)