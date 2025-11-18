from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel


class HotelRequestModel(Base, BaseMixinModel):
    __tablename__ = "hotel_request"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    city = Column(String, nullable=False)
    type = Column(String, nullable=True)
    name = Column(String, nullable=True)
    tasria_number = Column(Integer, nullable=True)
    check_in = Column(JSONB, nullable=False)
    check_out = Column(JSONB, nullable=False)
    number_of_haji = Column(Integer, nullable=False)
    room_allocation = Column(JSONB, nullable=False)
    hotel_contact_person = Column(JSONB, nullable=True)
    status = Column(String, nullable=True)
    nusuk_request_id = Column(String, nullable=True)
    agency_name = Column(String, nullable=True)