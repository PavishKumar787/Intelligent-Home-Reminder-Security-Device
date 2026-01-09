import time
import cv2
import face_recognition
import numpy as np
from recognition.face_db import load_known_faces


_cache = {
    "names": [],
    "encodings": [],
    "timestamp": 0.0,
    "reload_interval": 5.0
}


def _get_known_faces():
    now = time.time()
    if (
        not _cache["names"]
        or now - _cache["timestamp"] > _cache["reload_interval"]
    ):
        try:
            names, encodings = load_known_faces()
            _cache["names"] = names
            _cache["encodings"] = encodings
            _cache["timestamp"] = now
        except Exception:
            pass
    return _cache["names"], _cache["encodings"]


def identify_person(frame):
    if frame is None:
        return None

    known_names, known_encodings = _get_known_faces()
    if not known_names or len(known_encodings) == 0:
        return None

    if not isinstance(frame, np.ndarray) or frame.ndim != 3:
        return None

    if frame.dtype != np.uint8:
        frame = frame.astype(np.uint8)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Force a fresh copy to guarantee strict C-contiguous memory layout for dlib
    rgb = np.array(rgb, dtype=np.uint8, order='C', copy=True)

    face_locations = face_recognition.face_locations(rgb)
    if not face_locations:
        return None

    encodings = face_recognition.face_encodings(rgb, face_locations)
    if not encodings:
        return None

    distances = face_recognition.face_distance(known_encodings, encodings[0])
    idx = np.argmin(distances)
    distance = distances[idx]

    MATCH_THRESHOLD = 0.45
    if distance < MATCH_THRESHOLD:
        return known_names[idx]

    return "STRANGER"
