"""Tactical formation classifier and pitch spatial analysis."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from src.config import PITCH_LENGTH, PITCH_WIDTH

logger = logging.getLogger(__name__)

# Standard recognized tactical formations
KNOWN_FORMATIONS = {
    (4, 3, 3): "4-3-3 Attack",
    (4, 4, 2): "4-4-2 Classic",
    (4, 2, 3, 1): "4-2-3-1 Modern",
    (3, 5, 2): "3-5-2 Wing-backs",
    (3, 4, 3): "3-4-3 Total Football",
    (5, 3, 2): "5-3-2 Low Block",
    (5, 4, 1): "5-4-1 Ultra Defensive",
    (4, 1, 4, 1): "4-1-4-1 Holding Mid",
    (4, 5, 1): "4-5-1 Compact",
}


@dataclass
class TacticalMetrics:
    """Metrics describing team structure and pitch spacing."""
    formation_name: str
    line_counts: List[int]
    compactness_width: float  # Difference between left-most and right-most outfield player
    compactness_depth: float  # Difference between deepest defender and furthest attacker
    team_centroid: Tuple[float, float]
    lines: List[List[Dict[str, Any]]]


class FormationDetector:
    """Infers tactical team formations (e.g., 4-3-3, 4-4-2) from 2D pitch coordinates."""

    def __init__(self, pitch_length: float = PITCH_LENGTH, pitch_width: float = PITCH_WIDTH):
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width

    def detect_formation(
        self,
        players: List[Dict[str, Any]],
        attacking_left_to_right: bool = True
    ) -> TacticalMetrics:
        """Infer tactical formation and spatial lines for a single team.

        Args:
            players: List of player dicts with keys 'pitch_x', 'pitch_y', and optionally 'track_id', 'jersey_number'.
            attacking_left_to_right: True if team defends X=0 and attacks toward X=105.

        Returns:
            TacticalMetrics dataclass with formation name and structural metrics.
        """
        valid_players = [p for p in players if p.get("pitch_x") is not None and p.get("pitch_y") is not None]

        if len(valid_players) < 4:
            return TacticalMetrics(
                formation_name="Analyzing Formation...",
                line_counts=[],
                compactness_width=0.0,
                compactness_depth=0.0,
                team_centroid=(50.0, 34.0),
                lines=[]
            )

        # Normalize X so team always defends x=0 and attacks toward x=105
        norm_players = []
        for p in valid_players:
            px = p["pitch_x"] if attacking_left_to_right else (self.pitch_length - p["pitch_x"])
            py = p["pitch_y"]
            norm_players.append({**p, "norm_x": px, "norm_y": py})

        # Sort players from defensive depth to offensive depth
        norm_players.sort(key=lambda p: p["norm_x"])

        # Identify goalkeeper: closest player to defense goal (norm_x < 22m and central in pitch)
        goalkeeper = None
        outfield_players = []

        if norm_players[0]["norm_x"] < 22.0:
            goalkeeper = norm_players[0]
            outfield_players = norm_players[1:]
        else:
            outfield_players = norm_players

        if not outfield_players:
            return TacticalMetrics(
                formation_name="Analyzing...",
                line_counts=[],
                compactness_width=0.0,
                compactness_depth=0.0,
                team_centroid=(norm_players[0]["norm_x"], norm_players[0]["norm_y"]),
                lines=[]
            )

        # Calculate team spatial extent
        x_coords = [p["norm_x"] for p in outfield_players]
        y_coords = [p["norm_y"] for p in outfield_players]

        depth_span = max(x_coords) - min(x_coords)
        width_span = max(y_coords) - min(y_coords)
        centroid = (float(np.mean(x_coords)), float(np.mean(y_coords)))

        # Cluster outfield players into tactical lines along the depth axis (X)
        lines = self._cluster_into_lines(outfield_players)
        line_counts = [len(line) for line in lines]

        # Match to known formations
        formation_tuple = tuple(line_counts)
        if formation_tuple in KNOWN_FORMATIONS:
            formation_name = KNOWN_FORMATIONS[formation_tuple]
        else:
            # Approximate nearest standard formation
            formation_name = self._approximate_formation(line_counts)

        return TacticalMetrics(
            formation_name=formation_name,
            line_counts=line_counts,
            compactness_width=round(width_span, 1),
            compactness_depth=round(depth_span, 1),
            team_centroid=(round(centroid[0], 1), round(centroid[1], 1)),
            lines=lines
        )

    def _cluster_into_lines(self, outfield_players: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Cluster outfield players into 3 or 4 depth lines (Defenders, Midfielders, Attackers)."""
        n = len(outfield_players)
        if n <= 3:
            return [outfield_players]

        # Sort by depth
        sorted_p = sorted(outfield_players, key=lambda p: p["norm_x"])

        # Detect natural gaps in depth
        depth_gaps = []
        for i in range(len(sorted_p) - 1):
            gap = sorted_p[i + 1]["norm_x"] - sorted_p[i]["norm_x"]
            depth_gaps.append((gap, i))

        # Sort gaps descending to find the strongest line separators
        depth_gaps.sort(key=lambda item: item[0], reverse=True)

        # Decide between 3 lines (standard) or 4 lines (e.g. 4-2-3-1)
        split_points = []
        if n >= 9:
            # Top 2 or 3 largest separation gaps
            candidate_splits = sorted([item[1] + 1 for item in depth_gaps[:2]])
            split_points = candidate_splits
        elif n >= 6:
            candidate_splits = sorted([item[1] + 1 for item in depth_gaps[:2]])
            split_points = candidate_splits
        else:
            split_points = [depth_gaps[0][1] + 1]

        # Slice players into lines
        lines: List[List[Dict[str, Any]]] = []
        prev_idx = 0
        for sp in split_points:
            lines.append(sorted_p[prev_idx:sp])
            prev_idx = sp
        lines.append(sorted_p[prev_idx:])

        # Sort players within each line by pitch width (Y) for clean left-to-right ordering
        for line in lines:
            line.sort(key=lambda p: p["norm_y"])

        return lines

    @staticmethod
    def _approximate_formation(counts: List[int]) -> str:
        """Map non-standard line counts to the closest standard formation string."""
        if not counts:
            return "4-3-3"
        total = sum(counts)
        # If standard 10 outfield players
        if total == 10:
            if len(counts) == 3:
                return f"{counts[0]}-{counts[1]}-{counts[2]}"
            elif len(counts) == 4:
                return f"{counts[0]}-{counts[1]}-{counts[2]}-{counts[3]}"

        # Fallback formation representation
        return "-".join(str(c) for c in counts)
