from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2
import time
from detection.motion_detection import detect_motion
from detection.state import current_detection, detection_tracking, UNKNOWN_THRESHOLD, NO_FACE_RESET_THRESHOLD
from db import get_user_by_name
from recognition.live_recognition import recognize_from_frame
from services.alert_store import alerts  # Import shared store for debug
from services.alert_service import clear_stranger_alerts, create_alert

# Debug: Print store ID to verify same instance
print(f"🔗 video.py loaded - ALERT STORE ID: {id(alerts)}")

router = APIRouter()

camera = None
last_motion_alert_time = 0
last_reminder_alert_time = 0

def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("ERROR: Could not open camera")
            return None
    return camera

def generate_frames():
    global camera
    print("Starting frame generation...")
    frame_count = 0
    
    while True:
        try:
            camera = get_camera()
            if camera is None:
                time.sleep(1)
                continue
                
            success, frame = camera.read()
            if not success:
                print("Failed to read frame, restarting camera...")
                if camera:
                    camera.release()
                    camera = None
                time.sleep(1)
                continue

            # Resize frame for faster processing and bandwidth
            frame = cv2.resize(frame, (640, 480))

            # 🔥 PRIORITY 1: Face Recognition (higher priority)
            try:
                name, confidence = recognize_from_frame(frame)
                current_time = time.time()
                
                # 🔥 HARD DEBUG - Log every frame
                if frame_count % 30 == 0:
                    print(f"🔥 Recognition loop running - Frame {frame_count}, Detected: {name}")
                
                if name and name != "Unknown":
                    # Known face detected
                    if not detection_tracking["known_user_present"]:
                        # Transition from unknown/none to known - DO NOT clear alerts, let them persist
                        print(f"✅ Known user detected: {name}")
                    detection_tracking["unknown_frames"] = 0
                    detection_tracking["no_face_frames"] = 0
                    detection_tracking["known_user_present"] = True
                    detection_tracking["last_stranger_alert"] = False
                    
                    current_detection["type"] = "face"
                    current_detection["name"] = name
                    current_detection["isKnown"] = True
                    current_detection["confidence"] = float(confidence) if confidence else None

                    try:
                        user = get_user_by_name(name)
                        if user and user.get("reminders"):
                            global last_reminder_alert_time
                            if time.time() - last_reminder_alert_time >= 30:
                                items = ", ".join(user["reminders"])
                                create_alert(
                                    "reminder",
                                    f"{name.capitalize()}, don't forget your {items}"
                                )
                                last_reminder_alert_time = time.time()
                    except Exception as reminder_error:
                        print(f"⚠️ Reminder alert error: {reminder_error}")
                    if frame_count % 30 == 0:
                        print(f"✓ Recognized: {name} (confidence: {confidence:.2f})" if confidence else f"✓ Recognized: {name}")
                elif name == "Unknown":
                    # Unknown face detected - increment counter, reset no-face counter
                    detection_tracking["unknown_frames"] += 1
                    detection_tracking["no_face_frames"] = 0
                    detection_tracking["known_user_present"] = False
                    
                    current_detection["type"] = "face"
                    current_detection["name"] = "Unknown"
                    current_detection["isKnown"] = False
                    current_detection["confidence"] = float(confidence) if confidence else None
                    
                    # Debug: Log counter every 10 frames
                    if detection_tracking["unknown_frames"] % 10 == 0:
                        print(f"🔍 Unknown frames: {detection_tracking['unknown_frames']}/{UNKNOWN_THRESHOLD}")
                    
                    # Create stranger alert only after threshold AND not already alerted
                    if (detection_tracking["unknown_frames"] >= UNKNOWN_THRESHOLD and 
                        not detection_tracking["last_stranger_alert"]):
                        print(f"🚨🚨 CREATING STRANGER ALERT - Threshold reached: {detection_tracking['unknown_frames']} 🚨🚨")
                        result = create_alert("security", "Stranger detected near entrance")
                        print(f"🚨 Alert created result: {result}")
                        detection_tracking["last_stranger_alert"] = True
                        print(f"⚠️ Stranger alert triggered after {UNKNOWN_THRESHOLD} frames")
                else:
                    # No face detected - increment no-face counter
                    detection_tracking["no_face_frames"] += 1
                    
                    # Reset unknown counter after prolonged no-face period
                    if detection_tracking["no_face_frames"] >= NO_FACE_RESET_THRESHOLD:
                        detection_tracking["unknown_frames"] = 0
                        detection_tracking["last_stranger_alert"] = False
                    
                    try:
                        motion_detected = detect_motion(frame)
                        if motion_detected:
                            global last_motion_alert_time
                            if time.time() - last_motion_alert_time >= 5:
                                create_alert("motion", "Motion detected in camera view")
                                last_motion_alert_time = time.time()
                        else:
                            # No motion either - clear detection state completely
                            current_detection["type"] = None
                            current_detection["name"] = None
                            current_detection["isKnown"] = False
                            current_detection["confidence"] = None
                    except Exception as me:
                        # On motion detection error, clear state
                        current_detection["type"] = None
                        current_detection["name"] = None
                        current_detection["isKnown"] = False
                        current_detection["confidence"] = None
            except Exception as e:
                print(f"Recognition error: {e}")
                # Clear detection state on error
                current_detection["type"] = None
                current_detection["name"] = None
                current_detection["isKnown"] = False
                current_detection["confidence"] = None

            ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                print("Failed to encode frame")
                continue
                
            frame_bytes = buffer.tobytes()
            frame_count += 1
            
            if frame_count % 30 == 0:
                print(f"Streaming frame {frame_count}, size: {len(frame_bytes)} bytes")

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n"
                + frame_bytes
                + b"\r\n"
            )
            
        except Exception as e:
            print(f"Frame generation error: {e}")
            time.sleep(1)
            continue

@router.get("/video-feed")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Connection": "keep-alive"}
    )
