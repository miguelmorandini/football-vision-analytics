"""Pitch Homography and Perspective Transformation module.

Maps broadcast video pixel coordinates to a normalized 2D tactical football pitch.
"""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import cv2
import numpy as np

from src.config import PITCH_LENGTH, PITCH_WIDTH

logger = logging.getLogger(__name__)


class PitchHomographyTransformer:
    """Calculates and applies perspective transformation from broadcast video to 2D pitch."""

    def __init__(
        self,
        source_points: Optional[np.ndarray] = None,
        target_points: Optional[np.ndarray] = None,
        pitch_length: float = PITCH_LENGTH,
        pitch_width: float = PITCH_WIDTH
    ):
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.homography_matrix: Optional[np.ndarray] = None

        if source_points is not None and target_points is not None:
            self.set_calibration_points(source_points, target_points)
        else:
            self.set_default_broadcast_calibration()

    def set_calibration_points(self, source_points: np.ndarray, target_points: np.ndarray):
        """Compute the 3x3 homography matrix H given at least 4 point correspondences."""
        if len(source_points) < 4 or len(target_points) < 4:
            raise ValueError("At least 4 corresponding points are required to compute Homography.")

        src = np.array(source_points, dtype=np.float32)
        dst = np.array(target_points, dtype=np.float32)

        H, _ = cv2.findHomography(src, dst)
        self.homography_matrix = H

    def set_default_broadcast_calibration(
        self,
        frame_width: int = 1280,
        frame_height: int = 720
    ):
        """Set a realistic homography calibration matrix for standard television broadcast camera angles."""
        # Source 4 key points in typical TV broadcast frame (main camera high midfield view)
        src = np.array([
            [frame_width * 0.08, frame_height * 0.38],   # Top-left pitch touchline
            [frame_width * 0.92, frame_height * 0.38],   # Top-right pitch touchline
            [frame_width * 0.98, frame_height * 0.94],   # Bottom-right pitch touchline
            [frame_width * 0.02, frame_height * 0.94],   # Bottom-left pitch touchline
        ], dtype=np.float32)

        # Target 2D Pitch Coordinates (meters: [0, 105] x [0, 68])
        dst = np.array([
            [15.0, 5.0],                  # Near Team A defensive midfield
            [90.0, 5.0],                  # Near Team B defensive midfield
            [100.0, self.pitch_width - 5],# Near Team B bottom touchline
            [5.0, self.pitch_width - 5],  # Near Team A bottom touchline
        ], dtype=np.float32)

        self.set_calibration_points(src, dst)

    def transform_point(self, x: float, y: float) -> Tuple[float, float]:
        """Transform a single 2D camera pixel coordinate into pitch coordinates (meters)."""
        if self.homography_matrix is None:
            return 50.0, 34.0

        pt = np.array([[[x, y]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(pt, self.homography_matrix)
        pitch_x = float(transformed[0][0][0])
        pitch_y = float(transformed[0][0][1])

        # Clamp inside pitch boundaries
        pitch_x = max(0.0, min(self.pitch_length, pitch_x))
        pitch_y = max(0.0, min(self.pitch_width, pitch_y))

        return round(pitch_x, 2), round(pitch_y, 2)

    def transform_points(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Transform a list of camera coordinates into pitch coordinates."""
        if not points or self.homography_matrix is None:
            return []

        pts = np.array([points], dtype=np.float32)
        transformed = cv2.perspectiveTransform(pts, self.homography_matrix)[0]

        result = []
        for p in transformed:
            px = max(0.0, min(self.pitch_length, float(p[0])))
            py = max(0.0, min(self.pitch_width, float(p[1])))
            result.append((round(px, 2), round(py, 2)))

        return result
