from sqlalchemy.orm import Session
from dao.patient_profile_dao import PatientProfileDAO
from common.models.patient_profile import PatientProfile
from common.schemas.patient_profile import PatientProfileCreate, PatientProfileUpdate


dao = PatientProfileDAO()

class PatientProfileService:

    def get_all(self, db: Session):
        return dao.get_all(db)
    
    def get_by_id(self, db: Session, id: int):
        patient_profile = dao.get_by_id(db, id)
        if not patient_profile:
            raise ValueError(f'patient profile with id {id} not found')
        return patient_profile
    
    
    def get_by_mrn(self, db: Session, mrn: str):
        patient_profile = dao.get_by_mrn(db, mrn)
        if not patient_profile:
            raise ValueError(f'patient profile with mrn {mrn} not found')
        return patient_profile
    

    def get_by_email(self, db: Session, email: str):
        patient_profile = dao.get_by_email(db, email)
        if not patient_profile:
            raise ValueError(f'patient profile with email {email} not found')
        return patient_profile
    

    def create(self, db:Session, data: PatientProfileCreate):
        self._validate(db, data)
        patient_profile = PatientProfile(
            mrn = data.mrn,
            first_name = data.first_name,
            last_name = data.last_name,
            gender = data.gender,
            email = data.email,
            phone = data.phone,
            address = data.address
        )
        return dao.create(db, patient_profile)
    

    def update(self, db:Session, id: int, data: PatientProfileUpdate):
        patient_profile = self.get_by_id(db, id )
        if data.mrn:
            existing = dao.get_by_mrn(db, data.mrn)
            if existing and existing.id != id:
                raise ValueError(f'MRN {data.mrn} is already in use')
        if data.email:
            existing = dao.get_by_email(db, data.email)
            if(existing) and existing.id != id:
                raise ValueError(f'MRN {data.email} is already in use')
            
        if data.mrn is not None:
            patient_profile.mrn = data.mrn
        if data.first_name is not None:
            patient_profile.first_name = data.first_name
        if data.last_name is not None:
            patient_profile.last_name = data.last_name
        if data.last_name is not None:
            patient_profile.last_name = data.last_name
        if data.gender is not None:
            patient_profile.gender = data.gender
        if data.email is not None:
            patient_profile.email = data.email
        if data.phone is not None:
            patient_profile.phone = data.phone
        if data.address is not None:
            patient_profile.address = data.address

        return dao.update(db, patient_profile)
    
    def delete(self, db: Session, id: int):
        patient_profile = dao.get_by_id(db, id)
        dao.delete(patient_profile)

    def _validate(self, db: Session, data: PatientProfileCreate):
        if dao.get_by_mrn(db, data.mrn):
            raise ValueError(f'MRN {data.mrn} already exists')
        if dao.get_by_email(db, data.email):
            raise ValueError(f'Email {data.email} alerady exists')