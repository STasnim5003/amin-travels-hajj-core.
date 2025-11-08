from sqlalchemy import Column, Integer, String

from data.model.base_mixin_model import Base,BaseMixinModel


class CityNameModelForUmrah(Base, BaseMixinModel):
    __tablename__ = 'city_name'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    agency_name = Column(String, nullable=True)