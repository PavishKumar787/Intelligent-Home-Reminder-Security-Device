import json
import os

# Use absolute path based on this file's location
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_user(user):
    """Add or update user with face encoding - supports multiple encodings per person"""
    data = load_db()
    user_name = user["name"].lower()
    new_encoding = user["face_encoding"]
    
    # Check if user already exists
    for u in data:
        if u["name"] == user_name:
            # Support multiple encodings per user
            if "face_encodings" not in u:
                # Migrate from single encoding to list
                if "face_encoding" in u:
                    u["face_encodings"] = [u["face_encoding"]]
                else:
                    u["face_encodings"] = []
            
            # Add new encoding to the list (max 10 encodings per person)
            if len(u["face_encodings"]) < 10:
                u["face_encodings"].append(new_encoding)
                print(f"Added encoding #{len(u['face_encodings'])} for user: {user_name}")
            else:
                # Replace oldest encoding if at max
                u["face_encodings"].pop(0)
                u["face_encodings"].append(new_encoding)
                print(f"Replaced oldest encoding for user: {user_name} (max 10 reached)")
            
            u["reminders"] = user.get("reminders", u.get("reminders", []))
            save_db(data)
            return
    
    # New user - store as list of encodings
    data.append({
        "name": user_name,
        "face_encodings": [new_encoding],
        "reminders": user.get("reminders", [])
    })
    save_db(data)
    print(f"Added new user: {user_name} with 1 encoding")

def add_user_embedding(name, embedding):
    """Update user's face encoding"""
    users = load_db()
    user_name = name.lower()
    
    for u in users:
        if u["name"] == user_name:
            u["face_encoding"] = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
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
