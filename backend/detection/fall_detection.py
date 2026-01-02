import math
import time
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

ANGLE_THRESHOLD_DEGREES = 30
SITTING_ANGLE_THRESHOLD_DEGREES = 55
HEAD_DROP_OFFSET = 0.05
WRIST_HEAD_OFFSET = 0.04
HEAD_DROP_VELOCITY = 0.06
MOVEMENT_THRESHOLD = 0.015

fall_detected = False
fall_start_time = None
last_movement_time = None
_previous_centers = None
_previous_head_level = None


def _compute_centers(landmarks):
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]

    shoulder_center = (
        (left_shoulder.x + right_shoulder.x) * 0.5,
        (left_shoulder.y + right_shoulder.y) * 0.5,
    )
    hip_center = (
        (left_hip.x + right_hip.x) * 0.5,
        (left_hip.y + right_hip.y) * 0.5,
    )

    return shoulder_center, hip_center


def _torso_angle_degrees(shoulder_center, hip_center):
    dx = hip_center[0] - shoulder_center[0]
    dy = hip_center[1] - shoulder_center[1]

    angle = abs(math.degrees(math.atan2(dy, dx)))
    if angle > 90:
        angle = 180 - angle
    return angle


def _register_movement(shoulder_center, hip_center):
    global last_movement_time
    if _previous_centers is None:
        return

    shoulder_prev = _previous_centers[0]
    hip_prev = _previous_centers[1]

    shoulder_delta = math.hypot(
        shoulder_center[0] - shoulder_prev[0],
        shoulder_center[1] - shoulder_prev[1],
    )
    hip_delta = math.hypot(
        hip_center[0] - hip_prev[0],
        hip_center[1] - hip_prev[1],
    )

    if fall_detected and max(shoulder_delta, hip_delta) > MOVEMENT_THRESHOLD:
        last_movement_time = time.time()


def detect_fall(frame):
    global fall_detected, fall_start_time, last_movement_time, _previous_centers, _previous_head_level

    rgb = frame[:, :, ::-1]
    result = pose.process(rgb)

    if not result.pose_landmarks:
        _previous_centers = None
        _previous_head_level = None
        return fall_detected

    landmarks = result.pose_landmarks.landmark
    shoulder_center, hip_center = _compute_centers(landmarks)
    angle = _torso_angle_degrees(shoulder_center, hip_center)
    head_y = landmarks[0].y
    hip_y = (landmarks[23].y + landmarks[24].y) * 0.5
    head_below_hip = head_y - hip_y > HEAD_DROP_OFFSET

    left_wrist_y = landmarks[15].y
    right_wrist_y = landmarks[16].y
    wrists_near_head = (
        abs(left_wrist_y - head_y) < WRIST_HEAD_OFFSET
        or abs(right_wrist_y - head_y) < WRIST_HEAD_OFFSET
    )

    transient_head_drop = False
    if _previous_head_level is not None:
        head_velocity = head_y - _previous_head_level
        transient_head_drop = head_velocity > HEAD_DROP_VELOCITY
    _previous_head_level = head_y

    _register_movement(shoulder_center, hip_center)
    _previous_centers = (shoulder_center, hip_center)

    is_fallen_posture = angle < ANGLE_THRESHOLD_DEGREES
    is_faint_posture = (
        not is_fallen_posture
        and angle < SITTING_ANGLE_THRESHOLD_DEGREES
        and head_below_hip
        and not wrists_near_head
    )
    posture_triggered = is_fallen_posture or is_faint_posture or transient_head_drop

    if posture_triggered and not fall_detected:
        fall_detected = True
        fall_start_time = time.time()
        last_movement_time = fall_start_time
        if is_fallen_posture:
            print("[fall_detection] Fall posture detected; monitoring movement.")
        elif is_faint_posture:
            print("[fall_detection] Possible faint posture detected; monitoring movement.")
        else:
            print("[fall_detection] Rapid head drop detected; monitoring movement.")
    elif not posture_triggered and fall_detected:
        fall_detected = False
        fall_start_time = None
        last_movement_time = None
        print("[fall_detection] Posture recovered; reset fall state.")

    return fall_detected


def no_movement(timeout=10):
    if not fall_detected or last_movement_time is None:
        return False
    return time.time() - last_movement_time > timeout
