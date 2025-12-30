from fastapi import APIRouter
from services.alert_store import alerts  # Import shared store directly
from services.alert_service import get_alerts, clear_alerts
from detection.state import current_detection
from db import get_all_users, get_user_by_name

# Debug: Print store ID to verify same instance
print(f"🔗 dashboard.py loaded - ALERT STORE ID: {id(alerts)}")

router = APIRouter()

@router.get("/health")
def health_check():
    """Check if the system is active and running"""
    return {"status": "active", "message": "System is running"}

@router.get("/alerts")
def get_alerts_endpoint():
    print(f"📋 GET /alerts - ALERT STORE ID: {id(alerts)}, count: {len(alerts)}")
    result = get_alerts()
    print(f"📋 GET /alerts returning {len(result)} alerts")
    return result

@router.delete("/alerts")
def delete_all_alerts():
    """Clear all alerts"""
    clear_alerts()
    return {"message": "All alerts cleared"}

@router.get("/current-detection")
def get_current_detection():
    # If a known face is detected, include their reminders
    detection = dict(current_detection)
    if detection.get("isKnown") and detection.get("name"):
        user = get_user_by_name(detection["name"])
        if user:
            detection["reminders"] = user.get("reminders", [])
        else:
            detection["reminders"] = []
    else:
        detection["reminders"] = []
    return detection

@router.get("/users")
def get_users():
    """Get all enrolled users with their reminders (without face encodings)"""
    users = get_all_users()
    return [
        {
            "name": user["name"],
            "reminders": user.get("reminders", [])
        }
        for user in users
    ]
