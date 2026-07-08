from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Date, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from data.model.base_mixin_model import Base, BaseMixinModel


class PackageModel(Base, BaseMixinModel):
    __tablename__ = 'packages'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    discount = Column(String, nullable=True)
    price = Column(BigInteger, nullable=True)
    hajj_year = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=True)
    description_type = Column(String, nullable=True)
    package_type = Column(String, nullable=False)
    is_publish = Column(Boolean, nullable = True)


    # Existing JSON fields
    others_feature = Column(JSONB(astext_type=String), nullable=True)
    makkah = Column(JSONB(astext_type=String), nullable=True)
    azizia = Column(JSONB(astext_type=String), nullable=True)
    madinah = Column(JSONB(astext_type=String), nullable=True)
    includes = Column(JSONB(astext_type=String), nullable=True)
    hotel_info = Column(JSONB(astext_type=String), nullable=True)
    excludes = Column(JSONB(astext_type=String), nullable=True)

    # New fields from migration
    duration_range = Column(JSONB(astext_type=String), nullable=True)
    flight_date = Column(JSONB(astext_type=String), nullable=True)
    bed_type = Column(JSONB(astext_type=String), nullable=True)
    return_ticket = Column(String, nullable=True)
    fixed_or_shifting = Column(String, nullable=True)
    food_menu_id = Column(Integer, ForeignKey("core.food_menu.id"),nullable=True)
    ziara_id = Column(Integer, ForeignKey("core.ziara.id"),nullable=True)
    special_services = Column(JSONB(astext_type=String), nullable=True)
    other_services = Column(JSONB(astext_type=String), nullable=True)
    route_id = Column(Integer, ForeignKey("core.route.id"))
    airlines = Column(String, nullable=True)
    agency_name = Column(String, nullable=True)
    air_ticket = Column(JSONB(astext_type=String), nullable=True)
    transportation = Column(JSONB(astext_type=String), nullable=True)
    mina_and_arafah = Column(JSONB(astext_type=String), nullable=True)
    hajj_guide = Column(JSONB(astext_type=String), nullable=True)
    qurbani = Column(JSONB(astext_type=String), nullable=True)
    tayef_jeddah_ziyara = Column(JSONB(astext_type=String), nullable=True)
    additional_services = Column(JSONB(astext_type=String), nullable=True)
    important_notes = Column(JSONB(astext_type=String), nullable=True)
    required_add_ons = Column(JSONB(astext_type=String), nullable=True)

    route = relationship("RouteModel", backref="packages")
    ziara = relationship("ZiaraModel", backref="packages")
    food_menu = relationship("FoodMenuModel", backref="packages")

    @property
    def locations(self) -> dict:
        return {
            "makkah": self.makkah or [],
            "madinah": self.madinah or [],
            "azizia": self.azizia or [],
            "others_feature": self.others_feature or [],
        }

class PackageNameModel(Base, BaseMixinModel):
    __tablename__ = 'package_name'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    agency_name = Column(String, nullable=True)