from sqlalchemy import Column, Integer, String
from common.database import Base

class PatientProfile(Base):
    __tablename__ = 'patient_profiles'

    id = Column(Integer, primary_key=True, index=True)
    mrn = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)