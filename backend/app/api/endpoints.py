from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to the AI4Health API"}
    
@router.get("/ping")
def ping():
    return {"message": "Pong"}

@router.get("/analytics")
def get_analytics():
    # Placeholder for returning analytics results
    return {"message": "Analytics results"}

