from fastapi import APIRouter, UploadFile, File, Form
import cv2
import numpy as np
from mediapipe import solutions
from db import load_db, save_db
from recognition.mediapipe_embedding import extract_embedding

router = APIRouter()

# MediaPipe Face Mesh (for re-enrollment)
mp_face_mesh = solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    min_detection_confidence=0.6
)

@router.get("/users")
def get_users():
    users = load_db()
    return [u["name"] for u in users]


@router.post("/re-enroll-face")
async def re_enroll_face(
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

    # Detect face landmarks using MediaPipe
    result = face_mesh.process(rgb)
    if not result.multi_face_landmarks:
        return {"error": "No face detected"}

    # Extract normalized embedding
    new_embedding = extract_embedding(result.multi_face_landmarks[0])
    
    if new_embedding is None:
        return {"error": "Could not extract face encoding"}

    # Load DB and update user
    users = load_db()
    for user in users:
        if user["name"] == name.lower():
            user["face_encoding"] = new_embedding.tolist()
            save_db(users)
            return {"status": "Face updated successfully"}

    return {"error": "User not found"}


    # Load DB and update user
    users = load_db()
    for user in users:
        if user["name"] == name.lower():
            user["face_encoding"] = new_embedding
            save_db(users)
            return {"status": "Face updated successfully"}

    return {"error": "User not found"}
