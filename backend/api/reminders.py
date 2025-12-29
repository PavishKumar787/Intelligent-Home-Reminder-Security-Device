from fastapi import APIRouter
from db import update_reminders

router = APIRouter()

@router.post("/update-reminders")
def set_reminders(name: str, reminders: list[str]):
    success = update_reminders(name.lower(), reminders)
    if not success:
        return {"error": "User not found"}
    return {"status": "Reminders updated"}
