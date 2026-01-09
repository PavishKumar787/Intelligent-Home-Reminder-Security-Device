import json
import numpy as np
import os

# Use absolute path based on backend folder
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "users.json")

def load_known_faces():
    """Load enrolled faces from database - supports multiple encodings per person"""
    try:
        with open(DB_PATH, "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        print(f"Database {DB_PATH} not found. No known faces loaded.")
        return [], []

    names = []
    encodings = []

    for u in users:
        name = u.get("name")
        if not name:
            continue
            
        # Support both old format (face_encoding) and new format (face_encodings)
        if "face_encodings" in u and u["face_encodings"]:
            # New format: multiple encodings per person
            for enc in u["face_encodings"]:
                names.append(name)
                encodings.append(np.array(enc, dtype=np.float64))
        elif "face_encoding" in u and u["face_encoding"]:
            # Old format: single encoding
            names.append(name)
            encodings.append(np.array(u["face_encoding"], dtype=np.float64))

    print(f"Loaded {len(encodings)} face encodings for {len(set(names))} users")
    return names, encodings
