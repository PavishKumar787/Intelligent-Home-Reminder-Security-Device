from fastapi import APIRouter, UploadFile, File, Form, Request
import cv2
import numpy as np
import mediapipe as mp
import face_recognition
from db import add_user

router = APIRouter()

# MediaPipe Face Detection (hybrid approach)
mp_face_detection = mp.solutions.face_detection.FaceDetection(
    model_selection=1,
    min_detection_confidence=0.6
)


@router.post("/enroll-face")
async def enroll_face(
    name: str = Form(...),
    file: UploadFile = File(...)
):
    # Read uploaded image
    image_bytes = await file.read()
    np_img = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "Invalid image"}

    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect face using MediaPipe
    detections = mp_face_detection.process(rgb).detections
    if not detections:
        return {"error": "No face detected"}

    # Get bounding box from first detection
    h, w, _ = frame.shape
    box = detections[0].location_data.relative_bounding_box

    x1 = int(box.xmin * w)
    y1 = int(box.ymin * h)
    x2 = int((box.xmin + box.width) * w)
    y2 = int((box.ymin + box.height) * h)

    # Crop face from RGB image
    face_img = rgb[y1:y2, x1:x2]

    # Extract 128-dim face encoding using face_recognition
    encodings = face_recognition.face_encodings(face_img)
    if not encodings:
        return {"error": "Face encoding failed"}

    # Save user with face_encoding (single 128-dim vector)
    user = {
        "name": name.lower(),
        "face_encoding": encodings[0].tolist()
    }

    add_user(user)

    return {
        "status": "success",
        "message": f"{name} enrolled successfully"
    }
