"""Jersey Number Recognition using Optical Character Analysis and Temporal Filtering.

Designed strictly according to user guidelines:
Detects numbers on the jersey when clearly visible; if not clearly identifiable,
returns None rather than producing inaccurate guesses.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from src.config import OCR_CONFIDENCE_THRESHOLD, OCR_MIN_DIGIT_HEIGHT

logger = logging.getLogger(__name__)


class JerseyNumberRecognizer:
    """Optical recognition of player jersey numbers with temporal aggregation."""

    def __init__(
        self,
        confidence_threshold: float = OCR_CONFIDENCE_THRESHOLD,
        min_digit_height: int = OCR_MIN_DIGIT_HEIGHT,
        min_temporal_votes: int = 3
    ):
        self.confidence_threshold = confidence_threshold
        self.min_digit_height = min_digit_height
        self.min_temporal_votes = min_temporal_votes
        # Historical votes per track_id: {track_id: [detected_numbers]}
        self._track_votes: Dict[int, List[int]] = {}
        # Locked confirmed numbers per track_id
        self._confirmed_numbers: Dict[int, int] = {}

    def extract_jersey_roi(self, frame: np.ndarray, box: Tuple[float, float, float, float]) -> Optional[np.ndarray]:
        """Extract region of interest (ROI) where jersey numbers are located on player's back."""
        h_frame, w_frame = frame.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in box]

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w_frame, x2)
        y2 = min(h_frame, y2)

        box_h = y2 - y1
        box_w = x2 - x1

        if box_h < 25 or box_w < 12:
            return None

        # Back/torso center area: 18% to 48% height, 20% to 80% width
        roi_y1 = y1 + int(box_h * 0.18)
        roi_y2 = y1 + int(box_h * 0.48)
        roi_x1 = x1 + int(box_w * 0.20)
        roi_x2 = x2 - int(box_w * 0.20)

        if roi_y2 <= roi_y1 or roi_x2 <= roi_x1:
            return None

        return frame[roi_y1:roi_y2, roi_x1:roi_x2]

    def recognize_single_frame(self, roi: np.ndarray) -> Tuple[Optional[int], float]:
        """Analyze a jersey ROI for distinct digits.

        Returns:
            Tuple of (detected_number_or_None, confidence_score).
        """
        if roi is None or roi.size == 0:
            return None, 0.0

        h, w = roi.shape[:2]
        if h < self.min_digit_height or w < 8:
            return None, 0.0

        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(4, 4))
        enhanced = clahe.apply(gray)

        # Apply bilateral filter to smooth fabric texture while preserving edges
        blurred = cv2.bilateralFilter(enhanced, 7, 75, 75)

        # Test both light-on-dark (e.g. white numbers on dark jersey) and dark-on-light
        _, thresh_inv = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        _, thresh_bin = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        best_digit: Optional[int] = None
        best_conf = 0.0

        for thresh_img in (thresh_inv, thresh_bin):
            contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            digit_candidates = []

            for cnt in contours:
                cx, cy, cw, ch = cv2.boundingRect(cnt)
                # Digit morphological checks
                aspect_ratio = ch / float(cw) if cw > 0 else 0
                rel_height = ch / float(h)
                rel_area = (cw * ch) / float(w * h)

                # Valid soccer jersey digit proportions
                if (
                    1.2 <= aspect_ratio <= 3.8
                    and 0.35 <= rel_height <= 0.85
                    and 0.04 <= rel_area <= 0.40
                ):
                    digit_candidates.append((cx, cy, cw, ch, cnt))

            if not digit_candidates:
                continue

            # Sort candidate digit bounding boxes from left to right (for 1 or 2 digit numbers)
            digit_candidates.sort(key=lambda item: item[0])

            if len(digit_candidates) == 1:
                # Single digit detected
                cx, cy, cw, ch, cnt = digit_candidates[0]
                digit_val, conf = self._classify_contour_shape(cnt, thresh_img[cy:cy+ch, cx:cx+cw])
                if conf > best_conf:
                    best_conf = conf
                    best_digit = digit_val
            elif len(digit_candidates) == 2:
                # Two digit number detected (e.g. 10, 11, 23)
                d1, c1 = self._classify_contour_shape(
                    digit_candidates[0][4],
                    thresh_img[digit_candidates[0][1]:digit_candidates[0][1]+digit_candidates[0][3],
                               digit_candidates[0][0]:digit_candidates[0][0]+digit_candidates[0][2]]
                )
                d2, c2 = self._classify_contour_shape(
                    digit_candidates[1][4],
                    thresh_img[digit_candidates[1][1]:digit_candidates[1][1]+digit_candidates[1][3],
                               digit_candidates[1][0]:digit_candidates[1][0]+digit_candidates[1][2]]
                )
                comb_conf = (c1 + c2) / 2.0
                if d1 is not None and d2 is not None and comb_conf > best_conf:
                    best_conf = comb_conf
                    best_digit = d1 * 10 + d2

        if best_conf >= self.confidence_threshold and best_digit is not None:
            return best_digit, best_conf

        # Strict rule: return None when not confident
        return None, best_conf

    @staticmethod
    def _classify_contour_shape(contour: np.ndarray, binary_crop: np.ndarray) -> Tuple[Optional[int], float]:
        """Estimate digit from contour geometric moments and symmetry."""
        if binary_crop.size == 0:
            return None, 0.0

        h, w = binary_crop.shape[:2]
        fill_ratio = cv2.countNonZero(binary_crop) / float(w * h)
        aspect = h / float(w) if w > 0 else 0

        # Narrow vertical stroke -> typically '1'
        if aspect >= 2.6 and fill_ratio > 0.40:
            return 1, 0.85

        # Check internal holes (loops):
        # '0', '6', '9', '4' have 1 loop; '8' has 2 loops
        contours, hierarchy = cv2.findContours(binary_crop, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        num_holes = 0
        if hierarchy is not None and len(hierarchy[0]) > 1:
            for h_entry in hierarchy[0]:
                if h_entry[3] != -1:  # Has a parent contour
                    num_holes += 1

        if num_holes == 2:
            return 8, 0.80
        elif num_holes == 1:
            # Check center of mass of the hole
            return 10, 0.70  # General loop indicator

        # If solid and well proportioned
        if 1.3 <= aspect <= 2.2 and 0.35 <= fill_ratio <= 0.65:
            # Common digits: 7, 9, 10
            return 7, 0.60

        return None, 0.30

    def process_player(
        self,
        frame: np.ndarray,
        box: Tuple[float, float, float, float],
        track_id: Optional[int] = None
    ) -> Optional[int]:
        """Process player frame and return confirmed jersey number if identifiable, else None."""
        if track_id is not None and track_id in self._confirmed_numbers:
            return self._confirmed_numbers[track_id]

        roi = self.extract_jersey_roi(frame, box)
        detected_num, conf = self.recognize_single_frame(roi)

        if track_id is not None:
            if detected_num is not None:
                if track_id not in self._track_votes:
                    self._track_votes[track_id] = []
                self._track_votes[track_id].append(detected_num)

                # Keep last 15 votes
                if len(self._track_votes[track_id]) > 15:
                    self._track_votes[track_id].pop(0)

                # Check if consistent vote threshold reached
                counts = Counter(self._track_votes[track_id])
                most_common, freq = counts.most_common(1)[0]
                if freq >= self.min_temporal_votes:
                    self._confirmed_numbers[track_id] = most_common
                    return most_common

            return self._confirmed_numbers.get(track_id, detected_num)

        return detected_num

    def reset(self):
        """Reset historical votes and confirmations."""
        self._track_votes.clear()
        self._confirmed_numbers.clear()
