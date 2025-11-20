from sqlalchemy import update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from data.model.flight_request_model import FlightRequestModel
from data.model.route_model import RouteModel


async def create(db: AsyncSession, data: dict):
    try:
        new_flight = FlightRequestModel(**data)
        db.add(new_flight)
        await db.commit()
        await db.refresh(new_flight)
        return new_flight
    except Exception as e:
        await db.rollback()
        raise e

async def get_by_id(db:AsyncSession, flight_request_id:int):
    try:
        ArrivalRoute = aliased(RouteModel)
        DepartureRoute = aliased(RouteModel)

        result = await db.execute(
            select(
                FlightRequestModel,
                ArrivalRoute.description.label("arrival_route_description"),
                DepartureRoute.description.label("departure_route_description")
            )
            .join(ArrivalRoute, FlightRequestModel.arrival_route == ArrivalRoute.id, isouter=True)
            .join(DepartureRoute, FlightRequestModel.departure_route == DepartureRoute.id, isouter=True)
            .where(FlightRequestModel.id == flight_request_id)
        )
        row = result.first()
        if not row:
            return None
        flight_request, arrival_route_name, departure_route_name = row

        data = flight_request.__dict__.copy()
        data["arrival_route_description"] = arrival_route_name
        data["departure_route_description"] = departure_route_name

        return data
    except Exception as e:
        raise e

async def update_flight_request(db: AsyncSession, flight_request_id: int, data: dict):
    try:
        stmt = (
            update(FlightRequestModel)
            .where(FlightRequestModel.id == flight_request_id)
            .values(**data)
            .returning(FlightRequestModel)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_all_flight_requests(db, agency_names):
    try:
        ArrivalRoute = aliased(RouteModel)
        DepartureRoute = aliased(RouteModel)

        stmt = (
            select(
                FlightRequestModel,
                ArrivalRoute.description.label("arrival_route_description"),
                DepartureRoute.description.label("departure_route_description")
            )
            .join(ArrivalRoute, FlightRequestModel.arrival_route == ArrivalRoute.id, isouter=True)
            .join(DepartureRoute, FlightRequestModel.departure_route == DepartureRoute.id, isouter=True)
            .where(FlightRequestModel.agency_name.in_(agency_names))
            .order_by(FlightRequestModel.id.desc())
        )
        result = await db.execute(stmt)
        return result.all()
    except Exception as e:
        raise e

async def delete_flight_request(db: AsyncSession, flight_request_id: int, agency_name: str) -> bool:
    try:
        # Check if the flight request exists
        result = await db.execute(
            select(FlightRequestModel).where(
                FlightRequestModel.id == flight_request_id,
                FlightRequestModel.agency_name == agency_name
            )
        )
        flight_request = result.scalar_one_or_none()
        if not flight_request:
            return False

        # Delete the flight request
        await db.execute(
            delete(FlightRequestModel).where(
                FlightRequestModel.id == flight_request_id,
                FlightRequestModel.agency_name == agency_name
            )
        )
        await db.commit()
        return True

    except Exception as e:
        await db.rollback()
        raise e