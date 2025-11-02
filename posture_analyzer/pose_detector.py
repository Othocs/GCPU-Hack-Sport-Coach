"""
PoseDetector wrapper for MediaPipe Pose Landmarker
Provides a simple interface for pose detection in the API
"""

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os


class PoseDetector:
    """Wrapper for MediaPipe Pose Landmarker"""

    def __init__(self):
        self.detector = None
        self._initialize_detector()

    def _find_model_path(self):
        """Find pose landmarker model file"""
        # Try different possible model locations
        possible_paths = [
            "pose_landmarker_lite.task",
            "pose_landmarker_full.task",
            "pose_landmarker_heavy.task",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # If no model found, raise error with helpful message
        raise FileNotFoundError(
            "Pose landmarker model not found. Please download from:\n"
            "https://developers.google.com/mediapipe/solutions/vision/pose_landmarker#models"
        )

    def _initialize_detector(self):
        """Initialize MediaPipe pose detector"""
        model_path = self._find_model_path()

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,  # IMAGE mode for single frames
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_segmentation_masks=False,
        )

        self.detector = vision.PoseLandmarker.create_from_options(options)

    def detect(self, frame_bgr):
        """
        Detect pose landmarks from BGR image

        Args:
            frame_bgr: OpenCV BGR image (numpy array)

        Returns:
            pose_landmarks: List of landmark objects or None if no pose detected
        """
        if self.detector is None:
            raise RuntimeError("Detector not initialized")

        # Convert BGR to RGB
        frame_rgb = frame_bgr[:, :, ::-1].copy()

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # Detect pose
        result = self.detector.detect(mp_image)

        # Return landmarks if detected
        if result.pose_landmarks and len(result.pose_landmarks) > 0:
            return result.pose_landmarks[0]

        return None
