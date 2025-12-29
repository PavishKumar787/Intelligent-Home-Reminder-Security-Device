import numpy as np

def extract_embedding(landmarks):
    """
    Extract normalized embedding from MediaPipe face landmarks
    
    468 landmarks × 3 coordinates (x, y, z) = 1404 dimensions
    Then normalized using L2 norm
    """
    embedding = []
    for lm in landmarks.landmark:
        embedding.extend([lm.x, lm.y, lm.z])

    embedding = np.array(embedding, dtype=np.float32)

    # 🔥 Normalize (CRITICAL for cosine similarity)
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return None
    return embedding / norm
