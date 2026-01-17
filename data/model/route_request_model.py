from sqlalchemy import Column, Integer, String, Float

from data.model.base_mixin_model import Base, BaseMixinModel
from sqlalchemy.dialects.postgresql import JSONB


class RouteRequestModel(Base, BaseMixinModel):
    __tablename__ = "route_request"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    arrival = Column(JSONB, nullable=True)
    departure = Column(JSONB, nullable=True)
    between_cities_up = Column(JSONB, nullable=True)
    between_cities_down = Column(JSONB, nullable=True)
    mashaer = Column(JSONB, nullable=True)
    total_price = Column(Float, nullable=False)
    agency_name = Column(String, nullable=False)
    status = Column(String, nullable=True)
    cancellation_status = Column(String, nullable=True)
