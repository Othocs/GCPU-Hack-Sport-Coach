from typing import Dict, Optional
from .landmarks import PoseLandmark, _landmarks_to_np
from .angles import _angle_at
from .analyzers.squat import analyze_squat
from .analyzers.pushup import analyze_pushup
from .analyzers.deadlift import analyze_deadlift
from .analyzers.plank import analyze_plank
from .analyzers.lunge import analyze_lunge

def get_all_angles(landmarks) -> Dict[str, float]:
    L = _landmarks_to_np(landmarks)

    def maybe(name: str, value: Optional[float], dst: Dict[str, float]):
        if value is not None:
            dst[name] = value

    angles: Dict[str, float] = {}
    maybe('left_shoulder', _angle_at(L, PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER), angles)
    maybe('right_shoulder', _angle_at(L, PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_SHOULDER, PoseLandmark.LEFT_SHOULDER), angles)
    maybe('left_elbow', _angle_at(L, PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_WRIST), angles)
    maybe('right_elbow', _angle_at(L, PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_WRIST), angles)
    maybe('left_hip', _angle_at(L, PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE), angles)
    maybe('right_hip', _angle_at(L, PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE), angles)
    maybe('left_knee', _angle_at(L, PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_ANKLE), angles)
    maybe('right_knee', _angle_at(L, PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_ANKLE), angles)
    maybe('body_alignment_left', _angle_at(L, PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_ANKLE), angles)
    maybe('body_alignment_right', _angle_at(L, PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_ANKLE), angles)
    return angles

def analyze_generic_exercise(landmarks, exercise_type: str = None) -> Dict[str, any]:
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
        return {'angles': get_all_angles(landmarks), 'mistakes': [], 'severity': 'good'}