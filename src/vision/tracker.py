"""Player and ball tracking module using ByteTrack and Kalman filtering."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

from src.vision.detector import Detection

logger = logging.getLogger(__name__)


class FootballTracker:
    """Persistent object tracker for maintaining player IDs across video frames."""

    def __init__(self, track_activation_threshold: float = 0.35, lost_track_buffer: int = 30):
        self.track_activation_threshold = track_activation_threshold
        self.lost_track_buffer = lost_track_buffer
        self._tracker = None
        self._history: Dict[int, List[Tuple[float, float]]] = {}
        self._init_tracker()

    def _init_tracker(self):
        """Initialize the ByteTrack instance from supervision."""
        try:
            import supervision as sv
            self._tracker = sv.ByteTrack(
                track_activation_threshold=self.track_activation_threshold,
                lost_track_buffer=self.lost_track_buffer
            )
            logger.info("ByteTrack initialized successfully.")
        except Exception as e:
            logger.warning(f"supervision ByteTrack not loaded, using fallback tracker: {e}")
            self._tracker = None

    def update(self, detections: List[Detection]) -> List[Detection]:
        """Update tracker state with new frame detections.

        Args:
            detections: List of Detection instances for the current frame.

        Returns:
            List of Detection instances with assigned track_id.
        """
        # Separate players (trackable) and ball
        player_detections = [d for d in detections if d.class_name == "player"]
        ball_detections = [d for d in detections if d.class_name == "ball"]

        if not player_detections:
            return ball_detections

        if self._tracker is not None:
            import supervision as sv

            xyxy = np.array([d.box for d in player_detections], dtype=np.float32)
            confidence = np.array([d.confidence for d in player_detections], dtype=np.float32)
            class_id = np.array([d.class_id for d in player_detections], dtype=int)

            sv_detections = sv.Detections(
                xyxy=xyxy,
                confidence=confidence,
                class_id=class_id
            )

            tracked = self._tracker.update_with_detections(sv_detections)

            # Map tracker IDs back to our Detection objects
            tracked_players: List[Detection] = []
            for i in range(len(tracked)):
                t_box = tracked.xyxy[i].tolist()
                t_conf = float(tracked.confidence[i]) if tracked.confidence is not None else 1.0
                t_id = int(tracked.tracker_id[i]) if tracked.tracker_id is not None else (i + 1)

                det = Detection(
                    box=(t_box[0], t_box[1], t_box[2], t_box[3]),
                    confidence=t_conf,
                    class_id=0,
                    class_name="player",
                    track_id=t_id
                )
                tracked_players.append(det)

                # Record trajectory history (feet position)
                feet = det.bottom_center
                if t_id not in self._history:
                    self._history[t_id] = []
                self._history[t_id].append(feet)
                if len(self._history[t_id]) > 60:
                    self._history[t_id].pop(0)

            return tracked_players + ball_detections
        else:
            # Simple fallback ID assignment
            for idx, d in enumerate(player_detections):
                d.track_id = idx + 1
            return player_detections + ball_detections

    def get_track_history(self, track_id: int) -> List[Tuple[float, float]]:
        """Retrieve recent trajectory trail for a tracked player."""
        return self._history.get(track_id, [])

    def reset(self):
        """Reset tracking states."""
        self._history.clear()
        self._init_tracker()
