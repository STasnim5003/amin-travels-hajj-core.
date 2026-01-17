from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, func, update, delete

from data.model.admin_model import AdminModel
from data.model.route_request_model import RouteRequestModel


async def find_route_by_route_mapping_id(db:AsyncSession, route_mapping_id:str, agency_name : str):
    try:
        stmt = (
            select(RouteRequestModel)
            .where(RouteRequestModel.route_mapping_id == route_mapping_id,
                   RouteRequestModel.agency_name == agency_name)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e


async def create_route_request(db:AsyncSession, request_dict:dict, sar_update_dict:dict):
    try:
        stmt = (
            insert(RouteRequestModel)
            .values(**request_dict)
            .returning(RouteRequestModel)
        )
        result = await db.execute(stmt)

        sar_update_stmt = (
            update(AdminModel)
            .where(AdminModel.agency_name == sar_update_dict['agency_name'])
            .values(sar =sar_update_dict['sar'])
        )
        await db.execute(sar_update_stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e

async def find_hajji_by_route_type(db:AsyncSession, route_type : str, agency_name : str):
    try:
        stmt = (
            select(RouteRequestModel)
            .where(RouteRequestModel.agency_name == agency_name,
                   RouteRequestModel.route_type == route_type)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_route_wise_hajji_count(db: AsyncSession, agency_name: str):
    try:
        stmt = (
            select(
                RouteRequestModel.route_type,
                RouteRequestModel.agency_name,
                func.sum(RouteRequestModel.number_of_pax).label("total_pax")
            )
            .where(RouteRequestModel.agency_name == agency_name)
            .group_by(
                RouteRequestModel.route_type,
                RouteRequestModel.agency_name
            )
        )

        result = await db.execute(stmt)
        return result.mappings().all()   # returns list of tuples

    except Exception as e:
        raise e


async def get_route_requests(db:AsyncSession, agency_names: List[str]):
    try:
        stmt = (
            select(RouteRequestModel)
            .where(RouteRequestModel.agency_name.in_(agency_names))
            .order_by(RouteRequestModel.id.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_route_request_by_id(db:AsyncSession, request_id:int):
    try:
        stmt = (
            select(RouteRequestModel)
            .where(RouteRequestModel.id == request_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def update_route_requests(db:AsyncSession, request_dict:dict, sar_update_dict:dict):
    try:
        stmt = (
            update(RouteRequestModel)
            .where(RouteRequestModel.id == request_dict['id'])
            .values(**request_dict)
            .returning(RouteRequestModel)
        )
        result = await db.execute(stmt)

        if sar_update_dict:
            sar_update_stmt = (
                update(AdminModel)
                .where(AdminModel.agency_name == sar_update_dict['agency_name'])
                .values(sar =sar_update_dict['sar'])
            )
            await db.execute(sar_update_stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_route_request(db:AsyncSession, request_id:int, sar_update_dict:dict):
    try:
        stmt = (
            delete(RouteRequestModel)
            .where(RouteRequestModel.id == request_id)
        )
        await db.execute(stmt)

        sar_update_stmt = (
            update(AdminModel)
            .where(AdminModel.agency_name == sar_update_dict['agency_name'])
            .values(sar = sar_update_dict['sar'])
        )

        await db.execute(sar_update_stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e


async def cancel_route_request(db:AsyncSession, request_dict:dict):
    try:
        stmt = (
            update(RouteRequestModel)
            .where(RouteRequestModel.id == request_dict['id'])
            .values(**request_dict)
            .returning(RouteRequestModel))
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def cancel_request_lead_agency_action(db, request_dict):
    try:
        stmt = (update(RouteRequestModel)
                .where(RouteRequestModel.id == request_dict['id'])
                .values(**request_dict)
                .returning(RouteRequestModel))
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e