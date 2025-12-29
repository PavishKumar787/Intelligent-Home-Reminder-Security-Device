import time
import numpy as np

from camera import get_frame
from detection.motion_detection import detect_motion
from detection.fall_detection import detect_fall, no_movement
from detection.state import current_detection
from services.alert_service import create_alert
from recognition.face_recognition import identify_person
from db import get_user_by_name


# ---------------- ALERT COOLDOWNS ---------------- #
COOLDOWNS = {
    "MOTION": 5,
    "REMINDER": 30,
    "EMERGENCY": 10,
    "WARNING": 15,
    "SECURITY": 10
}

last_alert_time = {}


def can_trigger(alert_type):
    now = time.time()
    last_time = last_alert_time.get(alert_type, 0)
    if now - last_time >= COOLDOWNS[alert_type]:
        last_alert_time[alert_type] = now
        return True
    return False


# ---------------- AI PROCESSOR ---------------- #
def start_processing():
    print("🧠 AI Processor started")

    last_face_check = 0
    cached_person = None
    FACE_INTERVAL = 5  # seconds

    while True:
        try:
            # ---------------- GET FRAME ---------------- #
            frame = get_frame()
            if frame is None:
                time.sleep(0.2)
                continue

            # ---------------- HARD FRAME VALIDATION ---------------- #
            if (
                not isinstance(frame, np.ndarray)
                or frame.dtype != np.uint8
                or len(frame.shape) != 3
                or frame.shape[2] != 3
            ):
                print(
                    "⚠️ Invalid frame skipped:",
                    type(frame),
                    getattr(frame, "dtype", None),
                    getattr(frame, "shape", None)
                )
                time.sleep(0.5)
                continue

            now = time.time()

            # ---------------- FACE RECOGNITION (RATE LIMITED) ---------------- #
            if now - last_face_check >= FACE_INTERVAL:
                cached_person = identify_person(frame)
                last_face_check = now

            person = cached_person

            # ---------------- NO FACE ---------------- #
            if person is None:
                current_detection["type"] = None
                current_detection["name"] = None
                current_detection["isKnown"] = False
                time.sleep(0.5)
                continue

            # ---------------- STRANGER ---------------- #
            if person == "STRANGER":
                # 🔥 UPDATE DETECTION STATE
                current_detection["type"] = "face"
                current_detection["name"] = "Unknown"
                current_detection["isKnown"] = False
                
                if can_trigger("SECURITY"):
                    create_alert(
                        "SECURITY",
                        "⚠️ Stranger detected near entrance"
                    )
                time.sleep(1)
                continue

            # ---------------- KNOWN USER ---------------- #
            # 🔥 UPDATE DETECTION STATE
            current_detection["type"] = "face"
            current_detection["name"] = person
            current_detection["isKnown"] = True
            
            user = get_user_by_name(person)

            if detect_motion(frame) and can_trigger("MOTION"):
                create_alert(
                    "MOTION",
                    f"Movement detected by {person}"
                )

            if detect_fall(frame) and can_trigger("EMERGENCY"):
                create_alert(
                    "EMERGENCY",
                    f"🚨 {person} may have fallen"
                )

            if no_movement() and can_trigger("WARNING"):
                create_alert(
                    "WARNING",
                    f"⚠️ No movement detected for {person}"
                )

            # ---------------- REMINDERS ---------------- #
            if user and user.get("reminders") and can_trigger("REMINDER"):
                items = ", ".join(user["reminders"])
                create_alert(
                    "REMINDER",
                    f"{person}, don’t forget your {items}"
                )

            time.sleep(0.5)

        except Exception as e:
            print("❌ AI Processor error:", e)
            time.sleep(1)
