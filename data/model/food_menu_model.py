from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text

from data.model.base_mixin_model import BaseMixinModel, Base


class FoodMenuModel(Base, BaseMixinModel):
    __tablename__ = "food_menu"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    agency_name = Column(String, nullable=True)
    items = Column(JSONB, nullable=True)
    is_publish = Column(Boolean, server_default=text("false"), nullable=False)
