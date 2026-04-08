from sqlalchemy import Column, Integer, String, DateTime, Boolean, text

from data.model.base_mixin_model import BaseMixinModel, Base


class UmrahHotelBooking(Base, BaseMixinModel):
    __tablename__ = "umrah_hotel_booking"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    res_no = Column(String, nullable=False)
    guest_name = Column(String, nullable=False)
    hotel_name = Column(String, nullable=False)

    room_type = Column(String)
    mp = Column(String)
    qty = Column(String)
    check_in = Column(String)
    check_out = Column(String)
    remarks = Column(String)

    agency_name = Column(String)
