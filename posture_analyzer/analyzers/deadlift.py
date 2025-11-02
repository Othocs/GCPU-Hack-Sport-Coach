from typing import Dict, Any
from ..landmarks import PoseLandmark, get_landmark_3d, _landmarks_to_np
from ..angles import calculate_angle

def analyze_deadlift(landmarks) -> Dict[str, Any]:
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

    body_angle_left = calculate_angle(left_shoulder, left_hip, left_ankle)
    body_angle_right = calculate_angle(right_shoulder, right_hip, right_ankle)
    angles['body_left'] = body_angle_left; angles['body_right'] = body_angle_right

    if body_angle_left is not None and body_angle_right is not None:
        avg_body_angle = 0.5 * (body_angle_left + body_angle_right)
        if avg_body_angle < 160.0:
            mistakes.append({'issue': 'Rounded back (spinal flexion)','severity': 'severe','fix': 'Keep back straight and chest up, engage core'})

    if knee_angle_left is not None and knee_angle_right is not None:
        avg_knee_angle = 0.5 * (knee_angle_left + knee_angle_right)
        if avg_knee_angle < 140.0:
            mistakes.append({'issue': 'Too much knee bend (squatting the weight)','severity': 'moderate','fix': 'Start with less knee bend, focus on hip hinge'})

    if (knee_angle_left is not None and knee_angle_right is not None and
        hip_angle_left is not None and hip_angle_right is not None):
        if knee_angle_left > 175.0 and knee_angle_right > 175.0 and (hip_angle_left < 150.0 or hip_angle_right < 150.0):
            mistakes.append({'issue': 'Knees extending too early','severity': 'moderate','fix': 'Maintain knee position longer, extend hips and knees together'})

    severity = 'severe' if any(m['severity']=='severe' for m in mistakes) else ('moderate' if mistakes else 'good')
    return {'angles': angles, 'mistakes': mistakes, 'severity': severity}