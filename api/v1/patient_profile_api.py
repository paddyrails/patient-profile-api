from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.database import get_db
from common.schemas.patient_profile import PatientProfileCreate, PatientProfileUpdate, PatientProfileResponse
from services.patient_profile_service import PatientProfileService
from typing import List

router = APIRouter(prefix="/api/v1/patient-profiles", tags=["Patient Profiles"]) 

service = PatientProfileService()

# Get all Patient Profiles
@router.get("/", response_model=List[PatientProfileResponse])
def get_all(db: Session = Depends(get_db)):
    return service.get_all(db)

#Get Patient by id
@router.get("/{id}", response_model=PatientProfileResponse)
def get_by_id(id: int, db: Session = Depends(get_db)):
    try:
        return service.get_by_id(db, id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
#Create Patient profile
@router.post("/", response_model=PatientProfileResponse, status_code=201)
def create(data: PatientProfileCreate, db: Session = Depends(get_db)):
    try:
        return service.create(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
#Update Patient Profile
@router.put("/{id}", response_model=PatientProfileResponse)
def update(id: int, data: PatientProfileUpdate, db: Session = Depends(get_db)):
    try:
        return service.update(db, id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Delete Patient Profile
@router.delete("/{id}", status_code=200)
def delete(id: int, db: Session = Depends(get_db)):
    try:
        return service.delete(db, id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    
