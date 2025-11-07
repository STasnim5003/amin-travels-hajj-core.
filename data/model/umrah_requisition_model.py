from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel


class UmrahRequisitionModel(Base, BaseMixinModel):
    __tablename__ = "umrah_requisition"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    number_of_traveller = Column(Integer, nullable=False)
    adult_traveller = Column(Integer, nullable=False)
    other_traveller = Column(JSONB, nullable=True)
    is_visa = Column(Boolean, nullable=False)
    with_hotel_brn = Column(Boolean, nullable=True)
    air_ticket = Column(Boolean, nullable=False)
    air_ticket_category = Column(String, nullable=True)
    airline_preference = Column(String, nullable=True)
    flight_data = Column(JSONB, nullable=True)
    hotel_info = Column(JSONB, nullable=False)
    transport = Column(JSONB, nullable=False)
    remarks = Column(String, nullable=False)
    agency_name = Column(String, nullable=False)

