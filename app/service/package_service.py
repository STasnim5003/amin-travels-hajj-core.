from data.repository import package_repository


async def get_packages(name, search, db):
    result = await package_repository.get_packages(db, name, search)
    return result