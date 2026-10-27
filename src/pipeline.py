"""End-to-end Computer Vision and Tactical Video Processing Pipeline."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import cv2
import numpy as np

from src.config import TEAM_COLORS
from src.tactics.formation_detector import FormationDetector
from src.vision.detector import Detection, FootballDetector
from src.vision.homography import PitchHomographyTransformer
from src.vision.number_ocr import JerseyNumberRecognizer
from src.vision.team_classifier import TeamColorClassifier
from src.vision.tracker import FootballTracker

logger = logging.getLogger(__name__)


class FootballVideoPipeline:
    """Full analysis pipeline for soccer match video processing."""

    def __init__(
        self,
        detector: Optional[FootballDetector] = None,
        tracker: Optional[FootballTracker] = None,
        team_classifier: Optional[TeamColorClassifier] = None,
        homography: Optional[PitchHomographyTransformer] = None,
        ocr: Optional[JerseyNumberRecognizer] = None,
        formation_detector: Optional[FormationDetector] = None,
    ):
        self.detector = detector or FootballDetector()
        self.tracker = tracker or FootballTracker()
        self.team_classifier = team_classifier or TeamColorClassifier()
        self.homography = homography or PitchHomographyTransformer()
        self.ocr = ocr or JerseyNumberRecognizer()
        self.formation_detector = formation_detector or FormationDetector()

    def process_frame(
        self,
        frame: np.ndarray,
        frame_idx: int = 0
    ) -> Dict[str, Any]:
        """Process a single video frame through all computer vision stages."""
        # 1. Detection
        detections = self.detector.detect(frame)

        # 2. Tracking
        tracked = self.tracker.update(detections)

        # 3. Team Classification
        classified = self.team_classifier.classify(frame, tracked)

        players_data: List[Dict[str, Any]] = []
        ball_data: Optional[Dict[str, Any]] = None

        for det in classified:
            # 4. Homography: map feet coordinate to pitch
            feet_x, feet_y = det.bottom_center
            pitch_x, pitch_y = self.homography.transform_point(feet_x, feet_y)
            det.pitch_x = pitch_x
            det.pitch_y = pitch_y

            if det.class_name == "player":
                # 5. Jersey Number OCR (strict confidence check)
                number = self.ocr.process_player(frame, det.box, track_id=det.track_id)
                det.jersey_number = number

                players_data.append({
                    "track_id": det.track_id,
                    "team_id": det.team_id or "team_a",
                    "box": list(det.box),
                    "confidence": round(det.confidence, 2),
                    "pitch_x": pitch_x,
                    "pitch_y": pitch_y,
                    "jersey_number": number
                })
            elif det.class_name == "ball":
                ball_data = {
                    "box": list(det.box),
                    "pitch_x": pitch_x,
                    "pitch_y": pitch_y
                }

        # 6. Tactical Formation Inference
        team_a_players = [p for p in players_data if p["team_id"] == "team_a"]
        team_b_players = [p for p in players_data if p["team_id"] == "team_b"]

        metrics_a = self.formation_detector.detect_formation(team_a_players, attacking_left_to_right=True)
        metrics_b = self.formation_detector.detect_formation(team_b_players, attacking_left_to_right=False)

        return {
            "frame_idx": frame_idx,
            "players": players_data,
            "ball": ball_data,
            "team_a": {
                "formation": metrics_a.formation_name,
                "line_counts": metrics_a.line_counts,
                "compactness_width": metrics_a.compactness_width,
                "compactness_depth": metrics_a.compactness_depth,
                "centroid": metrics_a.team_centroid
            },
            "team_b": {
                "formation": metrics_b.formation_name,
                "line_counts": metrics_b.line_counts,
                "compactness_width": metrics_b.compactness_width,
                "compactness_depth": metrics_b.compactness_depth,
                "centroid": metrics_b.team_centroid
            }
        }

    def annotate_frame(self, frame: np.ndarray, frame_data: Dict[str, Any]) -> np.ndarray:
        """Draw bounding boxes, team color halos, and jersey numbers on the video frame."""
        annotated = frame.copy()

        for p in frame_data.get("players", []):
            box = p.get("box")
            if not box:
                continue
            x1, y1, x2, y2 = [int(v) for v in box]
            team_id = p.get("team_id", "team_a")
            color_cfg = TEAM_COLORS.get(team_id, TEAM_COLORS["team_a"])

            # Hex to BGR for OpenCV
            hex_code = color_cfg["primary_hex"].lstrip("#")
            rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
            bgr = (rgb[2], rgb[1], rgb[0])

            # Draw bottom marker / ground ellipse
            cx = int((x1 + x2) / 2)
            ew = int((x2 - x1) * 0.55)
            cv2.ellipse(annotated, (cx, y2), (ew, 8), 0, 0, 360, bgr, 2)

            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), bgr, 2)

            # Draw label banner
            num_str = f"#{p['jersey_number']}" if p.get("jersey_number") is not None else f"ID {p.get('track_id')}"
            label = f"{num_str}"
            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)

            cv2.rectangle(annotated, (x1, max(0, y1 - lh - 6)), (x1 + lw + 6, y1), bgr, -1)
            cv2.putText(
                annotated, label, (x1 + 3, max(lh + 2, y1 - 4)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA
            )

        # Draw ball
        ball = frame_data.get("ball")
        if ball and ball.get("box"):
            bx1, by1, bx2, by2 = [int(v) for v in ball["box"]]
            cv2.rectangle(annotated, (bx1, by1), (bx2, by2), (0, 255, 255), 2)
            cv2.circle(annotated, (int((bx1+bx2)/2), int((by1+by2)/2)), 4, (0, 255, 255), -1)

        return annotated

    def process_video(
        self,
        video_path: str,
        output_json_path: Optional[str] = None,
        max_frames: int = 150,
        frame_stride: int = 2,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """Process a video file and save/return telemetry timeline."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open video file: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        frames_to_read = min(total_frames, max_frames)
        timeline: List[Dict[str, Any]] = []

        curr_frame_idx = 0
        processed_count = 0

        while cap.isOpened() and curr_frame_idx < frames_to_read:
            ret, frame = cap.read()
            if not ret:
                break

            if curr_frame_idx % frame_stride == 0:
                frame_telemetry = self.process_frame(frame, frame_idx=curr_frame_idx)
                timeline.append(frame_telemetry)
                processed_count += 1

                if progress_callback:
                    pct = min(1.0, curr_frame_idx / max(1, frames_to_read))
                    progress_callback(pct, f"Processing frame {curr_frame_idx}/{frames_to_read}")

            curr_frame_idx += 1

        cap.release()

        result = {
            "video_path": video_path,
            "total_frames": total_frames,
            "processed_frames": len(timeline),
            "fps": fps,
            "resolution": [width, height],
            "timeline": timeline
        }

        if output_json_path:
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

        return result
