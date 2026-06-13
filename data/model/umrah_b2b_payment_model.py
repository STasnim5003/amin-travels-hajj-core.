from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel


class UmrahB2BPayment(BaseMixinModel, Base):
    __tablename__ = "umrah_b2b_payements"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=True)
    way_of_payment = Column(String, nullable=True)

    amount = Column(Float, nullable=False)

    payment_date = Column(Date, nullable=True)
    remarks = Column(String, nullable=True)

    agency_name = Column(String, nullable=True)
    invoice_no = Column(String, nullable=True)
    b2b_agent_name = Column(String, nullable=True)
