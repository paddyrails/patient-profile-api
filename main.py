from fastapi import FastAPI
from common.database import engine, Base
from api import router
from common.limiter import limiter  
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Patient Profile Api",
    version="1.0.0",
    description="API for managing patient profiles"
)

app.state.limiter = limiter                                                                                                                  
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(router)