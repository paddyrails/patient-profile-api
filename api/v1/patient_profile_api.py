from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from common.database import get_db
from common.schemas.patient_profile import PatientProfileCreate, PatientProfileUpdate, PatientProfileResponse
from services.patient_profile_service import PatientProfileService
from typing import List
from common.limiter import limiter

router = APIRouter(prefix="/api/v1/patient-profiles", tags=["Patient Profiles"]) 

service = PatientProfileService()

# Get all Patient Profiles
@router.get("/", response_model=List[PatientProfileResponse])
@limiter.limit("10/minute")
def get_all(request: Request, db: Session = Depends(get_db)):
    return service.get_all(db)

#Get Patient by id
@router.get("/{id}", response_model=PatientProfileResponse)
@limiter.limit("10/minute")
def get_by_id(request: Request, id: int, db: Session = Depends(get_db)):
    try:
        return service.get_by_id(db, id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
#Create Patient profile
@router.post("/", response_model=PatientProfileResponse, status_code=201)
@limiter.limit("3/minute")
def create(request: Request, data: PatientProfileCreate, db: Session = Depends(get_db)):
    try:
        return service.create(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
#Update Patient Profile
@router.put("/{id}", response_model=PatientProfileResponse)
@limiter.limit("3/minute")
def update(request: Request, id: int, data: PatientProfileUpdate, db: Session = Depends(get_db)):
    try:
        return service.update(db, id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Delete Patient Profile
@router.delete("/{id}", status_code=200)
@limiter.limit("3/minute")
def delete(request: Request, id: int, db: Session = Depends(get_db)):
    try:
        return service.delete(db, id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    
