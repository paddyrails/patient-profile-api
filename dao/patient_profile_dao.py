from sqlalchemy.orm import Session
from common.models.patient_profile import PatientProfile

class PatientProfileDAO:


    def get_all(self, db: Session):
        return db.query(PatientProfile).all()
    
    def get_by_id(self, db: Session, id: int):
        return db.query(PatientProfile).filter(PatientProfile.id == id).first()
    
    def get_by_mrn(self, db: Session, mrn: str):
        return db.query(PatientProfile).filter(PatientProfile.mrn == mrn).first()
    
    def get_by_email(self, db: Session, email: str):
        return db.query(PatientProfile).filter(PatientProfile.email == email).first()
    
    def create(self, db: Session, patient_profile: PatientProfile):
        db.add(patient_profile)
        db.commit()
        db.refresh(patient_profile)
        return patient_profile
    
    def update(self, db: Session, patient_profile:PatientProfile):
        db.commit()
        db.refresh(patient_profile)
        return patient_profile
    
    def delete(self, db: Session, patient_profile:PatientProfile):
        db.delete(patient_profile)
        db.commit()