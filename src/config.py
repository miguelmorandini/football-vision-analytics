"""Configuration settings and constants for Football Vision Analytics."""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DEMO_DIR = DATA_DIR / "demo_matches"
VIDEOS_DIR = DATA_DIR / "videos"

# Ensure directories exist
DEMO_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Standard Football Pitch Dimensions (in meters according to FIFA guidelines)
PITCH_LENGTH = 105.0  # X-axis: 0 (Team A Goal) to 105 (Team B Goal)
PITCH_WIDTH = 68.0    # Y-axis: 0 (Touchline top) to 68 (Touchline bottom)

# Detection & Tracking Config
DEFAULT_DETECTION_CONF = 0.35
DEFAULT_TRACKER_THRESHOLD = 0.4
DEFAULT_MODEL_NAME = "yolov8n.pt"

# COCO Class IDs
COCO_PERSON_CLASS_ID = 0
COCO_SPORTS_BALL_CLASS_ID = 32

# OCR Settings
OCR_CONFIDENCE_THRESHOLD = 0.55
OCR_MIN_DIGIT_HEIGHT = 12

# Team Colors (Hex & RGB for tactical board)
TEAM_COLORS = {
    "team_a": {
        "name": "Team Blue",
        "primary_hex": "#1E40AF",   # Deep blue
        "secondary_hex": "#93C5FD",
        "text_hex": "#FFFFFF"
    },
    "team_b": {
        "name": "Team Red",
        "primary_hex": "#DC2626",   # Bright red
        "secondary_hex": "#FCA5A5",
        "text_hex": "#FFFFFF"
    },
    "goalkeeper": {
        "name": "Goalkeeper",
        "primary_hex": "#F59E0B",   # Amber / Yellow
        "secondary_hex": "#FDE68A",
        "text_hex": "#000000"
    },
    "referee": {
        "name": "Referee",
        "primary_hex": "#10B981",   # Emerald green / neon
        "secondary_hex": "#A7F3D0",
        "text_hex": "#000000"
    }
}

# ScoreBat API
SCOREBAT_API_URL = "https://www.scorebat.com/video-api/v1/"
