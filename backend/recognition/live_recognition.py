import cv2
import face_recognition
import numpy as np
from recognition.face_db import load_known_faces
import time

# Cache loaded faces with timestamp
_cache = {
    'names': [],
    'encodings': [],
    'timestamp': 0,
    'reload_interval': 5  # Reload every 5 seconds
}

def get_known_faces():
    """Get cached known faces, reload if needed"""
    current_time = time.time()
    
    # Reload if cache is empty or interval passed
    if (not _cache['names'] or 
        current_time - _cache['timestamp'] > _cache['reload_interval']):
        try:
            names, encodings = load_known_faces()
            _cache['names'] = names
            _cache['encodings'] = encodings
            _cache['timestamp'] = current_time
        except Exception as e:
            # Silently fail, keep old cache
            pass
    
    return _cache['names'], _cache['encodings']


def recognize_from_frame(frame):
    """
    Recognize face in a frame using face_recognition library
    
    Args:
        frame: BGR image frame from camera (uint8)
        
    Returns:
        (name, confidence) tuple or (None, None) if no face detected
    """
    try:
        known_names, known_encodings = get_known_faces()
        
        # Skip recognition if no known faces
        if not known_names or len(known_encodings) == 0:
            return None, None
        
        # Ensure frame is uint8 BGR
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        
        # Convert BGR to RGB (face_recognition requires RGB)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Make array contiguous
        rgb = np.ascontiguousarray(rgb)
        
        # Use face_recognition to detect face locations
        face_locations = face_recognition.face_locations(rgb)
        
        if not face_locations:
            return None, None

        # Get encoding for the first detected face
        encodings = face_recognition.face_encodings(rgb, face_locations)
        
        if not encodings or len(encodings) == 0:
            return None, None

        # Compare with known faces
        distances = face_recognition.face_distance(known_encodings, encodings[0])
        min_dist = np.min(distances)
        idx = np.argmin(distances)
        
        # Debug: Print distance for troubleshooting
        import random
        if random.random() < 0.03:
            print(f"Face detected - Distance to {known_names[idx]}: {min_dist:.3f}", flush=True)

        # Threshold tuned to reduce false positives; lower distance = better match (0.0 perfect, 1.0 none)
        RECOGNITION_THRESHOLD = 0.45
        
        if min_dist < RECOGNITION_THRESHOLD:
            confidence = 1 - min_dist  # Convert distance to confidence (0-1)
            return known_names[idx], confidence

        return "Unknown", 1 - min_dist
        
    except Exception as e:
        # Silently skip any errors during recognition
        return None, None
