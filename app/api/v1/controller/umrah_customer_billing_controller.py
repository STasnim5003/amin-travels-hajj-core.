import fastapi
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import umrah_customer_billing_service
from data.db.db_config import get_async_db
from infrastructure.schema.umrah_customer_billing_schema import UmrahCustomerBillingResponseSchema, \
    UmrahCustomerBillingBaseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Umrah Billing"])


@private_router.post("/umrah/customer-billing", response_model=UmrahCustomerBillingResponseSchema)
async def create_umrah_customer_billing(
        request: UmrahCustomerBillingBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user['agency_name']
    username = current_user['username']

    return await umrah_customer_billing_service.create_umrah_customer_billing(db=db, request=request,
                                                                              agency_name=agency_name,
                                                                              username=username)
