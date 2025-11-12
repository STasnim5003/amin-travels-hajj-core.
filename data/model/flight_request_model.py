from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base,BaseMixinModel


class FlightRequestModel(Base, BaseMixinModel):
    __tablename__ = "flight_request"
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    total_seat = Column(Integer, nullable=False)
    flight_name = Column(String, nullable=False)
    arrival_route = Column(Integer, nullable=False)
    arrival_date_option_1 = Column(JSONB, nullable=True)
    arrival_date_option_2 = Column(JSONB, nullable=True)
    departure_route = Column(Integer, nullable=False)
    departure_date_option_1 = Column(JSONB, nullable=True)
    departure_date_option_2 = Column(JSONB, nullable=True)
    agency_name = Column(String, nullable=True)
    duration = Column(String, nullable=True)
