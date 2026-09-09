from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel


class FlightPurchaseModel(Base, BaseMixinModel):
    __tablename__ = "flight_purchase"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    agency_name = Column(String, nullable=False)

    # Mirrors the shape returned by GET /flight-demand (english_calendar/arabic_calendar
    # keys) so a purchase can be created directly from a demand window and matched back
    # to it later for reconciliation.
    flight_date_start = Column(JSONB, nullable=False)
    flight_date_end = Column(JSONB, nullable=False)

    airline_name = Column(String, nullable=False)
    vendor_name = Column(String, nullable=True)
    pnr = Column(String, nullable=False)
    seats_purchased = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="BDT")
    purchase_date = Column(String, nullable=True)
    ticket_file = Column(JSONB, nullable=True)
    remarks = Column(String, nullable=True)
