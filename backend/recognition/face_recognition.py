import cv2
import numpy as np
from mediapipe import solutions
from db import get_all_users

# MediaPipe setup
mp_face_detection = solutions.face_detection
mp_face_mesh = solutions.face_mesh

face_detector = mp_face_detection.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.6
)

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

THRESHOLD = 0.15  # Euclidean distance threshold


def extract_embedding(landmarks):
    """
    Convert MediaPipe face landmarks into a numeric embedding
    """
    embedding = []
    for lm in landmarks.landmark:
        embedding.extend([lm.x, lm.y, lm.z])
    return np.array(embedding, dtype=np.float32)


def identify_person(frame):
    if frame is None:
        return None

    # Ensure uint8
    frame = np.array(frame, dtype=np.uint8, copy=True)

    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 🔍 Detect face
    detection = face_detector.process(rgb)
    if not detection.detections:
        return None

    # 🧠 Get face landmarks
    mesh_result = face_mesh.process(rgb)
    if not mesh_result.multi_face_landmarks:
        return None

    current_embedding = extract_embedding(
        mesh_result.multi_face_landmarks[0]
    )

    # 🔁 Compare with database
    users = get_all_users()
    for user in users:
        if not user:
            continue

        embeddings = []
        if user.get("face_encodings"):
            embeddings.extend(user["face_encodings"])
        elif user.get("face_encoding"):
            embeddings.append(user["face_encoding"])

        for saved in embeddings:
            saved_embedding = np.array(saved, dtype=np.float32)

            if saved_embedding.shape != current_embedding.shape:
                continue

            distance = np.linalg.norm(saved_embedding - current_embedding)

            if distance < THRESHOLD:
                return user["name"]

    return "STRANGER"
