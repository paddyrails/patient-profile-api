from fastapi import APIRouter
from api.v1.patient_profile_api import router as patient_profile_router

router = APIRouter()
router.include_router(patient_profile_router)