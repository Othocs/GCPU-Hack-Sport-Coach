from typing import Dict
from ..landmarks import PoseLandmark, get_landmark_3d, _landmarks_to_np, _safe_x
from ..angles import calculate_angle

def analyze_lunge(landmarks) -> Dict[str, any]:
    L = _landmarks_to_np(landmarks)

    left_shoulder = get_landmark_3d(L, PoseLandmark.LEFT_SHOULDER)
    left_hip = get_landmark_3d(L, PoseLandmark.LEFT_HIP)
    left_knee = get_landmark_3d(L, PoseLandmark.LEFT_KNEE)
    left_ankle = get_landmark_3d(L, PoseLandmark.LEFT_ANKLE)
    right_hip = get_landmark_3d(L, PoseLandmark.RIGHT_HIP)
    right_knee = get_landmark_3d(L, PoseLandmark.RIGHT_KNEE)
    right_ankle = get_landmark_3d(L, PoseLandmark.RIGHT_ANKLE)

    angles = {}; mistakes = []

    knee_angle_left = calculate_angle(left_hip, left_knee, left_ankle)
    knee_angle_right = calculate_angle(right_hip, right_knee, right_ankle)
    angles['knee_left'] = knee_angle_left; angles['knee_right'] = knee_angle_right

    body_angle = calculate_angle(left_shoulder, left_hip, left_ankle)
    angles['body_alignment'] = body_angle

    lkx = _safe_x(L, PoseLandmark.LEFT_KNEE)
    lax = _safe_x(L, PoseLandmark.LEFT_ANKLE)
    if lkx is not None and lax is not None and abs(lkx - lax) > 0.05:
        mistakes.append({'issue': 'Front knee over toes','severity': 'moderate','fix': 'Keep front knee aligned over ankle'})

    if knee_angle_left is not None and knee_angle_right is not None:
        if knee_angle_left > 120.0 or knee_angle_right > 120.0:
            mistakes.append({'issue': 'Insufficient lunge depth','severity': 'minor','fix': 'Lower until front thigh is parallel to floor'})

    severity = 'severe' if any(m['severity']=='severe' for m in mistakes) else ('moderate' if mistakes else 'good')
    return {'angles': angles, 'mistakes': mistakes, 'severity': severity}