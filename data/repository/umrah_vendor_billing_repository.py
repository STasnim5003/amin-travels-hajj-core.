from sqlalchemy import insert, text, select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.umrah_vendor_billing_model import UmrahVendorBillingModel


async def create_umrah_vendor_billing(db: AsyncSession, request_dict: dict):
    try:
        stmt = (
            insert(UmrahVendorBillingModel)
            .values(**request_dict)
            .returning(UmrahVendorBillingModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_vendor_billing(db: AsyncSession, agency_name: str):
    try:
        query = text("""
                SELECT
                    ur.amin_office_code,
                    ur.name,
                    ur.number_of_traveller,
                
                    (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'vendor_name', h -> 'price' ->> 'vendor_name',
                                'vendor_price', h -> 'price' ->> 'vendor_price',
                                'details', jsonb_build_object(
                                    'city', h ->> 'city',
                                    'check_in', h ->> 'check_in',
                                    'check_out', h ->> 'check_out',
                                    'room_type', h ->> 'room_type'
                                )
                            )
                        )
                        FROM jsonb_array_elements(ur.hotel_info) h
                    ) AS hotels,
                
                    (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'vendor_name', t -> 'price' ->> 'vendor_name',
                                'vendor_price', t -> 'price' ->> 'vendor_price',
                                'details', jsonb_build_object(
                                    'route_id', t ->> 'route_id',
                                    'transport', t ->> 'transport',
                                    'route_description', t ->> 'route_description'
                                )
                            )
                        )
                        FROM jsonb_array_elements(ur.transport) t
                    ) AS transports,
                
                    jsonb_build_object(
                        'vendor_name', ur.visa_price ->> 'vendor_name',
                        'vendor_price', ur.visa_price ->> 'vendor_price',
                        'details', NULL
                    ) AS visa,
                
                    jsonb_build_object(
                        'vendor_name', ur.air_ticket_price ->> 'vendor_name',
                        'vendor_price', ur.air_ticket_price ->> 'vendor_price',
                        'details', NULL
                    ) AS air_ticket,
                
                    jsonb_build_object(
                        'vendor_name', ur.train_price ->> 'vendor_name',
                        'vendor_price', ur.train_price ->> 'vendor_price',
                        'details', NULL
                    ) AS train,
                
                    jsonb_build_object(
                        'vendor_name', ur.guide_price ->> 'vendor_name',
                        'vendor_price', ur.guide_price ->> 'vendor_price',
                        'details', NULL
                    ) AS guide,
                
                    jsonb_build_object(
                        'vendor_name', ur.ziara_price ->> 'vendor_name',
                        'vendor_price', ur.ziara_price ->> 'vendor_price',
                        'details', NULL
                    ) AS ziara,
                
                    jsonb_build_object(
                        'vendor_name', ur.food_price ->> 'vendor_name',
                        'vendor_price', ur.food_price ->> 'vendor_price',
                        'details', NULL
                    ) AS food,
                
                    jsonb_build_object(
                        'vendor_name', ur.others_price ->> 'vendor_name',
                        'vendor_price', ur.others_price ->> 'vendor_price',
                        'details', NULL
                    ) AS others,
                
                    jsonb_build_object(
                        'visa', jsonb_build_object(
                            'vendor_name', ur.child_service -> 'visa' ->> 'vendor_name',
                            'vendor_price', ur.child_service -> 'visa' ->> 'vendor_price',
                            'details', NULL
                        ),
                        'hotel', jsonb_build_object(
                            'vendor_name', ur.child_service -> 'hotelbed' ->> 'vendor_name',
                            'vendor_price', ur.child_service -> 'hotelbed' ->> 'vendor_price',
                            'details', NULL
                        ),
                        'air_ticket', jsonb_build_object(
                            'vendor_name', ur.child_service -> 'airticket' ->> 'vendor_name',
                            'vendor_price', ur.child_service -> 'airticket' ->> 'vendor_price',
                            'details', NULL
                        )
                    ) AS child_services,
                
                    jsonb_build_object(
                        'visa', jsonb_build_object(
                            'vendor_name', ur.infant_service -> 'visa' ->> 'vendor_name',
                            'vendor_price', ur.infant_service -> 'visa' ->> 'vendor_price',
                            'details', NULL
                        ),
                        'hotel', jsonb_build_object(
                            'vendor_name', ur.infant_service -> 'hotelbed' ->> 'vendor_name',
                            'vendor_price', ur.infant_service -> 'hotelbed' ->> 'vendor_price',
                            'details', NULL
                        ),
                        'air_ticket', jsonb_build_object(
                            'vendor_name', ur.infant_service -> 'airticket' ->> 'vendor_name',
                            'vendor_price', ur.infant_service -> 'airticket' ->> 'vendor_price',
                            'details', NULL
                        )
                    ) AS infant_services,
                
                    (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'vendor_name', uvb.vendor_name,
                                'vendor_price', uvb.credit,
                                'details', jsonb_build_object(
                                    'bill', uvb.bill,
                                    'payment_date', uvb.payment_date,
                                    'description', uvb.description
                                )
                            )
                        )
                        FROM core.umrah_vendor_billing uvb
                        WHERE uvb.amin_office_code = ur.amin_office_code
                    ) AS payments
                
                FROM core.umrah_requisition ur
                WHERE ur.agency_name = :agency_name
                ORDER BY ur.amin_office_code DESC;
            """)

        result = await db.execute(query, {"agency_name": agency_name})
        return result.mappings().all()
    except Exception as e:
        raise e


async def get_vendor_billing_summary(db:AsyncSession, agency_name:str, vendor_name:str):
    try:
        stmt = (
            select(UmrahVendorBillingModel)
            .where(UmrahVendorBillingModel.vendor_name == vendor_name, UmrahVendorBillingModel.agency_name==agency_name)
        )

        result = await db.execute(stmt)
        return result.scalars()
    except Exception as e:
        raise e

async def get_umrah_all_vendor_billing(db:AsyncSession, agency_name:str):
    try:
        query = text("""
            WITH base_requisition AS (
    SELECT
        id,
        amin_office_code,
        agency_name,

        COALESCE(visa_price, '{}'::jsonb) AS visa_price,
        COALESCE(air_ticket_price, '{}'::jsonb) AS air_ticket_price,
        COALESCE(food_price, '{}'::jsonb) AS food_price,
        COALESCE(ziara_price, '{}'::jsonb) AS ziara_price,
        COALESCE(train_price, '{}'::jsonb) AS train_price,

        COALESCE(child_service, '{}'::jsonb) AS child_service,
        COALESCE(infant_service, '{}'::jsonb) AS infant_service,

        COALESCE(hotel_info, '[]'::jsonb) AS hotel_info,
        COALESCE(transport, '[]'::jsonb) AS transport,
        COALESCE(guide_price, '[]'::jsonb) AS guide_price

    FROM core.umrah_requisition
    WHERE agency_name = :agency_name
),

vendor_services AS (

    -- VISA
    SELECT
        ur.amin_office_code,
        ur.id,
        'VISA' AS service,
        COALESCE(ur.visa_price->>'vendor_name', '') AS vendor_name,
        COALESCE((ur.visa_price->>'vendor_price')::numeric, 0)
        + COALESCE((ur.child_service->'visa'->>'vendor_price')::numeric, 0)
        + COALESCE((ur.infant_service->'visa'->>'vendor_price')::numeric, 0) AS vendor_price,
        NULL::jsonb AS details
    FROM base_requisition ur

    UNION ALL

    -- AIR TICKET
    SELECT
        ur.amin_office_code,
        ur.id,
        'AIR_TICKET',
        COALESCE(ur.air_ticket_price->>'vendor_name', ''),
        COALESCE((ur.air_ticket_price->>'vendor_price')::numeric, 0)
        + COALESCE((ur.child_service->'airticket'->>'vendor_price')::numeric, 0)
        + COALESCE((ur.infant_service->'airticket'->>'vendor_price')::numeric, 0),
        NULL::jsonb
    FROM base_requisition ur

    -- FOOD
    UNION ALL
    SELECT
        ur.amin_office_code,
        ur.id,
        'FOOD',
        COALESCE(ur.food_price->>'vendor_name', ''),
        COALESCE((ur.food_price->>'vendor_price')::numeric, 0),
        NULL::jsonb
    FROM base_requisition ur

    -- ZIARA
    UNION ALL
    SELECT
        ur.amin_office_code,
        ur.id,
        'ZIARA',
        COALESCE(ur.ziara_price->>'vendor_name', ''),
        COALESCE((ur.ziara_price->>'vendor_price')::numeric, 0),
        NULL::jsonb
    FROM base_requisition ur

    -- TRAIN
    UNION ALL
    SELECT
        ur.amin_office_code,
        ur.id,
        'TRAIN',
        COALESCE(ur.train_price->>'vendor_name', ''),
        COALESCE((ur.train_price->>'vendor_price')::numeric, 0),
        NULL::jsonb
    FROM base_requisition ur

    -- HOTEL
    UNION ALL
    SELECT
        ur.amin_office_code,
        ur.id,
        'HOTEL',
        COALESCE(item->'price'->>'vendor_name', ''),
        COALESCE((item->'price'->>'vendor_price')::numeric, 0),
        item->'room_type'
    FROM base_requisition ur
    CROSS JOIN LATERAL jsonb_array_elements(ur.hotel_info) item

    -- TRANSPORT
    UNION ALL
    SELECT
        ur.amin_office_code,
        ur.id,
        'TRANSPORT',
        COALESCE(item->'price'->>'vendor_name', ''),
        COALESCE((item->'price'->>'vendor_price')::numeric, 0),
        item->'transport'
    FROM base_requisition ur
    CROSS JOIN LATERAL jsonb_array_elements(ur.transport) item

    -- GUIDE
    UNION ALL
    SELECT
        ur.amin_office_code,
        ur.id,
        'GUIDE',
        COALESCE(item->>'vendor_name', ''),
        COALESCE((item->>'vendor_price')::numeric, 0),
        NULL::jsonb
    FROM base_requisition ur
    CROSS JOIN LATERAL jsonb_array_elements(ur.guide_price) item
),

vendor_payments AS (
    SELECT
        COALESCE(vendor_name, '') AS vendor_name,
        COALESCE(category, '') AS category,

        COALESCE(SUM(amount), 0) AS total_vendor_payment,

        COALESCE(
            jsonb_agg(
                jsonb_build_object(
                    'invoice_no', invoice_no,
                    'amount', amount,
                    'payment_date', payment_date,
                    'id', id
                )
                ORDER BY id DESC
            ),
            '[]'::jsonb
        ) AS payments

    FROM core.umrah_vendor_billing
    WHERE agency_name = :agency_name
    GROUP BY vendor_name, category
)

SELECT
    vs.vendor_name,
    vs.service,

    COALESCE(SUM(vs.vendor_price), 0) AS total_vendor_price,
    COALESCE(vp.total_vendor_payment, 0) AS total_vendor_payment,

    COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'amin_office_code', vs.amin_office_code,
                'vendor_price', COALESCE(vs.vendor_price, 0),
                'details', vs.details
            )
        ),
        '[]'::jsonb
    ) AS requisitions,

    COALESCE(
        vp.payments,
        jsonb_build_array(
            jsonb_build_object(
                'invoice_no', NULL,
                'amount', NULL,
                'payment_date', NULL,
                'id', NULL
            )
        )
    ) AS payments

FROM vendor_services vs

LEFT JOIN vendor_payments vp
    ON vp.vendor_name = vs.vendor_name
   AND vp.category = vs.service

WHERE COALESCE(vs.vendor_name, '') <> ''

GROUP BY
    vs.vendor_name,
    vs.service,
    vp.total_vendor_payment,
    vp.payments;
            """)

        result = await db.execute(query, {"agency_name": agency_name})
        return result.mappings().all()
    except Exception as e:
        raise e