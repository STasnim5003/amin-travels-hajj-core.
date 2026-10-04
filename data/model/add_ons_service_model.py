from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text
from data.model.base_mixin_model import Base, BaseMixinModel


class AddOnsServiceModel(Base, BaseMixinModel):
    __tablename__ = "add_ons_service"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(JSONB, nullable=True)
    price = Column(String, nullable=False)
    agency_name = Column(String, nullable=True)
    hajj_year = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),nullable=True)
    updated_at = Column(DateTime(timezone=True),server_default=text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),onupdate=text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    is_active = Column(Boolean, server_default=text("true"), nullable=False)
