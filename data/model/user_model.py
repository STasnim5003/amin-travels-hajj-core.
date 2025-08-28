from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel
from data.model.package_model import PackageModel


class UserModel(Base, BaseMixinModel):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    whats_app_no = Column(String, index=True, nullable=False)
    nid_images = Column(JSONB, nullable=False)
    hajj_year = Column(Integer, nullable=True)
    discount_category = Column(Integer, nullable=True, default=0)
    package_id = Column(Integer, ForeignKey(PackageModel.id), nullable=True)
    payment_status = Column(String, nullable=False, default="PENDING")
    passport_images = Column(JSONB, nullable=True)
    vaccine_center = Column(String, nullable=True)
    registration_status = Column(String, nullable=False, default="PREREGISTERED")
    username = Column(String, index=True, nullable=True)
    password = Column(String, nullable=True)
    role = Column(String, index=True, nullable=False, default="PREREGISTERED_USER")