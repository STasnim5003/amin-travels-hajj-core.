from typing import List

from fastapi import HTTPException
from sqlalchemy import insert, select, update, delete, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_model import AdminModel
from data.model.hotel_request_model import HotelRequestModel
from data.model.pilgrim_data_model import PilgrimDataModel


async def create_hotel_request(db: AsyncSession, request_dict: dict):
    try:
        hotel_request_data = request_dict.copy()
        sar_value = hotel_request_data.pop("sar", None)
        hotel_requested = hotel_request_data.pop("hotel_requested", None)

        stmt = (
            insert(HotelRequestModel)
            .values(**hotel_request_data)
            .returning(HotelRequestModel)
        )
        result = await db.execute(stmt)

        update_values = {}

        if sar_value is not None:
            update_values["sar"] = sar_value

        if hotel_requested is not None:
            update_values["hotel_requested"] = hotel_requested

        if update_values:
            await db.execute(
                update(AdminModel)
                .where(AdminModel.agency_name == request_dict["agency_name"])
                .values(**update_values)
            )

        await db.commit()
        return result.scalar_one_or_none()

    except Exception as e:
        await db.rollback()
        raise e
async def get_hotel_requests(db: AsyncSession, agency_name: List[str]):
    try:
        query = """
            SELECT
                tasria_number,
                (t.check_in ->> 'english_calendar') AS check_in,
                (t.check_out ->> 'english_calendar') AS check_out,
                rfq_no,
                COUNT(*) AS merge_count,
                jsonb_agg(to_jsonb(t) ORDER BY id DESC) AS rows_json
            FROM core.hotel_request t
            WHERE t.agency_name = ANY(:agency_name)
            GROUP BY tasria_number, check_in, check_out, rfq_no;
        """


        result=await db.execute(
            text(query),
            {"agency_name": agency_name}
        )
        return result.mappings().all()
    except Exception as e:
        raise e

async def get_hotel_request_by_id(db:AsyncSession, request_id:int):
    try:
        stmt = select(HotelRequestModel).where(HotelRequestModel.id == request_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e

async def update_hotel_request(db:AsyncSession, request_dict: dict):
    try:
        sar_value = request_dict.pop("sar", None)
        hotel_requested = request_dict.pop("hotel_requested", None)
        agency_name = request_dict.pop("agency_name", None)

        stmt = (update(HotelRequestModel)
                .where(HotelRequestModel.id == request_dict['id'])
                .values(**request_dict)
                .returning(HotelRequestModel))
        result = await db.execute(stmt)

        update_values = {}

        if sar_value is not None:
            update_values["sar"] = sar_value

        if hotel_requested is not None:
            update_values["hotel_requested"] = hotel_requested

        if update_values:
            await db.execute(
                update(AdminModel)
                .where(AdminModel.agency_name == agency_name)
                .values(**update_values)
            )


        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_hotel_request(db:AsyncSession, request_id:int, request_dict:dict):
    try:
        stmt = delete(HotelRequestModel).where(HotelRequestModel.id == request_id)
        await db.execute(stmt)

        update_stmt = (update(AdminModel)
                       .values(
                            sar=request_dict.get("sar"),
                            hotel_requested=request_dict.get("hotel_requested"),
                        )
                       .where(AdminModel.agency_name == request_dict["agency_name"]))
        await db.execute(update_stmt)

        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e

async def get_madinah_allocated_and_total_seat(db:AsyncSession, agency_name:str):
    try:
        # Query 1: Allocated Hotel Seat
        hotel_stmt = (
            select(
                HotelRequestModel.city,
                HotelRequestModel.agency_name,
                func.sum(HotelRequestModel.number_of_haji).label("hotel_allocated_hajji")
            )
            .where(
                HotelRequestModel.city == "Madinah",
                HotelRequestModel.agency_name == agency_name
            )
            .group_by(
                HotelRequestModel.city,
                HotelRequestModel.agency_name
            )
        )

        hotel_result = await db.execute(hotel_stmt)
        hotel_row = hotel_result.first()

        # Query 2: Total pilgrims
        pilgrim_stmt = (
            select(
                PilgrimDataModel.group_name,
                func.count(PilgrimDataModel.tracking_id).label("total_pilgrims")
            )
            .where(PilgrimDataModel.group_name == agency_name)
            .group_by(PilgrimDataModel.group_name)
        )

        pilgrim_result = await db.execute(pilgrim_stmt)
        pilgrim_row = pilgrim_result.first()

        # Build JSON-safe response
        return {
            "city": hotel_row.city if hotel_row else "Madinah",
            "agency_name": agency_name,
            "hotel_allocated_hajji": hotel_row.hotel_allocated_hajji if hotel_row else 0,
            "total_pilgrims": pilgrim_row.total_pilgrims if pilgrim_row else 0
        }

    except Exception as e:
        raise e


async def cancel_hotel_request(db:AsyncSession, request_dict : dict):
    try:
        stmt = (update(HotelRequestModel)
                .where(HotelRequestModel.id == request_dict['id'])
                .values(**request_dict)
                .returning(HotelRequestModel))
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def cancel_request_lead_agency_action(db:AsyncSession, request_dict:dict):
    try:
        stmt = (update(HotelRequestModel)
                .where(HotelRequestModel.id == request_dict['id'])
                .values(**request_dict)
                .returning(HotelRequestModel))
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e