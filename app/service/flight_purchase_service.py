from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from data.repository import flight_purchase_repository
from infrastructure.schema.flight_purchase_schema import (
    FlightPurchaseCreateSchema,
    FlightPurchaseUpdateSchema,
    FlightPurchaseResponseSchema,
    FlightPurchaseListResponseSchema,
    FlightPurchaseReconciliationItemSchema,
    FlightPurchaseReconciliationResponseSchema,
)


def _validate_amounts(seats_purchased: int, cost: float):
    if seats_purchased is not None and seats_purchased <= 0:
        raise HTTPException(status_code=400, detail="seats_purchased must be greater than 0")
    if cost is not None and cost < 0:
        raise HTTPException(status_code=400, detail="cost cannot be negative")


def _normalize_ticket_file(ticket_file):
    """Coerce ticket_file into the project's standard file-metadata shape:
    a list of dicts each containing 'file_url' (see file_repository.upload_file)."""
    if not ticket_file:
        return ticket_file
    if isinstance(ticket_file, str):
        return [{"file_url": ticket_file}]
    if isinstance(ticket_file, dict):
        return [ticket_file]
    return ticket_file


async def create_flight_purchase(db: AsyncSession, request: FlightPurchaseCreateSchema, agency_name: str, username: str):
    try:
        _validate_amounts(request.seats_purchased, request.cost)

        request_dict = request.model_dump(exclude_none=True)
        request_dict["agency_name"] = agency_name
        request_dict["created_by"] = username
        request_dict["updated_by"] = username
        if "ticket_file" in request_dict:
            request_dict["ticket_file"] = _normalize_ticket_file(request_dict["ticket_file"])

        result = await flight_purchase_repository.create_flight_purchase(db, request_dict)
        return FlightPurchaseResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def get_flight_purchases(db: AsyncSession, agency_name: str):
    try:
        result = await flight_purchase_repository.get_flight_purchases(db, agency_name)
        purchases = []
        for item in result:
            if item.ticket_file:
                item.ticket_file = await generate_downloadable_urls(_normalize_ticket_file(item.ticket_file))
            purchases.append(FlightPurchaseResponseSchema.model_validate(item))

        return FlightPurchaseListResponseSchema(flight_purchases=purchases)
    except Exception as e:
        raise e


async def get_flight_purchase_by_id(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        result = await flight_purchase_repository.get_flight_purchase_by_id(db, purchase_id, agency_name)
        if result.ticket_file:
            result.ticket_file = await generate_downloadable_urls(_normalize_ticket_file(result.ticket_file))
        return FlightPurchaseResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def update_flight_purchase(db: AsyncSession, request: FlightPurchaseUpdateSchema, agency_name: str, username: str):
    try:
        _validate_amounts(request.seats_purchased, request.cost)

        update_dict = request.model_dump(exclude_none=True)
        if "ticket_file" in update_dict:
            update_dict["ticket_file"] = _normalize_ticket_file(update_dict["ticket_file"])
        result = await flight_purchase_repository.update_flight_purchase(db, update_dict, agency_name, username)
        return FlightPurchaseResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_flight_purchase(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        result = await flight_purchase_repository.delete_flight_purchase(db, purchase_id, agency_name)
        return FlightPurchaseListResponseSchema(
            flight_purchases=[FlightPurchaseResponseSchema.model_validate(item) for item in result]
        )
    except Exception as e:
        raise e


async def get_flight_purchase_reconciliation(db: AsyncSession, agency_name: str):
    try:
        rows = await flight_purchase_repository.get_flight_purchase_reconciliation(db, agency_name)

        windows = [
            FlightPurchaseReconciliationItemSchema(
                flight_date_start={
                    "english_calendar": r["english_start"],
                    "arabic_calendar": r["arabic_start"],
                },
                flight_date_end={
                    "english_calendar": r["english_end"],
                    "arabic_calendar": r["arabic_end"],
                },
                number_of_hajji=r["number_of_hajji"],
                total_seats_purchased=r["total_seats_purchased"],
                remaining_seats=r["remaining_seats"],
            )
            for r in rows
        ]

        return FlightPurchaseReconciliationResponseSchema(windows=windows)
    except Exception as e:
        raise e
