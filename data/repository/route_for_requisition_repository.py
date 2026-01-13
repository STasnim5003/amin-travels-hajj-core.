from typing import List, Optional

from sqlalchemy import update, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.route_for_requisition import RouteForRequisition


async def create_route_for_requisition(
        db: AsyncSession,
        route_request_1: dict,
        route_request_2: Optional[dict] = None
):
    try:
        created_routes = []

        # Insert first route
        stmt1 = (
            insert(RouteForRequisition)
            .values(**route_request_1)
            .returning(RouteForRequisition)
        )
        result1 = await db.execute(stmt1)
        created_routes.append(result1.scalar_one())

        # Insert second route if exists
        if route_request_2:
            stmt2 = (
                insert(RouteForRequisition)
                .values(**route_request_2)
                .returning(RouteForRequisition)
            )
            result2 = await db.execute(stmt2)
            created_routes.append(result2.scalar_one())

        await db.commit()
        return created_routes

    except Exception as e:
        await db.rollback()
        raise e


async def get_route_by_type_and_name(db, route_type, route_name, agency_name):
    try:
        stmt = (
            select(RouteForRequisition)
            .where(RouteForRequisition.route_type == route_type,
                   RouteForRequisition.route_name == route_name,
                   RouteForRequisition.agency_name == agency_name)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def get_routes(
        db: AsyncSession,
        route_type: Optional[str],
        agency_names: List[str]
):
    try:
        stmt = select(RouteForRequisition).where(
            RouteForRequisition.agency_name.in_(agency_names)
        )

        if route_type is not None:
            stmt = stmt.where(RouteForRequisition.route_type == route_type)

        result = await db.execute(stmt)
        return result.scalars().all()

    except Exception as e:
        raise e


async def get_routes_by_id(db: AsyncSession, requisition_id: int, agency_names: List[str]):
    try:
        stmt = select(RouteForRequisition).where(
            RouteForRequisition.agency_name.in_(agency_names),
            RouteForRequisition.id == requisition_id
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def update_route(db: AsyncSession, route_request: dict):
    try:
        stmt = (
            update(RouteForRequisition)
            .values(**route_request)
            .where(RouteForRequisition.id == route_request['id'], )
            .returning(RouteForRequisition)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_route(db: AsyncSession, requisition_id: int):
    try:
        stmt = (
            delete(RouteForRequisition)
            .where(RouteForRequisition.id == requisition_id)
        )
        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e
