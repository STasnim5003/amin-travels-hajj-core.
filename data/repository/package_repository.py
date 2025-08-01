from sqlalchemy.ext.asyncio import AsyncSession

from data.filter.query_filter import filter_query
from data.model.package_model import PackageModel
from infrastructure.schema.package_schema import PackageResponseSchema


async def get_packages(db:AsyncSession, name: str=None, search: str=None):
    try:
        packages, count = await filter_query(
            db=db,
            model=PackageModel,
            name=name,
            search=search,
            search_fields=["name"],
            sort_by=[("id", "asc")],
            is_active=True,
        )
        packages_response = []
        for package in packages:
            packages_response.append(PackageResponseSchema.model_validate(package).model_dump())
        return packages_response
    except Exception as e:
        raise



