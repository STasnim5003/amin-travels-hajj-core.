from sqlalchemy import Column, BigInteger, String
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import BaseMixinModel, Base


class ViewFieldModel(Base,BaseMixinModel):
    __tablename__ = 'pilgrim_view_field'
    __table_args__ = {'schema': 'core'}

    id: int = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    view_name: str = Column(String, nullable=False)
    username: str = Column(String, nullable=False)
    field_name: dict = Column(JSONB, nullable=False)
