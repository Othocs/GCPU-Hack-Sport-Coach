import numpy as np

class PoseLandmark:
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

_NUM_LANDMARKS = 33

def _landmarks_to_np(landmarks) -> np.ndarray:
    L = np.full((_NUM_LANDMARKS, 3), np.nan, dtype=np.float32)
    if not landmarks:
        return L
    n = min(len(landmarks), _NUM_LANDMARKS)
    xs = np.fromiter((landmarks[i].x for i in range(n)), dtype=np.float32, count=n)
    ys = np.fromiter((landmarks[i].y for i in range(n)), dtype=np.float32, count=n)
    zs = np.fromiter((landmarks[i].z for i in range(n)), dtype=np.float32, count=n)
    L[:n, 0] = xs; L[:n, 1] = ys; L[:n, 2] = zs
    return L

def _is_valid(p: np.ndarray) -> bool:
    return p is not None and not np.isnan(p).any()

def get_landmark_3d(landmarks, idx: int) -> np.ndarray:
    if isinstance(landmarks, np.ndarray):
        if idx < 0 or idx >= landmarks.shape[0]:
            return None
        p = landmarks[idx]
        return None if np.isnan(p).any() else p
    if not landmarks or idx >= len(landmarks):
        return None
    return np.array([landmarks[idx].x, landmarks[idx].y, landmarks[idx].z], dtype=np.float32)

def _safe_x(L: np.ndarray, idx: int):
    p = L[idx]
    return None if np.isnan(p).any() else float(p[0])