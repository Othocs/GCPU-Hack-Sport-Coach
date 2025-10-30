import numpy as np
from typing import Optional
from .landmarks import PoseLandmark, _landmarks_to_np, _safe_x
from .angles import _angle_at

def _coalesce_angles(*vals):
    return [v for v in vals if v is not None]

def quick_detect_exercise(landmarks) -> Optional[str]:
    L = _landmarks_to_np(landmarks)

    knee_left = _angle_at(L, PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_ANKLE)
    knee_right = _angle_at(L, PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_ANKLE)
    hip_left = _angle_at(L, PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE)
    hip_right = _angle_at(L, PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE)
    body_left = _angle_at(L, PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_ANKLE)
    body_right = _angle_at(L, PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_ANKLE)
    elbow_left = _angle_at(L, PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_WRIST)
    elbow_right = _angle_at(L, PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_WRIST)

    bodies = _coalesce_angles(body_left, body_right)
    if bodies and np.mean(bodies) >= 170.0:
        elbows = _coalesce_angles(elbow_left, elbow_right)
        if elbows and np.mean(elbows) < 160.0:
            return 'pushup'
        return 'plank'

    knees = _coalesce_angles(knee_left, knee_right)
    if len(knees) == 2 and all(k < 140.0 for k in knees):
        return 'squat'

    lkx = _safe_x(L, PoseLandmark.LEFT_KNEE)
    lax = _safe_x(L, PoseLandmark.LEFT_ANKLE)
    rkx = _safe_x(L, PoseLandmark.RIGHT_KNEE)
    rax = _safe_x(L, PoseLandmark.RIGHT_ANKLE)
    asym_angle = (knee_left is not None and knee_right is not None and abs(knee_left - knee_right) > 15.0)
    asym_xy = (lkx is not None and lax is not None and abs(lkx - lax) > 0.06) or \
              (rkx is not None and rax is not None and abs(rkx - rax) > 0.06)
    if asym_angle or asym_xy:
        return 'lunge'

    if knees and min(knees) >= 140.0 and bodies and np.mean(bodies) < 170.0:
        return 'deadlift'

    return None