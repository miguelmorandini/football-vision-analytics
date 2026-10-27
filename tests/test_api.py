"""Tests for ScoreBat API Client."""

import unittest
from src.api.scorebat import ScoreBatClient


class TestScoreBatClient(unittest.TestCase):
    """Test suite for the ScoreBat API integration."""

    def setUp(self):
        self.client = ScoreBatClient(timeout_seconds=5)

    def test_get_matches_returns_list(self):
        matches = self.client.get_matches()
        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)
        self.assertIn("title", matches[0])

    def test_search_matches_query(self):
        # Even if offline fallback or live, searching should return filtered results or empty
        matches = self.client.search_matches(query="Real", limit=5)
        self.assertIsInstance(matches, list)
        for m in matches:
            title = m.get("title", "")
            side1 = m.get("side1", {}).get("name", "")
            side2 = m.get("side2", {}).get("name", "")
            combined = f"{title} {side1} {side2}".lower()
            self.assertIn("real", combined)

    def test_get_competitions(self):
        comps = self.client.get_competitions()
        self.assertIsInstance(comps, list)
        self.assertGreater(len(comps), 0)


if __name__ == "__main__":
    unittest.main()
