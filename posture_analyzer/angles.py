import numpy as np
from typing import Optional

def calculate_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> Optional[float]:
    if p1 is None or p2 is None or p3 is None:
        return None
    if np.isnan(p1).any() or np.isnan(p2).any() or np.isnan(p3).any():
        return None
    v1 = p1 - p2; v2 = p3 - p2
    n1 = np.linalg.norm(v1); n2 = np.linalg.norm(v2)
    if n1 == 0.0 or n2 == 0.0:
        return None
    cos_angle = float(np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0))
    return float(np.degrees(np.arccos(cos_angle)))

def _angle_at(L: np.ndarray, i1: int, i2: int, i3: int) -> Optional[float]:
    p1, p2, p3 = L[i1], L[i2], L[i3]
    if np.isnan(p1).any() or np.isnan(p2).any() or np.isnan(p3).any():
        return None
    v1 = p1 - p2; v2 = p3 - p2
    n1 = np.linalg.norm(v1); n2 = np.linalg.norm(v2)
    if n1 == 0.0 or n2 == 0.0:
        return None
    cos_angle = float(np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0))
    return float(np.degrees(np.arccos(cos_angle)))

def calculate_distance(p1: np.ndarray, p2: np.ndarray) -> Optional[float]:
    if p1 is None or p2 is None:
        return None
    if np.isnan(p1).any() or np.isnan(p2).any():
        return None
    return float(np.linalg.norm(p1 - p2))