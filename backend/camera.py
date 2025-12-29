import cv2
import numpy as np

cap = cv2.VideoCapture(0)

def get_frame():
    if not cap.isOpened():
        return None

    ret, frame = cap.read()
    if not ret or frame is None:
        return None

    # 🔒 Force uint8
    if frame.dtype != np.uint8:
        frame = np.clip(frame, 0, 255).astype(np.uint8)

    # 🔒 Force 3 channels
    if len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    elif frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    return frame
