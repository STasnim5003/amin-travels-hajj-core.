import json
import json
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy import text, case, update, func, select, exists, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.payment_model import PaymentModel
from data.model.pilgrim_data_model import PilgrimDataModel, ReplacedPilgrimModel, \
    TrainingSessionAndPreRegisterEnquiryPilgrim
from infrastructure.schema.pilgrim_data_schema import BulkUpdatePilgrimRequestSchema, PilgrimRegistrationRequestSchema, \
    PilgrimFamilyGroupAssign


async def fetch_pilgrim_data_json(
        db: AsyncSession,
        name_en: Optional[str] = None,
        tracking_id: Optional[str] = None,
        serial_no: Optional[str] = None,
        mobile_no: Optional[str] = None,
        group_name: Optional[str] = None,
        allocation_status: Optional[str] = None,
        registration_status: Optional[str] = None,
        group_leader: Optional[str] = None,
        show_customers: bool = True,
        is_package_assigned: Optional[bool] = None,
        hajj_year: Optional[int] = None,
        skip: int = 0,
        limit: int = 10,
        family_code: Optional[str] = None,
        group_name_filter: Optional[str] = None,
        sub_group: Optional[str] = None,
        package_name: Optional[str] = None,
        passport_no: Optional[str] = None,
        package_bed_type: Optional[str] = None,
        package_duration: Optional[int] = None,
        is_nrb: Optional[bool] = None,
):
    try:
        where_conditions = []
        params = {
            "skip_val": skip,
            "limit_val": limit,
        }

        if name_en:
            where_conditions.append("p.name_en ILIKE :name_filter")
            params["name_filter"] = f"%{name_en}%"

        if tracking_id:
            where_conditions.append("p.tracking_id = :tracking_id")
            params["tracking_id"] = tracking_id

        if serial_no:
            where_conditions.append("p.serial_no = :serial_no")
            params["serial_no"] = serial_no

        if mobile_no:
            where_conditions.append("p.mobile_no = :mobile_no")
            params["mobile_no"] = mobile_no

        if allocation_status:
            where_conditions.append("p.allocation_status = :allocation_status")
            params["allocation_status"] = allocation_status

        if group_name:
            # Agencies see every pilgrim in their group, assigned or not.
            where_conditions.append("p.group_name ILIKE :group_name")
            params["group_name"] = f"%{group_name}%"

        if registration_status:
            where_conditions.append(
                "p.registration_status = :registration_status"
            )
            params["registration_status"] = registration_status

        if group_leader:
            where_conditions.append("p.group_leader = :group_leader")
            params["group_leader"] = group_leader

        if not show_customers:
            where_conditions.append("p.tracking_id IS NOT NULL")

        if is_package_assigned is not None:
            where_conditions.append(
                "p.is_package_assigned = :is_package_assigned"
            )
            params["is_package_assigned"] = is_package_assigned

        if hajj_year is not None:
            where_conditions.append("p.hajj_year = :hajj_year")
            params["hajj_year"] = hajj_year

        for column, value in (
                ("family_code", family_code),
                ("group_name", group_name_filter),
                ("sub_group", sub_group),
                ("package_name", package_name),
                ("passport_no", passport_no),
        ):
            if value:
                where_conditions.append(f"p.{column} ILIKE :f_{column}")
                params[f"f_{column}"] = f"%{value}%"

        if package_bed_type:
            where_conditions.append("p.package_bed_types ILIKE :package_bed_type")
            params["package_bed_type"] = f"%{package_bed_type}%"

        if package_duration is not None:
            where_conditions.append("p.package_duration = :package_duration")
            params["package_duration"] = package_duration

        if is_nrb is not None:
            has_second_nationality = "COALESCE(BTRIM(p.second_nationality), '') <> ''"
            where_conditions.append(has_second_nationality if is_nrb else f"NOT ({has_second_nationality})")

        where_clause = (
            "WHERE " + " AND ".join(where_conditions)
            if where_conditions
            else ""
        )

        # Status count CTE
        if group_name:
            status_count_conditions = [
                "group_name = :status_group_name",
                "allocation_status IN ('ASSIGNED', 'UNASSIGNED', 'WALK_IN')"
            ]

            params["status_group_name"] = group_name

            if hajj_year is not None:
                status_count_conditions.append(
                    "hajj_year = :status_hajj_year"
                )
                params["status_hajj_year"] = hajj_year

            status_count_where = " AND ".join(
                status_count_conditions
            )

            status_count_cte = f"""
            status_counts AS (
                SELECT JSON_OBJECT_AGG(registration_status, count)
                    AS registration_status_count
                FROM (
                    SELECT
                        registration_status,
                        COUNT(*) AS count
                    FROM core.pilgrim_data
                    WHERE {status_count_where}
                    GROUP BY registration_status
                ) registration_counts
            )
            """

            status_count_select = """
                (SELECT registration_status_count
                 FROM status_counts)
                 AS registration_status_count,
                NULL AS allocation_status_count
            """

        else:
            status_count_conditions = []

            if hajj_year is not None:
                status_count_conditions.append(
                    "hajj_year = :status_hajj_year"
                )
                params["status_hajj_year"] = hajj_year

            status_count_where = (
                f"WHERE {' AND '.join(status_count_conditions)}"
                if status_count_conditions
                else ""
            )

            status_count_cte = f"""
            status_counts AS (
                SELECT JSON_OBJECT_AGG(allocation_status, count)
                    AS allocation_status_count
                FROM (
                    SELECT
                        allocation_status,
                        COUNT(*) AS count
                    FROM core.pilgrim_data
                    {status_count_where}
                    GROUP BY allocation_status
                ) allocation_counts
            )
            """

            status_count_select = """
                NULL AS registration_status_count,
                (SELECT allocation_status_count
                 FROM status_counts)
                 AS allocation_status_count
            """

        query = f"""
        WITH filtered_data AS (
            SELECT
                p.*,
                COUNT(*) OVER() AS total_count
            FROM core.pilgrim_data p
            {where_clause}
            ORDER BY p.created_at DESC, p.id DESC
            LIMIT :limit_val OFFSET :skip_val
        ),
        result_data AS (
            SELECT
                TO_JSONB(filtered_data) - 'total_count' AS item,
                total_count
            FROM filtered_data
        ),
        {status_count_cte}
        SELECT
            (
                SELECT COALESCE(
                    JSON_AGG(item),
                    '[]'::json
                )
                FROM result_data
            ) AS data,
            (
                SELECT COALESCE(
                    MAX(total_count),
                    0
                )
                FROM result_data
            ) AS total_count,
            {status_count_select};
        """

        result = await db.execute(text(query), params)
        row = result.fetchone()

        if not row:
            return [], 0, {}, {}

        data = (
            json.loads(row[0])
            if isinstance(row[0], str)
            else row[0]
        ) or []

        total_count = row[1] or 0
        registration_status_count = row[2] or {}
        allocation_status_count = row[3] or {}

        return (
            data,
            total_count,
            registration_status_count,
            allocation_status_count,
        )

    except Exception as e:
        print(f"Error fetching pilgrim data: {e}")
        raise


async def update_pilgrim_approval_status(
        data: BulkUpdatePilgrimRequestSchema,
        db: AsyncSession,
        username: str
):
    tracking_ids = [item.tracking_id for item in data.data]

    group_name_cases = case(
        *[
            (PilgrimDataModel.tracking_id == item.tracking_id, item.group_name)
            for item in data.data
        ]
    )

    is_assigned_cases = case(
        *[
            (PilgrimDataModel.tracking_id == item.tracking_id, item.is_assigned)
            for item in data.data
        ]
    )

    allocation_status_cases = case(
        *[
            (
                PilgrimDataModel.tracking_id == item.tracking_id,
                "ASSIGNED" if item.is_assigned else "UNASSIGNED"
            )
            for item in data.data
        ]
    )

    stmt = (
        update(PilgrimDataModel)
        .where(PilgrimDataModel.tracking_id.in_(tracking_ids))
        .values(
            group_name=group_name_cases,
            is_assigned=is_assigned_cases,
            allocation_status=allocation_status_cases,
            updated_by=username,
            updated_at=func.now()
        ).returning(PilgrimDataModel)
    )

    result = await db.execute(stmt)
    await db.commit()

    updated_pilgrims = result.scalars().all()  # returns list of PilgrimDataModel objects
    return updated_pilgrims


async def get_pilgrim_by_mobile_no(db: AsyncSession, mobile_no: str):
    query = text("""
            SELECT name_bn, tracking_id, mobile_no, password
            FROM core.pilgrim_data
            WHERE mobile_no = :mobile_no
        """)
    result = await db.execute(query, {"mobile_no": mobile_no})
    row = result.fetchone()
    return row


async def get_pilgrim_by_tracking_id(db: AsyncSession, tracking_id: str):
    try:
        query = text("""
            SELECT 
                p.name_bn, p.name_en, p.father_name, p.mother_name, p.spouse_name, p.occupation, 
                p.nid, p.voucher, p.type, p.listed_in, p.date_of_birth, p.gender, p.management, 
                p.passport_address, p.present_address, p.permanent_address,p.serial_no, p.password,
                p.group_name,p.sub_group, p.registration_status, p.tracking_id, p.mobile_no, p.is_assigned, 
                p.updated_at,p.created_at, p.updated_by, p.created_by, p.id, p.passport_copy, p.allocation_status,
                p.vaccination_center, p.comment_on_package, p.package_name, p.package_duration, p.package_bed_types,
                p.total_payable, p.total_payment, p.total_available_amount,
                 p.total_due, p.add_ons_services, p.is_package_assigned,
                p.payment_against, p.group_leader, p.actual_payable, p.package_price_discount,
                p.second_nationality
            FROM core.pilgrim_data p
            WHERE p.tracking_id = :tracking_id
        """)

        result = await db.execute(query, {"tracking_id": tracking_id})
        row = result.fetchone()

        if not row:
            raise HTTPException(status_code=400, detail="Pilgrim not found")

        return row
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def pilgrim_register(db: AsyncSession, request_schema: PilgrimRegistrationRequestSchema):
    tracking_id = request_schema.tracking_id
    pilgrim = await get_pilgrim_by_tracking_id(db, tracking_id)
    if pilgrim is None:
        raise HTTPException(status_code=404, detail="Pilgrim not found")

    stmt = (
        update(PilgrimDataModel)  # your ORM model
        .where(PilgrimDataModel.tracking_id == tracking_id)
        .values(
            registration_status='APPLIED',
            vaccination_center=request_schema.vaccination_center,
            passport_copy=request_schema.passport_copy,
            package_id=request_schema.package_id,
            comment_on_package=request_schema.comment_on_package
        )
        .returning(PilgrimDataModel)  # important: RETURNING to get updated object
    )

    result = await db.execute(stmt)
    updated_pilgrim = result.scalar_one_or_none()  # returns the updated ORM object or None
    await db.commit()

    if not updated_pilgrim:
        raise HTTPException(status_code=400, detail="Failed to update pilgrim data")

    return updated_pilgrim


async def get_pilgrim_by_id(db: AsyncSession, pilgrim_id: int):
    try:
        query = (
            select(PilgrimDataModel)
            .where(PilgrimDataModel.id == pilgrim_id)
        )

        result = await db.execute(query)
        row = result.scalars().one_or_none()

        if not row:
            raise HTTPException(
                status_code=400,
                detail=f"Pilgrim with id {pilgrim_id} not found."
            )

        return row

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred while fetching pilgrim by ID."
        )


async def get_pilgrims_by_tracking_ids(db, tracking_ids: list[str], for_update: bool = False):
    stmt = select(PilgrimDataModel).where(PilgrimDataModel.tracking_id.in_(tracking_ids))
    if for_update:
        stmt = stmt.with_for_update()
    result = await db.execute(stmt)
    return result.scalars().all()


async def assign_family_code(db: AsyncSession, request_body: PilgrimFamilyGroupAssign):
    try:
        result = await db.execute(
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id.in_(request_body.tracking_ids))
            .values(family_code=request_body.family_code)
            .returning(PilgrimDataModel)
        )

        await db.commit()
        return result.scalars().all()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def is_family_codes_available(db: AsyncSession, family_code: str, hajj_year: int, exclude_tracking_ids: list = None):
    try:
        conditions = [
            PilgrimDataModel.family_code == family_code,
            PilgrimDataModel.hajj_year == hajj_year,
        ]
        if exclude_tracking_ids:
            conditions.append(PilgrimDataModel.tracking_id.notin_(exclude_tracking_ids))

        query = select(exists().where(*conditions))

        result = await db.execute(query)

        return bool(result.scalar())

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def replace_pilgrim(db: AsyncSession, request_dict: dict, replaced_dict: dict, replaced_details_dict: dict):
    try:
        update_stmt = (
            update(PilgrimDataModel)
            .where(PilgrimDataModel.id == replaced_dict['id'])
            .values(**replaced_dict)
            .returning(PilgrimDataModel)
        )

        result = await db.execute(update_stmt)

        insert_stmt = (
            insert(PilgrimDataModel)
            .values(**request_dict)
        )

        await db.execute(insert_stmt)

        replaced_details_insert_stmt = (
            insert(ReplacedPilgrimModel)
            .values(**replaced_details_dict)
        )

        await db.execute(replaced_details_insert_stmt)

        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def archive_pilgrims(db: AsyncSession, tracking_ids: List[str], update_data: dict):
    try:
        stmt = (
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id.in_(tracking_ids))
            .values(**update_data)
            .returning(PilgrimDataModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalars().all()
    except Exception as e:
        await db.rollback()
        raise e


async def get_replaced_pilgrims(db: AsyncSession, agency_name: str):
    try:
        stmt = (
            select(ReplacedPilgrimModel)
            .where(ReplacedPilgrimModel.agency_name == agency_name)
        )

        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e


async def pre_register_enquiry_or_book_training_session(db: AsyncSession, request_dict: dict):
    try:
        stmt = (
            insert(TrainingSessionAndPreRegisterEnquiryPilgrim)
            .values(**request_dict)
            .returning(TrainingSessionAndPreRegisterEnquiryPilgrim)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_pre_register_enquiry_training_session_pilgrims(db: AsyncSession, agency_name: str):
    try:
        stmt = select(TrainingSessionAndPreRegisterEnquiryPilgrim)
        if agency_name:
            stmt = stmt.where(TrainingSessionAndPreRegisterEnquiryPilgrim.agency_name == agency_name)

        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_pilgrim_agreement_by_family_code(
    db: AsyncSession,
    family_code: str,
    agency_name: str,
):
    try:
        # Every pilgrim of the family is returned, each pointing at its own package via package_id
        # (null when the package no longer matches). Each package's details are listed once in `packages`.
        query = text("""
            WITH fam AS (
                SELECT p.*, pk.id AS matched_package_id
                FROM core.pilgrim_data p
                LEFT JOIN LATERAL (
                    SELECT pk.id FROM core.packages pk
                    WHERE pk.name = p.package_name
                      AND pk.duration = p.package_duration
                      AND pk.agency_name = p.group_name
                    ORDER BY pk.id DESC
                    LIMIT 1
                ) pk ON true
                WHERE p.family_code = :family_code
                  AND p.group_name = :agency_name
            )
            SELECT
                :family_code AS family_code,

                (
                    SELECT coalesce(jsonb_object_agg(pk.id::text, jsonb_build_object(
                        'package_id', pk.id,
                        'package_name', pk.name,
                        'duration', pk.duration,
                        'duration_range', pk.duration_range,
                        'makkah', pk.makkah,
                        'madinah', pk.madinah,
                        'azizia', pk.azizia,
                        'flight_date', pk.flight_date,
                        'return_ticket', pk.return_ticket,
                        'fixed_or_shifting', pk.fixed_or_shifting,
                        'air_ticket', pk.air_ticket,
                        'transportation', CASE WHEN jsonb_typeof(pk.transportation) = 'array' THEN (
                            SELECT jsonb_agg(to_jsonb(replace(t.line, 'will be required', 'is added as add ons')) ORDER BY t.ord)
                            FROM jsonb_array_elements_text(pk.transportation) WITH ORDINALITY AS t(line, ord)
                        ) ELSE pk.transportation END,
                        'mina_and_arafah', pk.mina_and_arafah,
                        'hajj_guide', pk.hajj_guide,
                        'qurbani', pk.qurbani,
                        'tayef_jeddah_ziyara', pk.tayef_jeddah_ziyara,
                        'additional_services', pk.additional_services,
                        'important_notes', NULL::jsonb,
                        'required_add_ons', pk.required_add_ons
                    )), '{}'::jsonb)
                    FROM core.packages pk
                    WHERE pk.id IN (SELECT f.matched_package_id FROM fam f)
                ) AS packages,

                -- json (not jsonb) keeps the room types in the order the admin entered them
                (
                    SELECT json_object_agg(pk.id::text, pk.bed_type)
                    FROM core.packages pk
                    WHERE pk.id IN (SELECT f.matched_package_id FROM fam f)
                ) AS bed_types,

                jsonb_agg(
                    jsonb_build_object(
                        'tracking_id', fam.tracking_id,
                        'name_en', fam.name_en,
                        'passport_no', fam.passport_no,
                        'package_id', fam.matched_package_id,
                        'package_name', fam.package_name,
                        'package_duration', fam.package_duration,
                        'package_bed_types', fam.package_bed_types,
                        'add_ons_services', fam.add_ons_services,
                        'total_payable', fam.total_payable,
                        'package_price_discount', coalesce(fam.package_price_discount, 0),
                        'actual_payable', fam.actual_payable
                    )
                    ORDER BY (fam.matched_package_id IS NULL), fam.matched_package_id, fam.name_en
                ) AS pilgrims
            FROM fam
            HAVING count(*) > 0;
        """)

        result = await db.execute(
            query,
            {
                "family_code": family_code,
                "agency_name": agency_name,
            },
        )

        row = result.mappings().first()
        if not row:
            return None

        agreement = dict(row)
        bed_types = agreement.pop("bed_types") or {}
        if isinstance(bed_types, str):
            bed_types = json.loads(bed_types)
        for package_id, package in agreement["packages"].items():
            package["bed_type"] = bed_types.get(package_id)
        # Deprecated: kept until the frontend reads packages[pilgrim.package_id]. Package of the first pilgrim.
        first_package_id = agreement["pilgrims"][0].get("package_id") if agreement["pilgrims"] else None
        agreement["package_info"] = agreement["packages"].get(str(first_package_id)) if first_package_id else None
        return agreement

    except Exception:
        raise


async def manual_pre_registration(db:AsyncSession, request_dict:dict):
    try:
        stmt = (
            insert(PilgrimDataModel)
            .values(**request_dict)
            .returning(PilgrimDataModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def has_payments(db: AsyncSession, tracking_id: str) -> bool:
    stmt = select(exists().where(PaymentModel.tracking_id == tracking_id))
    return bool((await db.execute(stmt)).scalar())


async def delete_pilgrim(db:AsyncSession, tracking_id:str):
    try:
        stmt = (
            delete(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id == tracking_id)
        )

        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e
