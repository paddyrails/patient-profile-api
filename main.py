from fastapi import FastAPI
from common.database import engine, Base
from api import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="patient profile api",
    version="1.0.0",
    description="API for managing patient profiles"
)

app.include_router(router)