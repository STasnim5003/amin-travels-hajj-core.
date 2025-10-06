from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel


class ZiaraModel(Base, BaseMixinModel):
    __tablename__ = "ziara"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    agency_name = Column(String, nullable=True)