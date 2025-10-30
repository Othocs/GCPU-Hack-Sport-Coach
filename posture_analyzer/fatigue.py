import numpy as np
from typing import Dict, List, Optional
from collections import deque
from .landmarks import PoseLandmark, get_landmark_3d

class FatigueAnalyzer:
    def __init__(
        self, 
        window_size: int = 30, 
        threshold: float = 0.15, 
        dynamic: bool = True
    ):
        self.window_size = window_size
        self.default_threshold = threshold
        self.dynamic = dynamic
        self.pose_history = deque(maxlen=window_size)
        self.fatigue_scores = {
            'shoulder_stability': 0.0,
            'core_stability': 0.0,
            'knee_stability': 0.0,
            'elbow_stability': 0.0,
            'ankle_stability': 0.0,
            'velocity': 0.0,
            'early_fatigue': 0.0,
            'overall': 0.0
        }
        self._dynamic_threshold = threshold

    def update(self, landmarks, user_profile: Optional[dict] = None) -> Dict[str, float]:
        current_pose = self._extract_key_points(landmarks)
        if not current_pose:
            return self.fatigue_scores

        self.pose_history.append(current_pose)

        if len(self.pose_history) < 2:
            return self.fatigue_scores
        
        # Variation des jointures principales
        self.fatigue_scores['shoulder_stability'] = min(self._calculate_joint_variation(PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER) / 5.0, 1.0)
        self.fatigue_scores['core_stability'] = min(self._calculate_joint_variation(PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP) / 4.0, 1.0)
        self.fatigue_scores['knee_stability'] = min(self._calculate_joint_variation(PoseLandmark.LEFT_KNEE, PoseLandmark.RIGHT_KNEE) / 3.0, 1.0)
        self.fatigue_scores['elbow_stability'] = min(self._calculate_joint_variation(PoseLandmark.LEFT_ELBOW, PoseLandmark.RIGHT_ELBOW) / 3.0, 1.0)
        self.fatigue_scores['ankle_stability'] = min(self._calculate_joint_variation(PoseLandmark.LEFT_ANKLE, PoseLandmark.RIGHT_ANKLE) / 3.0, 1.0)

        # Analyse de la vélocité : indicateur de mouvements saccadés (fatigue musculaire)
        self.fatigue_scores['velocity'] = self._calculate_velocity()

        # Fatigue précoce : micro-oscillations des épaules (signes de perte de stabilité)
        self.fatigue_scores['early_fatigue'] = self._calculate_early_fatigue()

        # Seuil dynamique
        if self.dynamic and user_profile is not None:
            self._dynamic_threshold = self._adapt_threshold(user_profile)
        else:
            self._dynamic_threshold = self.default_threshold

        self.fatigue_scores['overall'] = (
            self.fatigue_scores['shoulder_stability'] + 
            self.fatigue_scores['core_stability'] + 
            self.fatigue_scores['knee_stability'] + 
            self.fatigue_scores['velocity'] +
            self.fatigue_scores['early_fatigue']
        ) / 5.0

        return self.fatigue_scores

    def is_fatigued(self) -> bool:
        return self.fatigue_scores['overall'] > self._dynamic_threshold

    def _extract_key_points(self, landmarks):
        points = {}
        key_indices = [
            PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER,
            PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP,
            PoseLandmark.LEFT_KNEE, PoseLandmark.RIGHT_KNEE,
            PoseLandmark.LEFT_ANKLE, PoseLandmark.RIGHT_ANKLE,
            PoseLandmark.LEFT_ELBOW, PoseLandmark.RIGHT_ELBOW
        ]
        for idx in key_indices:
            point = get_landmark_3d(landmarks, idx)
            if point is not None:
                points[idx] = point
        return points if len(points) == len(key_indices) else None

    def _calculate_joint_variation(self, joint1: int, joint2: int) -> float:
        if len(self.pose_history) < 2:
            return 0.0
        variations = []
        for i in range(1, len(self.pose_history)):
            prev_pose = self.pose_history[i-1]
            curr_pose = self.pose_history[i]
            if joint1 in prev_pose and joint1 in curr_pose and joint2 in prev_pose and joint2 in curr_pose:
                prev_dist = np.linalg.norm(prev_pose[joint1] - prev_pose[joint2])
                curr_dist = np.linalg.norm(curr_pose[joint1] - curr_pose[joint2])
                variation = abs(curr_dist - prev_dist) / (prev_dist + 1e-8)
                variations.append(variation)
        return np.mean(variations) * 100 if variations else 0.0

    def _calculate_velocity(self) -> float:
        """Analyse la vitesse des points clefs entre deux frames (très élevé = perte de contrôle possible)."""
        if len(self.pose_history) < 2:
            return 0.0
        velocities = []
        for i in range(1, len(self.pose_history)):
            for k in self.pose_history[i]:
                if k in self.pose_history[i-1]:
                    diff = self.pose_history[i][k] - self.pose_history[i-1][k]
                    velocities.append(np.linalg.norm(diff))
        return min(np.mean(velocities) * 5, 1.0) if velocities else 0.0

    def _calculate_early_fatigue(self) -> float:
        """Détecte micro-oscillations des épaules (tremblements = signe de fatigue débutant)."""
        if len(self.pose_history) < 4:
            return 0.0
        left_shoulder = [pose[PoseLandmark.LEFT_SHOULDER] for pose in self.pose_history if PoseLandmark.LEFT_SHOULDER in pose]
        if len(left_shoulder) < 4:
            return 0.0
        # Calcul de la somme des déplacements successifs (temporellement proches)
        jitter = np.sum([np.linalg.norm(left_shoulder[i+1] - left_shoulder[i]) for i in range(len(left_shoulder)-1)])
        return min(jitter * 2, 1.0)

    def _adapt_threshold(self, user_profile: dict) -> float:
        """Adapte dynamiquement le seuil de fatigue selon le profil de l'utilisateur."""
        base = self.default_threshold
        age = user_profile.get('age', 30)
        if age < 20:      # jeunes sportifs
            return base + 0.03
        elif age > 40:    # un peu moins de réserve
            return base - 0.03
        return base