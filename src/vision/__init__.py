"""Computer Vision module for player detection, tracking, homography, and OCR."""

from .detector import Detection, FootballDetector
from .homography import PitchHomographyTransformer
from .number_ocr import JerseyNumberRecognizer
from .team_classifier import TeamColorClassifier
from .tracker import FootballTracker

__all__ = [
    "Detection",
    "FootballDetector",
    "FootballTracker",
    "TeamColorClassifier",
    "PitchHomographyTransformer",
    "JerseyNumberRecognizer",
]
