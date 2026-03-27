from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI(
    title="AI4Health Outbreak Prediction API",
    description="Backend for automated outbreak prediction and analytics.",
    version="1.0.0"
)

app.include_router(router)