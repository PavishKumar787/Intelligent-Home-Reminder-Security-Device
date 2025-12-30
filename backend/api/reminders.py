from fastapi import APIRouter
from pydantic import BaseModel
from db import update_reminders, get_user_by_name
from typing import List

router = APIRouter()

class UpdateRemindersRequest(BaseModel):
    name: str
    reminders: List[str]

@router.post("/update-reminders")
def set_reminders(request: UpdateRemindersRequest):
    success = update_reminders(request.name.lower(), request.reminders)
    if not success:
        return {"error": "User not found"}
    return {"status": "Reminders updated", "reminders": request.reminders}

@router.get("/user-reminders")
def get_user_reminders(name: str):
    """Get reminders for a specific user"""
    user = get_user_by_name(name.lower())
    if not user:
        return {"error": "User not found"}
    return {"name": user["name"], "reminders": user.get("reminders", [])}
