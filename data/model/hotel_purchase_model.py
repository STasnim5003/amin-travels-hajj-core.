from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel


class HotelPurchaseModel(Base, BaseMixinModel):
    __tablename__ = "hotel_purchase"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    agency_name = Column(String, nullable=False)

    # Matches the bucket key returned by GET /hotel-demand (city + checkin/checkout +
    # category) so a purchase can be created directly from a demand row and matched
    # back to it later for reconciliation.
    city = Column(String, nullable=False)
    category = Column(String, nullable=False)
    checkin = Column(String, nullable=False)
    checkout = Column(String, nullable=False)

    hotel_name = Column(String, nullable=False)
    vendor_name = Column(String, nullable=True)

    # {bed_type: room_count}, mirrors GET /hotel-demand's room_and_number_of_hajji
    rooms_purchased = Column(JSONB, nullable=False)

    cost = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="BDT")
    purchase_date = Column(String, nullable=True)
    booking_file = Column(JSONB, nullable=True)
    remarks = Column(String, nullable=True)
