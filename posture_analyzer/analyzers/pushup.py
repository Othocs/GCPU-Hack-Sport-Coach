from typing import Dict
from ..landmarks import PoseLandmark, get_landmark_3d, _landmarks_to_np, _is_valid
from ..angles import calculate_angle

def analyze_pushup(landmarks) -> Dict[str, any]:
    L = _landmarks_to_np(landmarks)

    left_shoulder = get_landmark_3d(L, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_landmark_3d(L, PoseLandmark.RIGHT_SHOULDER)
    left_elbow = get_landmark_3d(L, PoseLandmark.LEFT_ELBOW)
    right_elbow = get_landmark_3d(L, PoseLandmark.RIGHT_ELBOW)
    left_wrist = get_landmark_3d(L, PoseLandmark.LEFT_WRIST)
    right_wrist = get_landmark_3d(L, PoseLandmark.RIGHT_WRIST)
    left_hip = get_landmark_3d(L, PoseLandmark.LEFT_HIP)
    right_hip = get_landmark_3d(L, PoseLandmark.RIGHT_HIP)
    left_ankle = get_landmark_3d(L, PoseLandmark.LEFT_ANKLE)
    right_ankle = get_landmark_3d(L, PoseLandmark.RIGHT_ANKLE)

    angles = {}; mistakes = []

    elbow_angle_left = calculate_angle(left_shoulder, left_elbow, left_wrist)
    elbow_angle_right = calculate_angle(right_shoulder, right_elbow, right_wrist)
    angles['elbow_left'] = elbow_angle_left; angles['elbow_right'] = elbow_angle_right

    body_angle_left = calculate_angle(left_shoulder, left_hip, left_ankle)
    body_angle_right = calculate_angle(right_shoulder, right_hip, right_ankle)
    angles['body_alignment_left'] = body_angle_left; angles['body_alignment_right'] = body_angle_right

    if body_angle_left is not None and body_angle_right is not None:
        avg_body_angle = 0.5 * (body_angle_left + body_angle_right)
        if avg_body_angle < 175.0:
            mistakes.append({'issue': 'Sagging hips / arched back','severity': 'moderate','fix': 'Engage core and glutes to maintain straight line'})

    if _is_valid(left_hip) and _is_valid(left_shoulder) and _is_valid(left_ankle):
        hip_height = float(left_hip[1]); shoulder_height = float(left_shoulder[1])
        if hip_height < shoulder_height - 0.05:
            mistakes.append({'issue': 'Raised buttocks','severity': 'moderate','fix': 'Lower hips to maintain straight line'})

    if elbow_angle_left is not None and elbow_angle_right is not None:
        avg_elbow_angle = 0.5 * (elbow_angle_left + elbow_angle_right)
        if avg_elbow_angle < 45.0:
            mistakes.append({'issue': 'Elbows tucked too close to body','severity': 'minor','fix': 'Keep elbows at ~45 degrees from body'})
        elif avg_elbow_angle > 90.0:
            mistakes.append({'issue': 'Elbows flaring outward','severity': 'moderate','fix': 'Keep elbows at ~45 degrees from body'})

    if elbow_angle_left is not None and elbow_angle_right is not None:
        if min(elbow_angle_left, elbow_angle_right) > 90.0:
            mistakes.append({'issue': 'Incomplete range of motion','severity': 'minor','fix': 'Lower chest closer to ground'})

    severity = 'severe' if any(m['severity']=='severe' for m in mistakes) else ('moderate' if mistakes else 'good')
    return {'angles': angles, 'mistakes': mistakes, 'severity': severity}