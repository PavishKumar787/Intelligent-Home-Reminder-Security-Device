from fastapi import APIRouter
from db import load_db, save_db

router = APIRouter()

@router.delete("/delete-user")
def delete_user(name: str):
    users = load_db()
    updated = [u for u in users if u["name"] != name.lower()]

    if len(updated) == len(users):
        return {"error": "User not found"}

    save_db(updated)
    return {"status": f"{name} removed successfully"}
