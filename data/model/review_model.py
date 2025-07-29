from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Text
from data.model.base_mixin_model import Base, BaseMixinModel
from data.model.package_model import PackageModel
from data.model.user_model import UserModel


class ReviewModel(Base, BaseMixinModel):
    __tablename__ = 'reviews'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    reviewer = Column(BigInteger, ForeignKey(UserModel.id), index=True, nullable=False)
    description = Column(Text, nullable=False)
    package_id = Column(BigInteger, ForeignKey(PackageModel.id), nullable=False)