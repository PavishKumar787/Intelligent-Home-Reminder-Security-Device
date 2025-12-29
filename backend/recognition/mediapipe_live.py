import cv2
import numpy as np
from mediapipe import solutions
from recognition.face_db import load_known_faces
from recognition.mediapipe_embedding import extract_embedding

# Initialize MediaPipe Face Mesh
mp_face_mesh = solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Load known faces at startup
known_names, known_embeddings = load_known_faces()

# Stricter threshold for MediaPipe embeddings
SIMILARITY_THRESHOLD = 0.97

def recognize_face(frame):
    """
    Recognize a face in the frame using normalized embeddings and cosine similarity
    
    Returns: (name, confidence_score)
    - name: person's name or "Unknown"
    - confidence_score: similarity score (0-1)
    """
    if frame is None or len(known_embeddings) == 0:
        return None, None

    try:
        # Convert BGR to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect landmarks
        result = face_mesh.process(rgb)
        
        if not result.multi_face_landmarks:
            return None, None

        # Extract normalized embedding
        embedding = extract_embedding(result.multi_face_landmarks[0])
        
        if embedding is None:
            return None, None

        # Compute cosine similarity with all known embeddings
        similarities = [
            np.dot(embedding, known_emb)
            for known_emb in known_embeddings
        ]

        best_score = max(similarities)
        best_idx = np.argmax(similarities)

        print(f"Similarity: {best_score:.4f}")

        # Stricter threshold (0.97 for MediaPipe)
        if best_score > SIMILARITY_THRESHOLD:
            return known_names[best_idx], best_score

        return "Unknown", best_score

    except Exception as e:
        print(f"Face recognition error: {e}")
        return None, None
