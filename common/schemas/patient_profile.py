from pydantic import BaseModel, EmailStr
from typing import Optional

class PatientProfileBase(BaseModel):
    mrn: str
    first_name: str
    last_name: str
    gender: str
    email: EmailStr
    phone: str
    address: str

class PatientProfileCreate(PatientProfileBase):
    pass

class PatientProfileUpdate(BaseModel):
    mrn: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class PatientProfileResponse(PatientProfileBase):
    id: int

    class Config:
        from_attrubutes: True