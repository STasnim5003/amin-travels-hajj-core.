import json
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import text, case, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.pilgrim_data_schema import BulkUpdatePilgrimRequestSchema


async def fetch_pilgrim_data_json(
        db: AsyncSession,
        name: Optional[str] = None,
        tracking_id: Optional[str] = None,
        serial_no: Optional[str] = None,
        mobile_no: Optional[str] = None,
        group_name: Optional[str] = None,
        allocation_status: Optional[str] = None,
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

        if name:
            where_conditions.append("name_bn ILIKE :name_filter")
            params['name_filter'] = f"%{name}%"

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

        # Build WHERE clause
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        # PostgreSQL query using JSON aggregation and window function
        query = f"""
        WITH filtered_data AS (
            SELECT 
                id, name_bn, name_en, father_name, spouse_name, occupation, nid, voucher, type,
                listed_in, mother_name, date_of_birth, gender, management, mobile_no,
                passport_address, present_address, permanent_address, tracking_id,
                serial_no, group_name, registration_status, allocation_status,
                created_at, created_by, updated_at, updated_by, is_assigned,
                COUNT(*) OVER() as total_count
            FROM core.pilgrim_data
            {where_clause}
            ORDER BY created_at desc, id desc
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
                    'is_assigned', is_assigned
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

        # Handle the JSON data - it might be a string or already parsed
        data_json = row[0]  # Access by index to be safe
        total_count = row[1] if len(row) > 1 else 0

        # Parse JSON if it's a string
        if isinstance(data_json, str):
            data = json.loads(data_json)
        elif data_json is None:
            data = []
        else:
            data = data_json

        return data, total_count

    except Exception as e:
        print(f"Error fetching pilgrim data: {str(e)}")
        # Re-raise the exception to let the calling code handle it
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
        SELECT name_bn, father_name, mother_name, spouse_name, occupation, nid, voucher, type, listed_in,
               date_of_birth, gender, management, passport_address, present_address, permanent_address,
               serial_no, group_name, registration_status, tracking_id, mobile_no, is_assigned, updated_at,
               created_at, updated_by, created_by, id
        FROM core.pilgrim_data
        WHERE tracking_id = :tracking_id
    """)

    result = await db.execute(query, {"tracking_id": tracking_id})
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Pilgrim not found")

    return row
