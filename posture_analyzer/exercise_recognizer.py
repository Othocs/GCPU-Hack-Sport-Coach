import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
from .landmarks import PoseLandmark, get_landmark_3d, _landmarks_to_np
from .angles import calculate_angle
from .detect import quick_detect_exercise

class ExerciseRecognizer:
    def __init__(
        self, 
        confidence_threshold: float = 0.7, 
        min_frames: int = 10, 
        use_quick_detect: bool = True,
        smooth_window: int = 5
    ):
        self.confidence_threshold = confidence_threshold
        self.min_frames = min_frames
        self.use_quick_detect = use_quick_detect
        self.exercise_scores = defaultdict(float)
        self.current_exercise = None
        self.confidence = 0.0
        self.history = deque(maxlen=30)
        self.score_smooth = deque(maxlen=smooth_window)
        self.last_phase = None
        self.exercise_profiles = self._get_default_profiles()

    def recognize(
        self, 
        landmarks, 
        fatigue_score: Optional[float] = None, 
        user_profile: Optional[dict] = None
    ) -> Tuple[Optional[str], float, str]:
        """Détecte l'exercice, sa confiance, et la phase (init/mid/end)."""
        if user_profile is not None:
            self.exercise_profiles = self._get_user_profiles(user_profile)

        if landmarks is None:
            return self.current_exercise, self.confidence, self.last_phase

        # Détection rapide "mode boost"
        if self.use_quick_detect and (self.current_exercise is None or self.confidence < 0.5):
            quick_result = quick_detect_exercise(landmarks)
            if quick_result and quick_result in self.exercise_profiles:
                self._update_history(quick_result, fast_mode=True)
                if len(self.history) >= (self.min_frames // 2):
                    self.current_exercise = quick_result
                    self.confidence = 0.8
                    self.last_phase = 'init'
                    return self.current_exercise, self.confidence, self.last_phase

        angles = self._calculate_key_angles(landmarks)
        if not angles:
            return self.current_exercise, self.confidence, self.last_phase

        scores = self._calculate_exercise_scores(angles)
        self.score_smooth.append(scores)
        smooth_scores = self._get_smoothed_scores()

        if not smooth_scores:
            return None, 0.0, self.last_phase

        best_exercise = max(smooth_scores.items(), key=lambda x: x[1])
        self._update_history(best_exercise[0])

        if len(self.history) >= self.min_frames:
            self._update_confidence()
        
        # On baisse la confiance si beaucoup de fatigue détectée
        if fatigue_score is not None and fatigue_score > 0.8:
            self.confidence = max(0, self.confidence - 0.2)

        # Détermination de la phase du mouvement (prototype, à spécialiser selon l'exercice)
        phase = self._detect_phase(angles, best_exercise[0])
        self.last_phase = phase

        return self.current_exercise, self.confidence, phase

    def _get_default_profiles(self) -> Dict[str, dict]:
        return {
            'squat': {
                'key_angles': ['left_knee', 'right_knee', 'left_hip', 'right_hip'],
                'expected_ranges': {
                    'knee': (80, 140),
                    'hip': (60, 120)
                },
                'weight': 1.0
            },
            'pushup': {
                'key_angles': ['left_elbow', 'right_elbow', 'left_shoulder', 'right_shoulder'],
                'expected_ranges': {
                    'elbow': (60, 160),
                    'shoulder': (0, 45)
                },
                'weight': 1.0
            },
            'plank': {
                'key_angles': ['body_alignment_left', 'body_alignment_right'],
                'expected_ranges': {
                    'body_alignment': (160, 200)
                },
                'weight': 1.0
            },
            'lunge': {
                'key_angles': ['left_knee', 'right_knee', 'left_hip', 'right_hip', 'body_alignment_left', 'body_alignment_right'],
                'expected_ranges': {
                    'knee': (60, 150),
                    'hip': (60, 120),
                    'body_alignment': (160, 200)
                },
                'weight': 1.2
            },
            'deadlift': {
                'key_angles': ['left_knee', 'right_knee', 'left_hip', 'right_hip', 'body_alignment_left', 'body_alignment_right'],
                'expected_ranges': {
                    'knee': (160, 180),
                    'hip': (120, 170),
                    'body_alignment': (150, 200)
                },
                'weight': 1.1
            }
        }

    def _get_user_profiles(self, user_profile: dict) -> dict:
        base = self._get_default_profiles()
        for ex, prof in base.items():
            if user_profile.get('flexibility') == 'high':
                for k in prof['expected_ranges']:
                    minv, maxv = prof['expected_ranges'][k]
                    prof['expected_ranges'][k] = (minv-10, maxv+10)
        return base

    def _update_history(self, exercise: str, fast_mode: bool = False):
        if fast_mode:
            for _ in range(3):
                self.history.append(exercise)
        else:
            self.history.append(exercise)

    def _get_smoothed_scores(self) -> Dict[str, float]:
        if not self.score_smooth:
            return {}
        summed = defaultdict(float)
        for d in self.score_smooth:
            for k, v in d.items():
                summed[k] += v
        n = len(self.score_smooth)
        return {k: v/n for k, v in summed.items()}

    def _calculate_key_angles(self, landmarks) -> Dict[str, float]:
        L = _landmarks_to_np(landmarks)
        angles = {}

        def add_angle(name: str, i1: int, i2: int, i3: int) -> None:
            angle = calculate_angle(
                get_landmark_3d(L, i1),
                get_landmark_3d(L, i2),
                get_landmark_3d(L, i3)
            )
            if angle is not None:
                angles[name] = angle

        add_angle('left_knee', PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_ANKLE)
        add_angle('right_knee', PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_ANKLE)
        add_angle('left_hip', PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE)
        add_angle('right_hip', PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE)
        add_angle('left_elbow', PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_WRIST)
        add_angle('right_elbow', PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_WRIST)
        add_angle('body_alignment_left', PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_ANKLE)
        add_angle('body_alignment_right', PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_ANKLE)
        return angles

    def _calculate_exercise_scores(self, angles: Dict[str, float]) -> Dict[str, float]:
        scores = {}
        for exercise, profile in self.exercise_profiles.items():
            score = 0.0
            total_weight = 0
            for angle_name, angle_value in angles.items():
                if angle_value is None:
                    continue
                angle_type = self._get_angle_type(angle_name)
                if angle_type in profile['expected_ranges']:
                    min_angle, max_angle = profile['expected_ranges'][angle_type]
                    if min_angle <= angle_value <= max_angle:
                        score += 1.0
                    else:
                        distance = min(abs(angle_value - min_angle), abs(angle_value - max_angle))
                        score += max(0, 1.0 - (distance / 90.0))
                    total_weight += 1.0
            if total_weight > 0:
                scores[exercise] = (score / total_weight) * profile.get('weight', 1.0)
        return scores

    def _get_angle_type(self, angle_name: str) -> str:
        if 'knee' in angle_name:
            return 'knee'
        elif 'hip' in angle_name:
            return 'hip'
        elif 'elbow' in angle_name:
            return 'elbow'
        elif 'shoulder' in angle_name:
            return 'shoulder'
        elif 'body_alignment' in angle_name:
            return 'body_alignment'
        return 'other'

    def _detect_phase(self, angles: Dict[str, float], exercise: str) -> str:
        """Exemple : phase = down (end), up (init), milieu..."""
        if exercise not in self.exercise_profiles:
            return 'unk'
        profile = self.exercise_profiles[exercise]
        if 'knee' in profile['expected_ranges']:
            any_knee = [angles.get('left_knee', 0), angles.get('right_knee', 0)]
            valids = [k for k in any_knee if k]
            if not valids:
                return 'unk'
            mean_knee = sum(valids) / len(valids)
            min_knee, max_knee = profile['expected_ranges']['knee']
            if mean_knee < min_knee + 10:
                return 'end'
            elif mean_knee > max_knee - 10:
                return 'init'
            else:
                return 'mid'
        return 'unk'

    def _update_confidence(self):
        if not self.history:
            self.confidence = 0.0
            return
        counts = defaultdict(int)
        for ex in self.history:
            counts[ex] += 1

        most_common = max(counts.items(), key=lambda x: x[1])
        confidence = most_common[1] / len(self.history)

        if self.current_exercise and most_common[0] != self.current_exercise:
            self.confidence = confidence * 0.7
        else:
            self.confidence = min(1.0, confidence * 1.1)
        if confidence >= self.confidence_threshold:
            self.current_exercise = most_common[0]