from sqlalchemy import Column, String, BigInteger, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel


class AdminModel(Base, BaseMixinModel):
    __tablename__ = 'admin'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    profile_pic = Column(JSONB, nullable=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="ADMIN")
    is_active = Column(Boolean, nullable=False, default=True)
