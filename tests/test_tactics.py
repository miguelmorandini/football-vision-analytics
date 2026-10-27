"""Tests for Tactical Formation Detector and Pitch Homography."""

import unittest
from src.tactics.formation_detector import FormationDetector
from src.vision.homography import PitchHomographyTransformer


class TestTacticsAndVision(unittest.TestCase):
    """Test suite for tactics and pitch transformation."""

    def setUp(self):
        self.detector = FormationDetector()
        self.transformer = PitchHomographyTransformer()

    def test_detect_433_formation(self):
        # 1 Goalkeeper + 4 Defenders + 3 Midfielders + 3 Attackers
        players_433 = [
            {"pitch_x": 5.0, "pitch_y": 34.0, "track_id": 1},   # GK
            # 4 Defenders
            {"pitch_x": 20.0, "pitch_y": 10.0, "track_id": 2},
            {"pitch_x": 22.0, "pitch_y": 25.0, "track_id": 3},
            {"pitch_x": 22.0, "pitch_y": 43.0, "track_id": 4},
            {"pitch_x": 20.0, "pitch_y": 58.0, "track_id": 5},
            # 3 Midfielders
            {"pitch_x": 45.0, "pitch_y": 20.0, "track_id": 6},
            {"pitch_x": 48.0, "pitch_y": 34.0, "track_id": 7},
            {"pitch_x": 45.0, "pitch_y": 48.0, "track_id": 8},
            # 3 Attackers
            {"pitch_x": 75.0, "pitch_y": 15.0, "track_id": 9},
            {"pitch_x": 80.0, "pitch_y": 34.0, "track_id": 10},
            {"pitch_x": 75.0, "pitch_y": 53.0, "track_id": 11},
        ]
        metrics = self.detector.detect_formation(players_433, attacking_left_to_right=True)
        self.assertEqual(metrics.line_counts, [4, 3, 3])
        self.assertIn("4-3-3", metrics.formation_name)

    def test_detect_442_formation(self):
        # 1 Goalkeeper + 4 Defenders + 4 Midfielders + 2 Attackers
        players_442 = [
            {"pitch_x": 6.0, "pitch_y": 34.0, "track_id": 1},   # GK
            # 4 Defenders
            {"pitch_x": 22.0, "pitch_y": 12.0, "track_id": 2},
            {"pitch_x": 24.0, "pitch_y": 26.0, "track_id": 3},
            {"pitch_x": 24.0, "pitch_y": 42.0, "track_id": 4},
            {"pitch_x": 22.0, "pitch_y": 56.0, "track_id": 5},
            # 4 Midfielders
            {"pitch_x": 50.0, "pitch_y": 10.0, "track_id": 6},
            {"pitch_x": 52.0, "pitch_y": 28.0, "track_id": 7},
            {"pitch_x": 52.0, "pitch_y": 40.0, "track_id": 8},
            {"pitch_x": 50.0, "pitch_y": 58.0, "track_id": 9},
            # 2 Attackers
            {"pitch_x": 80.0, "pitch_y": 30.0, "track_id": 10},
            {"pitch_x": 80.0, "pitch_y": 38.0, "track_id": 11},
        ]
        metrics = self.detector.detect_formation(players_442, attacking_left_to_right=True)
        self.assertEqual(metrics.line_counts, [4, 4, 2])
        self.assertIn("4-4-2", metrics.formation_name)

    def test_pitch_homography_bounds(self):
        # Test boundary clamping
        px, py = self.transformer.transform_point(640, 360)
        self.assertGreaterEqual(px, 0.0)
        self.assertLessEqual(px, 105.0)
        self.assertGreaterEqual(py, 0.0)
        self.assertLessEqual(py, 68.0)


if __name__ == "__main__":
    unittest.main()
