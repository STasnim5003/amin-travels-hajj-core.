from sqlalchemy import Column, String, Integer, BigInteger, Date, DateTime, Boolean, ForeignKey, text
from sqlalchemy.orm import relationship
from data.model.base_mixin_model import Base, BaseMixinModel  # assuming you have Base from declarative_base()


class GetTogetherProgramCreate(Base, BaseMixinModel):
    __tablename__ = "get_together_program_create"
    __table_args__ = {"schema": "core"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    program_date = Column(Date, nullable=True)
    registration_deadline = Column(Date, nullable=True)
    program_venue = Column(String, nullable=True)
    total_seat = Column(Integer, nullable=True)
    description = Column(String, nullable=True)

    # relationship
    registrations = relationship("GetTogetherRegistration", back_populates="program")


class GetTogetherRegistration(Base, BaseMixinModel):
    __tablename__ = "get_together_registration"
    __table_args__ = {"schema": "core"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone_no = Column(String, nullable=False)
    no_of_attendance = Column(Integer, nullable=False)
    get_together_program_id = Column(BigInteger, ForeignKey(GetTogetherProgramCreate.id), nullable=False)

    # relationship
    program = relationship("GetTogetherProgramCreate", back_populates="registrations")
