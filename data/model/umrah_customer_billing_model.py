from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import BaseMixinModel, Base


class UmrahCustomerBillingModel(Base, BaseMixinModel):
    __tablename__ = "umrah_customer_billing"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String, nullable=False)
    description = Column(String, nullable=True)
    way_of_payment = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=True)
    remarks = Column(String, nullable=True)
    receipt = Column(JSONB, nullable=True)
    agency_name = Column(String, nullable=False)
