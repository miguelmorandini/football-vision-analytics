"""Client for the ScoreBat Free Football Video API.

Provides real-time access to official match highlights, embedded video feeds,
and metadata for matches from major soccer leagues around the world.
"""

from __future__ import annotations

import json
import logging
import urllib.request
from typing import Any, Dict, List, Optional

from src.config import SCOREBAT_API_URL

logger = logging.getLogger(__name__)


# Fallback sample matches in case the external API is offline or unreachable
FALLBACK_MATCHES: List[Dict[str, Any]] = [
    {
        "title": "Manchester City - Arsenal",
        "competition": {"name": "ENGLAND: Premier League", "id": 15},
        "date": "2026-10-25T16:30:00+0000",
        "thumbnail": "https://www.scorebat.com/og/m/og111111.jpeg",
        "side1": {"name": "Manchester City", "url": "manchester-city"},
        "side2": {"name": "Arsenal", "url": "arsenal"},
        "embed": "<iframe src='https://www.youtube.com/embed/dQw4w9WgXcQ' frameborder='0' width='100%' height='400' allowfullscreen></iframe>",
        "videos": [
            {"title": "Highlights", "embed": "<iframe src='https://www.youtube.com/embed/dQw4w9WgXcQ' frameborder='0' width='100%' height='400' allowfullscreen></iframe>"}
        ]
    },
    {
        "title": "Real Madrid - Barcelona",
        "competition": {"name": "SPAIN: La Liga", "id": 14},
        "date": "2026-10-24T20:00:00+0000",
        "thumbnail": "https://www.scorebat.com/og/m/og222222.jpeg",
        "side1": {"name": "Real Madrid", "url": "real-madrid"},
        "side2": {"name": "Barcelona", "url": "barcelona"},
        "embed": "<iframe src='https://www.youtube.com/embed/dQw4w9WgXcQ' frameborder='0' width='100%' height='400' allowfullscreen></iframe>",
        "videos": [
            {"title": "Highlights", "embed": "<iframe src='https://www.youtube.com/embed/dQw4w9WgXcQ' frameborder='0' width='100%' height='400' allowfullscreen></iframe>"}
        ]
    },
    {
        "title": "Bayern Munich - Borussia Dortmund",
        "competition": {"name": "GERMANY: Bundesliga", "id": 17},
        "date": "2026-10-24T17:30:00+0000",
        "thumbnail": "https://www.scorebat.com/og/m/og333333.jpeg",
        "side1": {"name": "Bayern Munich", "url": "bayern-munich"},
        "side2": {"name": "Borussia Dortmund", "url": "borussia-dortmund"},
        "embed": "<iframe src='https://www.youtube.com/embed/dQw4w9WgXcQ' frameborder='0' width='100%' height='400' allowfullscreen></iframe>",
        "videos": [
            {"title": "Highlights", "embed": "<iframe src='https://www.youtube.com/embed/dQw4w9WgXcQ' frameborder='0' width='100%' height='400' allowfullscreen></iframe>"}
        ]
    }
]


class ScoreBatClient:
    """Client for fetching and querying ScoreBat football highlight videos."""

    def __init__(self, api_url: str = SCOREBAT_API_URL, timeout_seconds: int = 8):
        self.api_url = api_url
        self.timeout = timeout_seconds
        self._cached_matches: Optional[List[Dict[str, Any]]] = None

    def get_matches(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetch latest matches from ScoreBat API feed with fallback support.

        Args:
            force_refresh: If True, bypass internal memory cache.

        Returns:
            List of match dictionaries containing title, competition, embed code, and teams.
        """
        if self._cached_matches is not None and not force_refresh:
            return self._cached_matches

        req = urllib.request.Request(
            self.api_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FootballVision/1.0"}
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    if isinstance(data, list) and len(data) > 0:
                        self._cached_matches = data
                        logger.info(f"Loaded {len(data)} matches from ScoreBat API.")
                        return data
        except Exception as e:
            logger.warning(f"Could not reach ScoreBat API: {e}. Using offline fallback dataset.")

        self._cached_matches = FALLBACK_MATCHES
        return FALLBACK_MATCHES

    def search_matches(
        self,
        query: Optional[str] = None,
        competition: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Filter matches by team/title query or competition name.

        Args:
            query: Text substring to match against title or team names.
            competition: Text substring to match against competition name.
            limit: Maximum number of matches to return.

        Returns:
            Filtered list of match items.
        """
        matches = self.get_matches()
        filtered: List[Dict[str, Any]] = []

        q_lower = query.lower().strip() if query else ""
        c_lower = competition.lower().strip() if competition else ""

        for m in matches:
            title = m.get("title", "")
            comp_obj = m.get("competition")
            comp_name = comp_obj.get("name", "") if isinstance(comp_obj, dict) else str(comp_obj or "")

            match_q = True
            if q_lower:
                match_q = (
                    q_lower in title.lower()
                    or (m.get("side1", {}).get("name", "").lower().find(q_lower) >= 0)
                    or (m.get("side2", {}).get("name", "").lower().find(q_lower) >= 0)
                )

            match_c = True
            if c_lower:
                match_c = c_lower in comp_name.lower()

            if match_q and match_c:
                filtered.append(m)
                if len(filtered) >= limit:
                    break

        return filtered

    def get_competitions(self) -> List[str]:
        """Get unique list of competition names from available matches."""
        matches = self.get_matches()
        comps = set()
        for m in matches:
            comp_obj = m.get("competition")
            name = comp_obj.get("name") if isinstance(comp_obj, dict) else str(comp_obj or "")
            if name:
                comps.add(name)
        return sorted(list(comps))
