# Pydantic models for API requests/responses
from pydantic import BaseModel

class AnalyticsResponse(BaseModel):
    message: str
