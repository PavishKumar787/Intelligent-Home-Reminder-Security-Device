import json
import os

DB_FILE = "users.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_user(user):
    """Add or update user with embedding (supports multi-sample enrollment)"""
    data = load_db()
    user_name = user["name"].lower()
    
    # Check if user already exists
    for u in data:
        if u["name"] == user_name:
            # Initialize face_encodings if not exists (backward compatibility)
            if "face_encodings" not in u:
                if "face_encoding" in u:
                    u["face_encodings"] = [u["face_encoding"]]
                    del u["face_encoding"]
                else:
                    u["face_encodings"] = []
            # Add new embedding
            u["face_encodings"].append(user["face_encoding"])
            save_db(data)
            return
    
    # New user
    data.append({
        "name": user_name,
        "face_encodings": [user["face_encoding"]],
        "reminders": user.get("reminders", [])
    })
    save_db(data)

def add_user_embedding(name, embedding):
    """Add embedding to existing user (for multi-sample enrollment)"""
    users = load_db()
    user_name = name.lower()
    
    for u in users:
        if u["name"] == user_name:
            if "face_encodings" not in u:
                u["face_encodings"] = []
            u["face_encodings"].append(embedding.tolist())
            save_db(users)
            return True
    
    return False

def get_all_users():
    return load_db()

def get_user_by_name(name):
    users = load_db()
    for user in users:
        if user["name"] == name.lower():
            return user
    return None

def update_reminders(name, reminders):
    users = load_db()
    for user in users:
        if user["name"] == name.lower():
            user["reminders"] = reminders
            save_db(users)
            return True
    return False
