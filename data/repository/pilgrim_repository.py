import json
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy import text, case, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.pilgrim_data_schema import BulkUpdatePilgrimRequestSchema, PilgrimRegistrationRequestSchema


async def fetch_pilgrim_data_json(
        db: AsyncSession,
        name_en: Optional[str] = None,
        tracking_id: Optional[str] = None,
        serial_no: Optional[str] = None,
        mobile_no: Optional[str] = None,
        group_name: Optional[str] = None,
        allocation_status: Optional[str] = None,
        registration_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
):
    try:
        # Build WHERE conditions dynamically
        where_conditions = []
        params = {
            'skip_val': skip,
            'limit_val': limit
        }

        if name_en:
            where_conditions.append("name_en ILIKE :name_filter")
            params['name_filter'] = f"%{name_en}%"

        if tracking_id:
            where_conditions.append("tracking_id = :tracking_id")
            params['tracking_id'] = tracking_id

        if serial_no:
            where_conditions.append("serial_no = :serial_no")
            params['serial_no'] = serial_no

        if mobile_no:
            where_conditions.append("mobile_no = :mobile_no")
            params['mobile_no'] = mobile_no

        if allocation_status:
            where_conditions.append("allocation_status = :allocation_status")
            params['allocation_status'] = allocation_status

        if group_name:
            where_conditions.append("group_name ILIKE :group_name")
            where_conditions.append("is_assigned = :is_assigned")
            params['group_name'] = f"%{group_name}%"
            params['is_assigned'] = True

        if registration_status:
            # Use ANY array to filter multiple values
            where_conditions.append("registration_status = :registration_status")
            params['registration_status'] = registration_status

        # Build WHERE clause
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        # PostgreSQL query using JSON aggregation and window function
        query = f"""
            WITH filtered_data AS (
                SELECT 
                    p.id, p.name_bn, p.name_en, p.father_name, p.spouse_name, p.occupation, p.nid, p.voucher, p.type,
                    p.listed_in, p.mother_name, p.date_of_birth, p.gender, p.management, p.mobile_no,
                    p.passport_address, p.present_address, p.permanent_address, p.tracking_id,
                    p.serial_no, p.group_name, p.registration_status, p.allocation_status,
                    p.created_at, p.created_by, p.updated_at, p.updated_by, p.is_assigned, p.comment_on_package,
                    p.vaccination_center, p.passport_copy, p.package_id,
                    pkg.name, pkg.duration,
                    COUNT(*) OVER() as total_count
                FROM core.pilgrim_data p
                LEFT JOIN core.packages pkg ON p.package_id = pkg.id
                {where_clause}
                ORDER BY p.created_at DESC, p.id DESC
                LIMIT :limit_val OFFSET :skip_val
            ),
            result_data AS (
                SELECT 
                    JSON_BUILD_OBJECT(
                        'id', id,
                        'name_bn', name_bn,
                        'name_en', name_en,
                        'father_name', father_name,
                        'spouse_name', spouse_name,
                        'occupation', occupation,
                        'nid', nid,
                        'voucher', voucher,
                        'type', type,
                        'listed_in', listed_in,
                        'mother_name', mother_name,
                        'date_of_birth', date_of_birth,
                        'gender', gender,
                        'management', management,
                        'mobile_no', mobile_no,
                        'passport_address', passport_address,
                        'present_address', present_address,
                        'permanent_address', permanent_address,
                        'tracking_id', tracking_id,
                        'serial_no', serial_no,
                        'group_name', group_name,
                        'registration_status', registration_status,
                        'allocation_status', allocation_status,
                        'created_at', created_at,
                        'created_by', created_by,
                        'updated_at', updated_at,
                        'updated_by', updated_by,
                        'is_assigned', is_assigned,
                        'vaccination_center', vaccination_center,
                        'passport_copy', passport_copy,
                        'package_id', package_id,
                        'package_name', name,
                        'duration', duration,
                        'comment_on_package', comment_on_package
                    ) as item,
                    total_count
                FROM filtered_data
            )
            SELECT 
                COALESCE(JSON_AGG(item), '[]'::json) as data,
                COALESCE(MAX(total_count), 0) as total_count
            FROM result_data;
        """

        # Execute the query
        result = await db.execute(text(query), params)
        row = result.fetchone()

        if row is None:
            return [], 0

        # Handle the JSON data
        data_json = row[0]
        total_count = row[1] if len(row) > 1 else 0

        if isinstance(data_json, str):
            data = json.loads(data_json)
        elif data_json is None:
            data = []
        else:
            data = data_json

        return data, total_count

    except Exception as e:
        print(f"Error fetching pilgrim data: {str(e)}")
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
        )
    )

    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


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
    query = text("""
        SELECT 
            p.name_bn, p.name_en, p.father_name, p.mother_name, p.spouse_name, p.occupation, 
            p.nid, p.voucher, p.type, p.listed_in, p.date_of_birth, p.gender, p.management, 
            p.passport_address, p.present_address, p.permanent_address,p.serial_no, p.password,
            p.group_name, p.registration_status, p.tracking_id, p.mobile_no, p.is_assigned, 
            p.updated_at,p.created_at, p.updated_by, p.created_by, p.id, p.passport_copy, p.allocation_status,
            p.vaccination_center, p.comment_on_package,pkg.id AS package_id, pkg.name as package_name, pkg.duration
        FROM core.pilgrim_data p
        LEFT JOIN core.packages pkg 
            ON p.package_id = pkg.id
        WHERE p.tracking_id = :tracking_id
    """)

    result = await db.execute(query, {"tracking_id": tracking_id})
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Pilgrim not found")

    return row


async def pilgrim_register(db: AsyncSession, request_schema: PilgrimRegistrationRequestSchema):
    tracking_id = request_schema.tracking_id
    pilgrim = await get_pilgrim_by_tracking_id(db, tracking_id)
    if pilgrim is None:
        raise HTTPException(status_code=404, detail="Pilgrim not found")

    query = text("""
        UPDATE core.pilgrim_data
        SET 
            registration_status = 'APPLIED',
            vaccination_center = :vaccination_center,
            passport_copy = :passport_copy,
            package_id = :package_id,
            comment_on_package = :comment_on_package
        WHERE tracking_id = :tracking_id
    """)

    await db.execute(query, {
        "vaccination_center": request_schema.vaccination_center,
        "passport_copy": json.dumps(request_schema.passport_copy),
        "tracking_id": tracking_id,
        "package_id" : request_schema.package_id,
        "comment_on_package" : request_schema.comment_on_package
    })
    await db.commit()

    return {"message": "Pilgrim applied for registration successfully"}

