import time
import numpy as np

from camera import get_frame
from detection.motion_detection import detect_motion
from detection.fall_detection import detect_fall, no_movement
from detection.state import (
    current_detection,
    detection_tracking,
    UNKNOWN_THRESHOLD,
    NO_FACE_RESET_THRESHOLD,
)
from services.alert_store import alerts  # Import shared store for debug
from services.alert_service import create_alert, clear_stranger_alerts
from recognition.face_recognition import identify_person
from db import get_user_by_name

# Debug: Print store ID to verify same instance
print(f"🔗 processor.py loaded - ALERT STORE ID: {id(alerts)}")


# ---------------- ALERT COOLDOWNS ---------------- #
COOLDOWNS = {
    "MOTION": 5,
    "REMINDER": 30,
    "EMERGENCY": 10,
    "WARNING": 15,
    "SECURITY": 10
}

KNOWN_PERSISTENCE_SECONDS = 12

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
    last_known_identity = {"name": None, "timestamp": 0.0, "ghost_active": False}

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
            ghost_known = False

            # ---------------- NO FACE ---------------- #
            if person is None:
                if (
                    last_known_identity["name"]
                    and (now - last_known_identity["timestamp"] <= KNOWN_PERSISTENCE_SECONDS)
                ):
                    person = last_known_identity["name"]
                    ghost_known = True
                    if not last_known_identity["ghost_active"]:
                        print(
                            f"👤 Processor: Continuing with last known identity {person} despite low visibility."
                        )
                    last_known_identity["ghost_active"] = True
                else:
                    current_detection["type"] = None
                    current_detection["name"] = None
                    current_detection["isKnown"] = False
                    detection_tracking["no_face_frames"] += 1
                    detection_tracking["known_user_present"] = False
                    if detection_tracking["no_face_frames"] >= NO_FACE_RESET_THRESHOLD:
                        if detection_tracking["last_stranger_alert"]:
                            print(
                                "🚪 Processor: Face lost long enough; resetting stranger alert flag."
                            )
                        detection_tracking["unknown_frames"] = 0
                        detection_tracking["last_stranger_alert"] = False
                        detection_tracking["no_face_frames"] = 0
                    last_known_identity["name"] = None
                    last_known_identity["timestamp"] = 0.0
                    last_known_identity["ghost_active"] = False
                    # Don't reset unknown_frames immediately - allow for brief detection gaps
                    time.sleep(0.5)
                    continue

            # ---------------- STRANGER ---------------- #
            if person == "STRANGER":
                # 🔥 UPDATE DETECTION STATE
                current_detection["type"] = "face"
                current_detection["name"] = "Unknown"
                current_detection["isKnown"] = False
                
                # Increment unknown frames counter on EVERY loop iteration (not just recognition)
                detection_tracking["unknown_frames"] += 1
                detection_tracking["no_face_frames"] = 0
                detection_tracking["known_user_present"] = False
                last_known_identity["name"] = None
                last_known_identity["timestamp"] = 0.0
                last_known_identity["ghost_active"] = False
                
                # Debug: Log every 5 increments
                if detection_tracking["unknown_frames"] % 5 == 0:
                    print(f"🔍 Processor: Unknown frames = {detection_tracking['unknown_frames']}/{UNKNOWN_THRESHOLD}")
                
                # Only create alert after threshold and not already alerted
                if detection_tracking["unknown_frames"] >= UNKNOWN_THRESHOLD:
                    if detection_tracking["last_stranger_alert"]:
                        if detection_tracking["unknown_frames"] == UNKNOWN_THRESHOLD:
                            print(
                                "🚫 Processor: Stranger alert suppressed (flag still True from previous sighting)."
                            )
                    else:
                        print(
                            f"🚨 Processor: Stranger threshold reached ({detection_tracking['unknown_frames']} frames)"
                        )
                        create_alert(
                            "security",
                            "Stranger detected near entrance"
                        )
                        detection_tracking["last_stranger_alert"] = True
                time.sleep(0.1)  # Faster loop for quicker detection
                continue

            # ---------------- KNOWN USER ---------------- #
            # Transition to known user - DO NOT clear alerts, let them persist
            if not detection_tracking["known_user_present"]:
                print(f"✅ Processor: Known user detected: {person}")
            detection_tracking["unknown_frames"] = 0
            detection_tracking["known_user_present"] = True
            detection_tracking["last_stranger_alert"] = False
            detection_tracking["no_face_frames"] = 0
            
            # 🔥 UPDATE DETECTION STATE
            current_detection["type"] = "face"
            current_detection["name"] = person
            current_detection["isKnown"] = True
            last_known_identity["name"] = person
            if not ghost_known:
                last_known_identity["timestamp"] = time.time()
                last_known_identity["ghost_active"] = False
            
            user = get_user_by_name(person)

            if detect_motion(frame) and can_trigger("MOTION"):
                create_alert(
                    "motion",
                    f"Movement detected by {person}"
                )

            fall_now = detect_fall(frame)
            if fall_now and can_trigger("EMERGENCY"):
                create_alert(
                    "emergency",
                    f"🚨 {person} may have fallen"
                )

            if no_movement() and can_trigger("WARNING"):
                create_alert(
                    "security",
                    f"⚠️ No movement detected for {person}"
                )

            # ---------------- REMINDERS ---------------- #
            if user and user.get("reminders") and can_trigger("REMINDER"):
                items = ", ".join(user["reminders"])
                create_alert(
                    "reminder",
                    f"{person.capitalize()}, don't forget your {items}"
                )

            time.sleep(0.5)

        except Exception as e:
            print("❌ AI Processor error:", e)
            time.sleep(1)
