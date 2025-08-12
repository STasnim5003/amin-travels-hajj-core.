from data.repository import package_repository


async def get_packages(name, search, hajj_year, package_type, duration, description_type, hajj_month, db):
    result = await package_repository.get_packages(db=db,
                                                   name=name,
                                                   search=search,
                                                   hajj_year=hajj_year,
                                                   package_type=package_type,
                                                   duration=duration,
                                                   description_type=description_type,
                                                   hajj_month=hajj_month)
    return result
