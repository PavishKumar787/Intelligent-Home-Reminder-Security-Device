alerts = []

def create_alert(alert_type, message):
    alert = {
        "type": alert_type,
        "message": message
    }
    alerts.append(alert)
    return alert

def get_alerts():
    return alerts
