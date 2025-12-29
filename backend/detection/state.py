# backend/detection/state.py
# Single source of truth for current detection state

current_detection = {
    "type": None,        # motion / face / fall
    "name": None,        # person name or "Unknown"
    "isKnown": False,    # true / false
    "confidence": None   # optional
}
