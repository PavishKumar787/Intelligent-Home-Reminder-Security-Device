import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from api.dashboard import router as dashboard_router
from api.video import router as video_router
from api.enroll import router as enroll_router
from api.reminders import router as reminders_router
from api.re_enroll import router as re_enroll_router
from api.delete_user import router as delete_user_router
import threading
from processor import start_processing
from services.alert_store import alerts  # Import shared store directly
from services.alert_service import clear_alerts, create_alert


def get_allowed_origins():
    default_origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
    ]

    extra_origins = os.getenv("FRONTEND_ORIGINS", "")
    parsed_extras = [origin.strip() for origin in extra_origins.split(",") if origin.strip()]
    default_origins.extend(parsed_extras)

    return list(dict.fromkeys(default_origins))

# Debug: Print store ID to verify same instance
print(f"🔗 main.py loaded - ALERT STORE ID: {id(alerts)}")

app = FastAPI(title="Smart Reminder & Surveillance System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(dashboard_router)
app.include_router(video_router)
app.include_router(enroll_router)
app.include_router(reminders_router)
app.include_router(re_enroll_router)
app.include_router(delete_user_router)

@app.on_event("startup")
def startup():
    # Clear old alerts on startup
    clear_alerts()
    print("✓ Alerts cleared on startup")
    
    thread = threading.Thread(target=start_processing, daemon=True)
    thread.start()

@app.get("/")
def root():
    return {"status": "System Running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
