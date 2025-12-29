import cv2
import mediapipe as mp
import face_recognition
import numpy as np
from recognition.face_db import load_known_faces

mp_face_detection = mp.solutions.face_detection.FaceDetection(
    model_selection=1,
    min_detection_confidence=0.6
)

known_names, known_encodings = load_known_faces()

def recognize_from_frame(frame):
    """
    Recognize face in a frame using MediaPipe detection + face_recognition encoding
    
    Args:
        frame: BGR image frame from camera
        
    Returns:
        (name, confidence) tuple or (None, None) if no face detected
    """
    global known_names, known_encodings
    
    # Reload faces if database was updated
    if not known_names:
        known_names, known_encodings = load_known_faces()
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    detections = mp_face_detection.process(rgb).detections

    if not detections:
        return None, None

    # Get bounding box from first detection
    h, w, _ = frame.shape
    box = detections[0].location_data.relative_bounding_box

    x1 = int(box.xmin * w)
    y1 = int(box.ymin * h)
    x2 = int((box.xmin + box.width) * w)
    y2 = int((box.ymin + box.height) * h)

    # Crop face from RGB image
    face_img = rgb[y1:y2, x1:x2]

    # Extract encoding from face
    encodings = face_recognition.face_encodings(face_img)
    if not encodings:
        return None, None

    # Compare with known faces
    distances = face_recognition.face_distance(known_encodings, encodings[0])
    min_dist = np.min(distances)

    if min_dist < 0.45:  # Good threshold for face_recognition
        idx = np.argmin(distances)
        confidence = 1 - min_dist  # Convert distance to confidence (0-1)
        return known_names[idx], confidence

    return "Unknown", None
