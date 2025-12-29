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

app = FastAPI(title="Smart Reminder & Surveillance System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(video_router)
app.include_router(enroll_router)
app.include_router(reminders_router)
app.include_router(re_enroll_router)
app.include_router(delete_user_router)

@app.on_event("startup")
def startup():
    thread = threading.Thread(target=start_processing, daemon=True)
    thread.start()

@app.get("/")
def root():
    return {"status": "System Running"}
