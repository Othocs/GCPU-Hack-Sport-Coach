"""
Posture Analyzer for Gym Exercises
Functions to compute angles and detect posture mistakes from skeleton positions
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import mediapipe as mp

# MediaPipe Pose Landmark Indices
class PoseLandmark:
    """MediaPipe Pose landmark indices"""
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


def get_landmark_3d(landmarks, idx: int) -> np.ndarray:
    """Extract 3D coordinates of a landmark"""
    if not landmarks or idx >= len(landmarks):
        return None
    return np.array([landmarks[idx].x, landmarks[idx].y, landmarks[idx].z])


def calculate_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """
    Calculate the angle between three points (angle at p2)
    
    Args:
        p1: First point
        p2: Vertex point (angle is measured here)
        p3: Third point
    
    Returns:
        Angle in degrees
    """
    if p1 is None or p2 is None or p3 is None:
        return None
    
    # Convert to numpy arrays if not already
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)
    
    # Calculate vectors
    v1 = p1 - p2
    v2 = p3 - p2
    
    # Calculate angle using dot product
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Avoid numerical errors
    angle = np.arccos(cos_angle)
    
    return np.degrees(angle)


def calculate_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calculate Euclidean distance between two points"""
    if p1 is None or p2 is None:
        return None
    return np.linalg.norm(np.array(p1) - np.array(p2))


def analyze_squat(landmarks) -> Dict[str, any]:
    """
    Analyze squat posture and detect mistakes
    
    Returns dict with:
    - angles: joint angles
    - mistakes: list of detected issues
    - severity: overall severity level
    """
    results = {
        'angles': {},
        'mistakes': [],
        'severity': 'good'
    }
    
    # Get key landmarks
    left_hip = get_landmark_3d(landmarks, PoseLandmark.LEFT_HIP)
    right_hip = get_landmark_3d(landmarks, PoseLandmark.RIGHT_HIP)
    left_knee = get_landmark_3d(landmarks, PoseLandmark.LEFT_KNEE)
    right_knee = get_landmark_3d(landmarks, PoseLandmark.RIGHT_KNEE)
    left_ankle = get_landmark_3d(landmarks, PoseLandmark.LEFT_ANKLE)
    right_ankle = get_landmark_3d(landmarks, PoseLandmark.RIGHT_ANKLE)
    left_shoulder = get_landmark_3d(landmarks, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_landmark_3d(landmarks, PoseLandmark.RIGHT_SHOULDER)
    
    # Calculate angles
    # Hip angle
    hip_angle_left = calculate_angle(left_shoulder, left_hip, left_knee)
    hip_angle_right = calculate_angle(right_shoulder, right_hip, right_knee)
    results['angles']['hip_left'] = hip_angle_left
    results['angles']['hip_right'] = hip_angle_right
    
    # Knee angle
    knee_angle_left = calculate_angle(left_hip, left_knee, left_ankle)
    knee_angle_right = calculate_angle(right_hip, right_knee, right_ankle)
    results['angles']['knee_left'] = knee_angle_left
    results['angles']['knee_right'] = knee_angle_right
    
    # Detect mistakes
    # 1. Knee valgus (caving in)
    if knee_angle_left and knee_angle_right:
        # Check if knees are caving inward
        if left_knee[0] < right_knee[0]:  # Crossed position
            results['mistakes'].append({
                'issue': 'Knee Valgus (knees caving inward)',
                'severity': 'severe',
                'fix': 'Push knees out over toes, strengthen glutes'
            })
    
    # 2. Insufficient depth
    if knee_angle_left and knee_angle_right:
        if knee_angle_left > 120 and knee_angle_right > 120:
            results['mistakes'].append({
                'issue': 'Insufficient squat depth',
                'severity': 'moderate',
                'fix': 'Lower until thighs are parallel to floor'
            })
    
    # 3. Excessive forward lean
    if hip_angle_left and hip_angle_right:
        avg_hip_angle = (hip_angle_left + hip_angle_right) / 2
        if avg_hip_angle > 160:
            results['mistakes'].append({
                'issue': 'Excessive forward lean',
                'severity': 'moderate',
                'fix': 'Keep chest up and back straight'
            })
    
    # 4. Heel lift
    left_heel = get_landmark_3d(landmarks, PoseLandmark.LEFT_HEEL)
    right_heel = get_landmark_3d(landmarks, PoseLandmark.RIGHT_HEEL)
    if left_heel and right_heel and left_ankle and right_ankle:
        if left_heel[2] > left_ankle[2] + 0.01 or right_heel[2] > right_ankle[2] + 0.01:
            results['mistakes'].append({
                'issue': 'Heels lifting off ground',
                'severity': 'moderate',
                'fix': 'Keep entire foot on ground, shift weight to heels'
            })
    
    # Determine overall severity
    if any(m['severity'] == 'severe' for m in results['mistakes']):
        results['severity'] = 'severe'
    elif results['mistakes']:
        results['severity'] = 'moderate'
    
    return results


def analyze_pushup(landmarks) -> Dict[str, any]:
    """
    Analyze push-up posture and detect mistakes
    """
    results = {
        'angles': {},
        'mistakes': [],
        'severity': 'good'
    }
    
    # Get key landmarks
    left_shoulder = get_landmark_3d(landmarks, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_landmark_3d(landmarks, PoseLandmark.RIGHT_SHOULDER)
    left_elbow = get_landmark_3d(landmarks, PoseLandmark.LEFT_ELBOW)
    right_elbow = get_landmark_3d(landmarks, PoseLandmark.RIGHT_ELBOW)
    left_wrist = get_landmark_3d(landmarks, PoseLandmark.LEFT_WRIST)
    right_wrist = get_landmark_3d(landmarks, PoseLandmark.RIGHT_WRIST)
    left_hip = get_landmark_3d(landmarks, PoseLandmark.LEFT_HIP)
    right_hip = get_landmark_3d(landmarks, PoseLandmark.RIGHT_HIP)
    left_ankle = get_landmark_3d(landmarks, PoseLandmark.LEFT_ANKLE)
    right_ankle = get_landmark_3d(landmarks, PoseLandmark.RIGHT_ANKLE)
    
    # Calculate angles
    # Elbow angle
    elbow_angle_left = calculate_angle(left_shoulder, left_elbow, left_wrist)
    elbow_angle_right = calculate_angle(right_shoulder, right_elbow, right_wrist)
    results['angles']['elbow_left'] = elbow_angle_left
    results['angles']['elbow_right'] = elbow_angle_right
    
    # Body alignment (shoulder-hip-ankle)
    body_angle_left = calculate_angle(left_shoulder, left_hip, left_ankle)
    body_angle_right = calculate_angle(right_shoulder, right_hip, right_ankle)
    results['angles']['body_alignment_left'] = body_angle_left
    results['angles']['body_alignment_right'] = body_angle_right
    
    # Detect mistakes
    # 1. Sagging hips
    if body_angle_left and body_angle_right:
        avg_body_angle = (body_angle_left + body_angle_right) / 2
        if avg_body_angle < 175:  # Should be close to 180
            results['mistakes'].append({
                'issue': 'Sagging hips / arched back',
                'severity': 'moderate',
                'fix': 'Engage core and glutes to maintain straight line'
            })
    
    # 2. Raised buttocks
    if left_hip and left_shoulder and left_ankle:
        hip_height = left_hip[1]
        shoulder_height = left_shoulder[1]
        ankle_height = left_ankle[1]
        if hip_height < shoulder_height - 0.05:  # Hip too high
            results['mistakes'].append({
                'issue': 'Raised buttocks',
                'severity': 'moderate',
                'fix': 'Lower hips to maintain straight line'
            })
    
    # 3. Elbows flaring out
    if elbow_angle_left and elbow_angle_right:
        avg_elbow_angle = (elbow_angle_left + elbow_angle_right) / 2
        if avg_elbow_angle < 45:  # Elbows too close to body
            results['mistakes'].append({
                'issue': 'Elbows tucked too close to body',
                'severity': 'minor',
                'fix': 'Keep elbows at ~45 degrees from body'
            })
        elif avg_elbow_angle > 90:  # Elbows flaring
            results['mistakes'].append({
                'issue': 'Elbows flaring outward',
                'severity': 'moderate',
                'fix': 'Keep elbows at ~45 degrees from body'
            })
    
    # 4. Incomplete range of motion
    if elbow_angle_left and elbow_angle_right:
        min_elbow_angle = min(elbow_angle_left, elbow_angle_right)
        if min_elbow_angle > 90:
            results['mistakes'].append({
                'issue': 'Incomplete range of motion',
                'severity': 'minor',
                'fix': 'Lower chest closer to ground'
            })
    
    # Determine overall severity
    if any(m['severity'] == 'severe' for m in results['mistakes']):
        results['severity'] = 'severe'
    elif results['mistakes']:
        results['severity'] = 'moderate'
    
    return results


def analyze_deadlift(landmarks) -> Dict[str, any]:
    """
    Analyze deadlift posture and detect mistakes
    """
    results = {
        'angles': {},
        'mistakes': [],
        'severity': 'good'
    }
    
    # Get key landmarks
    left_shoulder = get_landmark_3d(landmarks, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_landmark_3d(landmarks, PoseLandmark.RIGHT_SHOULDER)
    left_hip = get_landmark_3d(landmarks, PoseLandmark.LEFT_HIP)
    right_hip = get_landmark_3d(landmarks, PoseLandmark.RIGHT_HIP)
    left_knee = get_landmark_3d(landmarks, PoseLandmark.LEFT_KNEE)
    right_knee = get_landmark_3d(landmarks, PoseLandmark.RIGHT_KNEE)
    left_ankle = get_landmark_3d(landmarks, PoseLandmark.LEFT_ANKLE)
    right_ankle = get_landmark_3d(landmarks, PoseLandmark.RIGHT_ANKLE)
    
    # Calculate angles
    # Hip angle
    hip_angle_left = calculate_angle(left_shoulder, left_hip, left_knee)
    hip_angle_right = calculate_angle(right_shoulder, right_hip, right_knee)
    results['angles']['hip_left'] = hip_angle_left
    results['angles']['hip_right'] = hip_angle_right
    
    # Knee angle
    knee_angle_left = calculate_angle(left_hip, left_knee, left_ankle)
    knee_angle_right = calculate_angle(right_hip, right_knee, right_ankle)
    results['angles']['knee_left'] = knee_angle_left
    results['angles']['knee_right'] = knee_angle_right
    
    # Body angle (shoulder-hip-ankle)
    body_angle_left = calculate_angle(left_shoulder, left_hip, left_ankle)
    body_angle_right = calculate_angle(right_shoulder, right_hip, right_ankle)
    results['angles']['body_left'] = body_angle_left
    results['angles']['body_right'] = body_angle_right
    
    # Detect mistakes
    # 1. Rounded back
    if body_angle_left and body_angle_right:
        avg_body_angle = (body_angle_left + body_angle_right) / 2
        if avg_body_angle < 160:  # Excessive forward lean suggests rounding
            results['mistakes'].append({
                'issue': 'Rounded back (spinal flexion)',
                'severity': 'severe',
                'fix': 'Keep back straight and chest up, engage core'
            })
    
    # 2. Too much knee bend (squatting instead of deadlifting)
    if knee_angle_left and knee_angle_right:
        avg_knee_angle = (knee_angle_left + knee_angle_right) / 2
        if avg_knee_angle < 140:
            results['mistakes'].append({
                'issue': 'Too much knee bend (squatting the weight)',
                'severity': 'moderate',
                'fix': 'Start with less knee bend, focus on hip hinge'
            })
    
    # 3. Knees extending too early
    # This would require temporal analysis, but we can check if knees are too straight
    if knee_angle_left and knee_angle_right:
        if knee_angle_left > 175 and knee_angle_right > 175 and \
           hip_angle_left and hip_angle_right and \
           (hip_angle_left < 150 or hip_angle_right < 150):
            results['mistakes'].append({
                'issue': 'Knees extending too early',
                'severity': 'moderate',
                'fix': 'Maintain knee position longer, extend hips and knees together'
            })
    
    # Determine overall severity
    if any(m['severity'] == 'severe' for m in results['mistakes']):
        results['severity'] = 'severe'
    elif results['mistakes']:
        results['severity'] = 'moderate'
    
    return results


def analyze_plank(landmarks) -> Dict[str, any]:
    """
    Analyze plank posture and detect mistakes
    """
    results = {
        'angles': {},
        'mistakes': [],
        'severity': 'good'
    }
    
    # Get key landmarks
    left_shoulder = get_landmark_3d(landmarks, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_landmark_3d(landmarks, PoseLandmark.RIGHT_SHOULDER)
    left_hip = get_landmark_3d(landmarks, PoseLandmark.LEFT_HIP)
    right_hip = get_landmark_3d(landmarks, PoseLandmark.RIGHT_HIP)
    left_ankle = get_landmark_3d(landmarks, PoseLandmark.LEFT_ANKLE)
    right_ankle = get_landmark_3d(landmarks, PoseLandmark.RIGHT_ANKLE)
    
    # Calculate body alignment angle
    body_angle_left = calculate_angle(left_shoulder, left_hip, left_ankle)
    body_angle_right = calculate_angle(right_shoulder, right_hip, right_ankle)
    results['angles']['body_alignment_left'] = body_angle_left
    results['angles']['body_alignment_right'] = body_angle_right
    
    # Detect mistakes
    # 1. Sagging hips
    if body_angle_left and body_angle_right:
        avg_angle = (body_angle_left + body_angle_right) / 2
        if avg_angle < 175:
            results['mistakes'].append({
                'issue': 'Hips sagging / arched back',
                'severity': 'moderate',
                'fix': 'Engage core, squeeze glutes, maintain straight line'
            })
    
    # 2. Raised buttocks
    if left_hip and left_shoulder and left_ankle:
        hip_height = left_hip[1]
        shoulder_height = left_shoulder[1]
        if hip_height < shoulder_height - 0.05:
            results['mistakes'].append({
                'issue': 'Buttocks raised too high',
                'severity': 'moderate',
                'fix': 'Lower hips to shoulder level, maintain straight line'
            })
    
    # Determine overall severity
    if any(m['severity'] == 'severe' for m in results['mistakes']):
        results['severity'] = 'severe'
    elif results['mistakes']:
        results['severity'] = 'moderate'
    
    return results


def analyze_lunge(landmarks) -> Dict[str, any]:
    """
    Analyze lunge posture and detect mistakes
    """
    results = {
        'angles': {},
        'mistakes': [],
        'severity': 'good'
    }
    
    # Get key landmarks
    left_hip = get_landmark_3d(landmarks, PoseLandmark.LEFT_HIP)
    right_hip = get_landmark_3d(landmarks, PoseLandmark.RIGHT_HIP)
    left_knee = get_landmark_3d(landmarks, PoseLandmark.LEFT_KNEE)
    right_knee = get_landmark_3d(landmarks, PoseLandmark.RIGHT_KNEE)
    left_ankle = get_landmark_3d(landmarks, PoseLandmark.LEFT_ANKLE)
    right_ankle = get_landmark_3d(landmarks, PoseLandmark.RIGHT_ANKLE)
    left_shoulder = get_landmark_3d(landmarks, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_landmark_3d(landmarks, PoseLandmark.RIGHT_SHOULDER)
    
    # Calculate angles
    knee_angle_left = calculate_angle(left_hip, left_knee, left_ankle)
    knee_angle_right = calculate_angle(right_hip, right_knee, right_ankle)
    results['angles']['knee_left'] = knee_angle_left
    results['angles']['knee_right'] = knee_angle_right
    
    # Body alignment
    body_angle = calculate_angle(left_shoulder, left_hip, left_ankle)
    results['angles']['body_alignment'] = body_angle
    
    # Detect mistakes
    # 1. Front knee too far forward
    if left_knee and left_ankle:
        if abs(left_knee[0] - left_ankle[0]) > 0.05:
            results['mistakes'].append({
                'issue': 'Front knee over toes',
                'severity': 'moderate',
                'fix': 'Keep front knee aligned over ankle'
            })
    
    # 2. Incorrect depth
    if knee_angle_left and knee_angle_right:
        if knee_angle_left > 120 or knee_angle_right > 120:
            results['mistakes'].append({
                'issue': 'Insufficient lunge depth',
                'severity': 'minor',
                'fix': 'Lower until front thigh is parallel to floor'
            })
    
    # Determine overall severity
    if any(m['severity'] == 'severe' for m in results['mistakes']):
        results['severity'] = 'severe'
    elif results['mistakes']:
        results['severity'] = 'moderate'
    
    return results


def get_all_angles(landmarks) -> Dict[str, float]:
    """
    Calculate all major joint angles from landmarks
    Returns a comprehensive dictionary of all angles
    """
    angles = {}
    
    # Get all landmarks
    left_shoulder = get_landmark_3d(landmarks, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_landmark_3d(landmarks, PoseLandmark.RIGHT_SHOULDER)
    left_elbow = get_landmark_3d(landmarks, PoseLandmark.LEFT_ELBOW)
    right_elbow = get_landmark_3d(landmarks, PoseLandmark.RIGHT_ELBOW)
    left_wrist = get_landmark_3d(landmarks, PoseLandmark.LEFT_WRIST)
    right_wrist = get_landmark_3d(landmarks, PoseLandmark.RIGHT_WRIST)
    left_hip = get_landmark_3d(landmarks, PoseLandmark.LEFT_HIP)
    right_hip = get_landmark_3d(landmarks, PoseLandmark.RIGHT_HIP)
    left_knee = get_landmark_3d(landmarks, PoseLandmark.LEFT_KNEE)
    right_knee = get_landmark_3d(landmarks, PoseLandmark.RIGHT_KNEE)
    left_ankle = get_landmark_3d(landmarks, PoseLandmark.LEFT_ANKLE)
    right_ankle = get_landmark_3d(landmarks, PoseLandmark.RIGHT_ANKLE)
    
    # Shoulder angles
    angles['left_shoulder'] = calculate_angle(left_elbow, left_shoulder, right_shoulder)
    angles['right_shoulder'] = calculate_angle(right_elbow, right_shoulder, left_shoulder)
    
    # Elbow angles
    angles['left_elbow'] = calculate_angle(left_shoulder, left_elbow, left_wrist)
    angles['right_elbow'] = calculate_angle(right_shoulder, right_elbow, right_wrist)
    
    # Hip angles
    angles['left_hip'] = calculate_angle(left_shoulder, left_hip, left_knee)
    angles['right_hip'] = calculate_angle(right_shoulder, right_hip, right_knee)
    
    # Knee angles
    angles['left_knee'] = calculate_angle(left_hip, left_knee, left_ankle)
    angles['right_knee'] = calculate_angle(right_hip, right_knee, right_ankle)
    
    # Body alignment
    angles['body_alignment_left'] = calculate_angle(left_shoulder, left_hip, left_ankle)
    angles['body_alignment_right'] = calculate_angle(right_shoulder, right_hip, right_ankle)
    
    return angles


def analyze_generic_exercise(landmarks, exercise_type: str = None) -> Dict[str, any]:
    """
    Generic exercise analyzer that calls specific analyzers based on exercise type
    
    Args:
        landmarks: MediaPipe landmarks
        exercise_type: Type of exercise (squat, pushup, deadlift, plank, lunge)
    
    Returns:
        Analysis results with angles, mistakes, and severity
    """
    exercise_type = exercise_type.lower() if exercise_type else 'generic'
    
    if exercise_type == 'squat':
        return analyze_squat(landmarks)
    elif exercise_type in ['pushup', 'push-up']:
        return analyze_pushup(landmarks)
    elif exercise_type == 'deadlift':
        return analyze_deadlift(landmarks)
    elif exercise_type == 'plank':
        return analyze_plank(landmarks)
    elif exercise_type == 'lunge':
        return analyze_lunge(landmarks)
    else:
        # Generic analysis - return all angles
        return {
            'angles': get_all_angles(landmarks),
            'mistakes': [],
            'severity': 'good'
        }


if __name__ == "__main__":
    print("Posture Analyzer for Gym Exercises")
    print("Functions available:")
    print("- analyze_squat(landmarks)")
    print("- analyze_pushup(landmarks)")
    print("- analyze_deadlift(landmarks)")
    print("- analyze_plank(landmarks)")
    print("- analyze_lunge(landmarks)")
    print("- get_all_angles(landmarks)")
    print("- analyze_generic_exercise(landmarks, exercise_type)")
