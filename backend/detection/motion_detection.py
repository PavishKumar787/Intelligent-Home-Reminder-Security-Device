import cv2
from detection.state import current_detection

prev_frame = None

def detect_motion(frame):
    global prev_frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if prev_frame is None:
        prev_frame = gray
        return False

    diff = cv2.absdiff(prev_frame, gray)
    prev_frame = gray

    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    motion_pixels = cv2.countNonZero(thresh)

    if motion_pixels > 5000:
        # 🔥 UPDATE SHARED STATE
        current_detection["type"] = "motion"
        current_detection["name"] = "Motion Detected"
        current_detection["isKnown"] = False
        return True

    return False
