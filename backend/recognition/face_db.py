import json
import numpy as np

DB_PATH = "users.json"

def load_known_faces():
    """Load enrolled faces from database"""
    try:
        with open(DB_PATH, "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        print(f"Database {DB_PATH} not found. No known faces loaded.")
        return [], []

    names = []
    encodings = []

    for u in users:
        if u.get("name") and u.get("face_encoding"):
            names.append(u["name"])
            encodings.append(np.array(u["face_encoding"], dtype=np.float32))

    print(f"Loaded {len(names)} known faces from database")
    return names, encodings
