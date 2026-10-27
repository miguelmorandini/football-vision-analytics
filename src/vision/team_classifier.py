"""Team color classification using K-Means clustering on jersey crops."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from sklearn.cluster import KMeans

from src.vision.detector import Detection

logger = logging.getLogger(__name__)


class TeamColorClassifier:
    """Classifies detected soccer players into Team A, Team B, Goalkeeper, or Referee."""

    def __init__(self, n_clusters: int = 2):
        self.n_clusters = n_clusters
        self.kmeans: Optional[KMeans] = None
        self.team_colors: Dict[str, np.ndarray] = {}
        self.player_team_cache: Dict[int, str] = {}
        self.fitted = False

    @staticmethod
    def extract_jersey_crop(frame: np.ndarray, box: Tuple[float, float, float, float]) -> Optional[np.ndarray]:
        """Extract the upper torso crop (jersey region) of a player.

        Avoids head/face (top 0-15%) and shorts/legs/pitch background (bottom 50-100%).
        """
        h_frame, w_frame = frame.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in box]

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w_frame, x2)
        y2 = min(h_frame, y2)

        box_h = y2 - y1
        box_w = x2 - x1

        if box_h < 15 or box_w < 8:
            return None

        # Torso vertical window: 15% to 50% of total height
        torso_y1 = y1 + int(box_h * 0.15)
        torso_y2 = y1 + int(box_h * 0.50)

        # Torso horizontal window: inset 10% to avoid background bleed
        torso_x1 = x1 + int(box_w * 0.10)
        torso_x2 = x2 - int(box_w * 0.10)

        if torso_y2 <= torso_y1 or torso_x2 <= torso_x1:
            return None

        crop = frame[torso_y1:torso_y2, torso_x1:torso_x2]
        return crop

    @staticmethod
    def extract_dominant_color(crop: np.ndarray) -> Optional[np.ndarray]:
        """Extract dominant jersey color while filtering out green pitch background."""
        if crop is None or crop.size == 0:
            return None

        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        # Mask out grass green pixels (Hue 35 to 85)
        lower_green = np.array([35, 30, 30])
        upper_green = np.array([85, 255, 255])
        grass_mask = cv2.inRange(hsv, lower_green, upper_green)
        non_grass_mask = cv2.bitwise_not(grass_mask)

        valid_pixels = crop[non_grass_mask > 0]
        if len(valid_pixels) < 20:
            # If all was filtered, use all crop pixels
            valid_pixels = crop.reshape(-1, 3)

        # Convert to Lab color space for perceptual color consistency
        lab_pixels = cv2.cvtColor(valid_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2Lab).reshape(-1, 3)
        mean_color = np.median(lab_pixels, axis=0)
        return mean_color

    def fit(self, frame: np.ndarray, detections: List[Detection]):
        """Fit K-Means clustering model on initial frame of detected players."""
        player_colors: List[np.ndarray] = []
        player_indices: List[int] = []

        for idx, det in enumerate(detections):
            if det.class_name != "player":
                continue
            crop = self.extract_jersey_crop(frame, det.box)
            color = self.extract_dominant_color(crop)
            if color is not None:
                player_colors.append(color)
                player_indices.append(idx)

        if len(player_colors) < self.n_clusters:
            logger.warning("Not enough players detected to fit team colors.")
            return

        features = np.array(player_colors, dtype=np.float32)
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        labels = self.kmeans.fit_predict(features)

        self.team_colors = {
            "team_a": self.kmeans.cluster_centers_[0],
            "team_b": self.kmeans.cluster_centers_[1]
        }
        self.fitted = True

        for p_idx, cluster_id in zip(player_indices, labels):
            team_id = "team_a" if cluster_id == 0 else "team_b"
            detections[p_idx].team_id = team_id
            if detections[p_idx].track_id is not None:
                self.player_team_cache[detections[p_idx].track_id] = team_id

    def classify(self, frame: np.ndarray, detections: List[Detection]) -> List[Detection]:
        """Classify team for all detections in the frame.

        Uses track ID cache for temporal stability, and predicts using fitted clusters.
        """
        if not self.fitted:
            self.fit(frame, detections)
            return detections

        for det in detections:
            if det.class_name != "player":
                continue

            # Check track cache first to prevent team flickering
            if det.track_id is not None and det.track_id in self.player_team_cache:
                det.team_id = self.player_team_cache[det.track_id]
                continue

            crop = self.extract_jersey_crop(frame, det.box)
            color = self.extract_dominant_color(crop)

            if color is not None and self.kmeans is not None:
                cluster_id = self.kmeans.predict(color.reshape(1, -1))[0]
                team_id = "team_a" if cluster_id == 0 else "team_b"
                det.team_id = team_id
                if det.track_id is not None:
                    self.player_team_cache[det.track_id] = team_id
            else:
                det.team_id = "team_a"

        return detections
