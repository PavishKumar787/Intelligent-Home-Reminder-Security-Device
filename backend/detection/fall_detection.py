import mediapipe as mp
import time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

last_movement_time = time.time()

def detect_fall(frame):
    global last_movement_time
    rgb = frame[:, :, ::-1]
    result = pose.process(rgb)

    if not result.pose_landmarks:
        return False

    lm = result.pose_landmarks.landmark
    head_y = lm[0].y
    hip_y = lm[23].y

    last_movement_time = time.time()
    return head_y > hip_y

def no_movement(timeout=10):
    return time.time() - last_movement_time > timeout
