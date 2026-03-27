from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import BaseMixinModel, Base


class UmrahVendorBillingModel(Base, BaseMixinModel):
    __tablename__ = "umrah_vendor_billing"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    umrah_requisition_code = Column(String, nullable=False)
    invoice_no = Column(String, nullable=False)
    guest_name = Column(String, nullable=False)

    vendor_name = Column(String, nullable=False)
    description = Column(JSONB, nullable=True)

    bill = Column(Float, nullable=False)
    credit = Column(Float, nullable=False)

    payment_date = Column(String, nullable=False)
    remarks = Column(String, nullable=True)
    agency_name = Column(String, nullable=True)
