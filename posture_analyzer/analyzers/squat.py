from typing import Dict, Any
from ..landmarks import PoseLandmark, get_landmark_3d, _landmarks_to_np, _is_valid, _safe_x
from ..angles import calculate_angle

def analyze_squat(landmarks) -> Dict[str, Any]:
    L = _landmarks_to_np(landmarks)

    left_shoulder = get_landmark_3d(L, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_landmark_3d(L, PoseLandmark.RIGHT_SHOULDER)
    left_hip = get_landmark_3d(L, PoseLandmark.LEFT_HIP)
    right_hip = get_landmark_3d(L, PoseLandmark.RIGHT_HIP)
    left_knee = get_landmark_3d(L, PoseLandmark.LEFT_KNEE)
    right_knee = get_landmark_3d(L, PoseLandmark.RIGHT_KNEE)
    left_ankle = get_landmark_3d(L, PoseLandmark.LEFT_ANKLE)
    right_ankle = get_landmark_3d(L, PoseLandmark.RIGHT_ANKLE)

    angles = {}; mistakes = []

    hip_angle_left = calculate_angle(left_shoulder, left_hip, left_knee)
    hip_angle_right = calculate_angle(right_shoulder, right_hip, right_knee)
    angles['hip_left'] = hip_angle_left; angles['hip_right'] = hip_angle_right

    knee_angle_left = calculate_angle(left_hip, left_knee, left_ankle)
    knee_angle_right = calculate_angle(right_hip, right_knee, right_ankle)
    angles['knee_left'] = knee_angle_left; angles['knee_right'] = knee_angle_right

    if knee_angle_left is not None and knee_angle_right is not None:
        lx = _safe_x(L, PoseLandmark.LEFT_KNEE); rx = _safe_x(L, PoseLandmark.RIGHT_KNEE)
        if lx is not None and rx is not None and lx < rx:
            mistakes.append({'issue': 'Knee Valgus (knees caving inward)','severity': 'severe','fix': 'Push knees out over toes, strengthen glutes'})

    if knee_angle_left is not None and knee_angle_right is not None:
        if knee_angle_left > 120.0 and knee_angle_right > 120.0:
            mistakes.append({'issue': 'Insufficient squat depth','severity': 'moderate','fix': 'Lower until thighs are parallel to floor'})

    if hip_angle_left is not None and hip_angle_right is not None:
        avg_hip_angle = 0.5 * (hip_angle_left + hip_angle_right)
        if avg_hip_angle > 160.0:
            mistakes.append({'issue': 'Excessive forward lean','severity': 'moderate','fix': 'Keep chest up and back straight'})

    left_heel = get_landmark_3d(L, PoseLandmark.LEFT_HEEL)
    right_heel = get_landmark_3d(L, PoseLandmark.RIGHT_HEEL)
    if _is_valid(left_heel) and _is_valid(right_heel) and _is_valid(left_ankle) and _is_valid(right_ankle):
        if left_heel[2] > left_ankle[2] + 0.01 or right_heel[2] > right_ankle[2] + 0.01:
            mistakes.append({'issue': 'Heels lifting off ground','severity': 'moderate','fix': 'Keep entire foot on ground, shift weight to heels'})

    severity = 'severe' if any(m['severity']=='severe' for m in mistakes) else ('moderate' if mistakes else 'good')
    return {'angles': angles, 'mistakes': mistakes, 'severity': severity}