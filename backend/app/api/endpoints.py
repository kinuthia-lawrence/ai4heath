from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping():
    return {"message": "Pong"}

@router.get("/analytics")
def get_analytics():
    # Placeholder for returning analytics results
    return {"message": "Analytics results"}

