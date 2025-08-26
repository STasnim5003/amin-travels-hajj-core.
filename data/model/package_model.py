from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Text, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property

from data.model.base_mixin_model import Base, BaseMixinModel



class PackageModel(Base, BaseMixinModel):
    __tablename__ = 'packages'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    discount = Column(String, nullable=True)
    price = Column(BigInteger,  nullable=True)
    hajj_year = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=True)
    description_type = Column(String, nullable=True)
    package_type = Column(String, nullable=False)
    hajj_month = Column(String, nullable=True)
    others_feature = Column(JSONB(astext_type=String), nullable=True)
    makkah = Column(JSONB(astext_type=String), nullable=True)
    azizia = Column(JSONB(astext_type=String), nullable=True)
    madinah = Column(JSONB(astext_type=String), nullable=True)
    includes = Column(JSONB(astext_type=String), nullable=True)
    hotel_info = Column(JSONB(astext_type=String), nullable=True)
    excludes = Column(JSONB(astext_type=String), nullable=True)
    discount_deadline = Column(Date, nullable=True)

    @property
    def locations(self) -> dict:
        return {
            "makkah": self.makkah or [],
            "madinah": self.madinah or [],
            "azizia": self.azizia or [],
            "others_feature": self.others_feature or [],
        }

