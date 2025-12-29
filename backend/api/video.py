from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2
from detection.motion_detection import detect_motion
from detection.state import current_detection
from recognition.live_recognition import recognize_from_frame

router = APIRouter()

camera = cv2.VideoCapture(0)  # 0 = laptop camera

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        # 🔥 PRIORITY 1: Face Recognition (higher priority)
        name, confidence = recognize_from_frame(frame)
        
        if name:
            # Face detected
            current_detection["type"] = "face"
            current_detection["name"] = name
            current_detection["isKnown"] = name != "Unknown"
            current_detection["confidence"] = float(confidence) if confidence else None
        else:
            # PRIORITY 2: Motion Detection (fallback)
            detect_motion(frame)

        ret, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )

@router.get("/video-feed")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
