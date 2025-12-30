import uuid
from datetime import datetime, timedelta
from services.alert_store import alerts

# Debug: Print store ID to verify same instance is used everywhere
print(f"🔗 alert_service.py loaded - ALERT STORE ID: {id(alerts)}")

DUPLICATE_SUPPRESS_SECONDS = 60

def create_alert(alert_type, message):
    print(f"📥 create_alert called with type={alert_type}, message={message}")
    print(f"📥 ALERT STORE ID: {id(alerts)}, Current count BEFORE: {len(alerts)}")

    now = datetime.now()

    # Prevent duplicate alerts unless the previous one is older than the suppression window
    existing_match = next((a for a in alerts if a.get("message") == message), None)
    if existing_match:
        existing_time_str = existing_match.get("timestamp")
        within_window = False
        if existing_time_str:
            try:
                existing_time = datetime.fromisoformat(existing_time_str)
                within_window = (now - existing_time) < timedelta(seconds=DUPLICATE_SUPPRESS_SECONDS)
            except ValueError:
                within_window = True  # Fallback to suppress if timestamp is invalid
        if within_window:
            print(f"📥 Duplicate alert suppressed for {message}")
            return existing_match

    alert = {
        "id": str(uuid.uuid4()),
        "type": alert_type,
        "message": message,
        "timestamp": now.isoformat(),
        "read": False
    }
    alerts.append(alert)
    print(f"⚠️ Alert ADDED to list: {message}")
    print(f"📥 ALERT STORE ID: {id(alerts)}, Current count AFTER: {len(alerts)}")
    # Keep only last 50 alerts
    if len(alerts) > 50:
        alerts.pop(0)
    return alert

def get_alerts():
    # Return alerts in reverse order (newest first)
    print(f"📋 get_alerts called - ALERT STORE ID: {id(alerts)}, count: {len(alerts)}")
    return list(reversed(alerts))

def mark_alert_read(alert_id):
    for alert in alerts:
        if alert["id"] == alert_id:
            alert["read"] = True
            return True
    return False

def clear_alerts():
    """Clear all alerts"""
    print(f"🗑️ clear_alerts called - ALERT STORE ID: {id(alerts)}")
    alerts.clear()

def clear_stranger_alerts():
    """Remove all stranger-related alerts"""
    print(f"🗑️ clear_stranger_alerts called - ALERT STORE ID: {id(alerts)}")
    # Use slice assignment to modify in-place (keeps same list reference)
    alerts[:] = [a for a in alerts if "Stranger" not in a.get("message", "")]
    print(f"🗑️ After clearing stranger alerts: {len(alerts)} remaining")
