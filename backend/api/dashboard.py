from fastapi import APIRouter
from services.alert_service import get_alerts
from detection.state import current_detection

router = APIRouter()

@router.get("/alerts")
def alerts():
    return get_alerts()

@router.get("/current-detection")
def get_current_detection():
    return current_detection
