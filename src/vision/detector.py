"""Object detection module for football players, referees, and the ball."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import numpy as np

from src.config import (
    COCO_PERSON_CLASS_ID,
    COCO_SPORTS_BALL_CLASS_ID,
    DEFAULT_DETECTION_CONF,
    DEFAULT_MODEL_NAME,
)

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Represents a single detected object in a video frame."""
    box: Tuple[float, float, float, float]  # [x1, y1, x2, y2]
    confidence: float
    class_id: int
    class_name: str
    track_id: Optional[int] = None
    team_id: Optional[str] = None
    jersey_number: Optional[int] = None
    pitch_x: Optional[float] = None
    pitch_y: Optional[float] = None

    @property
    def bottom_center(self) -> Tuple[float, float]:
        """Returns the bottom center coordinate of the bounding box (player's feet)."""
        x1, y1, x2, y2 = self.box
        return (x1 + x2) / 2.0, y2

    @property
    def width(self) -> float:
        return self.box[2] - self.box[0]

    @property
    def height(self) -> float:
        return self.box[3] - self.box[1]


class FootballDetector:
    """YOLO-based object detector optimized for football match analysis."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        confidence_threshold: float = DEFAULT_DETECTION_CONF,
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.device = device
        self._model = None

    def _load_model(self):
        """Lazy load the YOLO model."""
        if self._model is None:
            try:
                from ultralytics import YOLO
                logger.info(f"Loading YOLO model: {self.model_name}")
                self._model = YOLO(self.model_name)
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                raise

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Detect players and the soccer ball in an image/frame.

        Args:
            frame: BGR numpy array representing the frame.

        Returns:
            List of Detection instances.
        """
        self._load_model()
        results = self._model(
            frame,
            conf=self.confidence_threshold,
            classes=[COCO_PERSON_CLASS_ID, COCO_SPORTS_BALL_CLASS_ID],
            verbose=False,
            device=self.device
        )

        detections: List[Detection] = []
        if not results or len(results) == 0:
            return detections

        r = results[0]
        boxes = r.boxes
        if boxes is None or len(boxes) == 0:
            return detections

        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            conf = float(box.conf[0].cpu().numpy())
            cls_id = int(box.cls[0].cpu().numpy())

            class_name = "player" if cls_id == COCO_PERSON_CLASS_ID else "ball"
            detections.append(
                Detection(
                    box=(xyxy[0], xyxy[1], xyxy[2], xyxy[3]),
                    confidence=conf,
                    class_id=cls_id,
                    class_name=class_name
                )
            )

        return detections
