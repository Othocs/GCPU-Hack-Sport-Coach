from typing import Dict, Any
from ..landmarks import PoseLandmark, get_landmark_3d, _landmarks_to_np, _is_valid
from ..angles import calculate_angle

def analyze_plank(landmarks) -> Dict[str, Any]:
    L = _landmarks_to_np(landmarks)

    left_shoulder = get_landmark_3d(L, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_landmark_3d(L, PoseLandmark.RIGHT_SHOULDER)
    left_hip = get_landmark_3d(L, PoseLandmark.LEFT_HIP)
    right_hip = get_landmark_3d(L, PoseLandmark.RIGHT_HIP)
    left_ankle = get_landmark_3d(L, PoseLandmark.LEFT_ANKLE)
    right_ankle = get_landmark_3d(L, PoseLandmark.RIGHT_ANKLE)

    angles = {}; mistakes = []

    body_angle_left = calculate_angle(left_shoulder, left_hip, left_ankle)
    body_angle_right = calculate_angle(right_shoulder, right_hip, right_ankle)
    angles['body_alignment_left'] = body_angle_left; angles['body_alignment_right'] = body_angle_right

    if body_angle_left is not None and body_angle_right is not None:
        avg_angle = 0.5 * (body_angle_left + body_angle_right)
        if avg_angle < 175.0:
            mistakes.append({'issue': 'Hips sagging / arched back','severity': 'moderate','fix': 'Engage core, squeeze glutes, maintain straight line'})

    if _is_valid(left_hip) and _is_valid(left_shoulder) and _is_valid(left_ankle):
        hip_height = float(left_hip[1]); shoulder_height = float(left_shoulder[1])
        if hip_height < shoulder_height - 0.05:
            mistakes.append({'issue': 'Buttocks raised too high','severity': 'moderate','fix': 'Lower hips to shoulder level, maintain straight line'})

    severity = 'severe' if any(m['severity']=='severe' for m in mistakes) else ('moderate' if mistakes else 'good')
    return {'angles': angles, 'mistakes': mistakes, 'severity': severity}