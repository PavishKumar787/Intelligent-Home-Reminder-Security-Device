# backend/detection/state.py
# Single source of truth for current detection state

current_detection = {
    "type": None,        # motion / face / fall
    "name": None,        # person name or "Unknown"
    "isKnown": False,    # true / false
    "confidence": None   # optional
}

# Tracking state for unknown user persistence
detection_tracking = {
    "unknown_frames": 0,           # Count of consecutive unknown frames
    "no_face_frames": 0,           # Count of frames with no face detected
    "known_user_present": False,   # Whether a known user was recently detected
    "last_stranger_alert": False   # Whether we already sent a stranger alert
}

# Threshold: ~0.5 second at 30 FPS so alerts trigger faster
UNKNOWN_THRESHOLD = 15
# Reset unknown counter if no face for ~2 seconds
NO_FACE_RESET_THRESHOLD = 60
