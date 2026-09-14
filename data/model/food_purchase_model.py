from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel


class FoodPurchaseModel(Base, BaseMixinModel):
    __tablename__ = "food_purchase"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    agency_name = Column(String, nullable=False)

    # Matches FoodDemandResponse.food_name returned by GET /food-demand so a
    # purchase can be created directly from a demand row and matched back to it
    # later for reconciliation.
    food_name = Column(String, nullable=False)
    items = Column(JSONB, nullable=True)

    vendor_name = Column(String, nullable=True)
    meals_purchased = Column(Integer, nullable=False)

    cost = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="BDT")
    purchase_date = Column(String, nullable=True)
    booking_file = Column(JSONB, nullable=True)
    remarks = Column(String, nullable=True)
