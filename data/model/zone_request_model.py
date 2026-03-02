from sqlalchemy import Column, Integer, String

from data.model.base_mixin_model import Base, BaseMixinModel
from sqlalchemy.dialects.postgresql import JSONB

class ZoneRequestModel(Base, BaseMixinModel):
    __tablename__ = "zone_request"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    agency_name = Column(String, nullable=False)
    details = Column(JSONB, nullable=True)
    remarks = Column(String, nullable=True)
    total_pilgrims = Column(Integer, nullable=True)