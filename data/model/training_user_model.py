from sqlalchemy import Column, Integer, String, BigInteger

from data.model.base_mixin_model import Base, BaseMixinModel


class TrainingUserModel(Base, BaseMixinModel):
    __tablename__ = 'user_training_books'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=False, nullable=False)
    whats_app_no = Column(String, index=False, nullable=False)
    hajj_year = Column(Integer, nullable=True)
