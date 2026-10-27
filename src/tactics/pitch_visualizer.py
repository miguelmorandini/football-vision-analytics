"""2D Tactical Football Pitch Visualizer.

Renders high-quality 2D radar minimap boards with players, lines, formations,
and ball positions using FIFA regulation field geometry.
"""

from __future__ import annotations

import io
from typing import Any, Dict, List, Optional

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from src.config import PITCH_LENGTH, PITCH_WIDTH, TEAM_COLORS
from src.tactics.formation_detector import TacticalMetrics


class PitchVisualizer:
    """Renderer for 2D tactical football pitch boards."""

    def __init__(
        self,
        pitch_length: float = PITCH_LENGTH,
        pitch_width: float = PITCH_WIDTH,
        theme: str = "dark"
    ):
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.theme = theme

    def render(
        self,
        players: List[Dict[str, Any]],
        ball: Optional[Dict[str, Any]] = None,
        metrics_a: Optional[TacticalMetrics] = None,
        metrics_b: Optional[TacticalMetrics] = None,
        show_tactical_lines: bool = True
    ) -> plt.Figure:
        """Create a Matplotlib figure of the 2D pitch with players and formations."""
        # Visual color palette
        if self.theme == "dark":
            bg_color = "#0F172A"       # Dark slate blue
            pitch_color = "#1E293B"    # Navy pitch
            line_color = "#64748B"     # Slate lines
            text_color = "#F8FAFC"
        else:
            bg_color = "#1E3A2F"
            pitch_color = "#2D5A46"    # Grass green
            line_color = "#E2E8F0"
            text_color = "#FFFFFF"

        fig, ax = plt.subplots(figsize=(10, 6.5), facecolor=bg_color)
        ax.set_facecolor(pitch_color)

        # Plot Pitch Geometry
        self._draw_pitch_geometry(ax, line_color)

        # Draw Tactical Interconnection Lines
        if show_tactical_lines:
            if metrics_a and metrics_a.lines:
                self._draw_team_lines(ax, metrics_a.lines, color="#3B82F6", alpha=0.4)
            if metrics_b and metrics_b.lines:
                self._draw_team_lines(ax, metrics_b.lines, color="#EF4444", alpha=0.4)

        # Draw Players
        for p in players:
            px = p.get("pitch_x")
            py = p.get("pitch_y")
            if px is None or py is None:
                continue

            team_id = p.get("team_id", "team_a")
            color_cfg = TEAM_COLORS.get(team_id, TEAM_COLORS["team_a"])
            primary_color = color_cfg["primary_hex"]
            jersey_number = p.get("jersey_number")
            track_id = p.get("track_id")

            # Player outer halo
            halo = patches.Circle(
                (px, py), radius=2.2,
                facecolor=primary_color, edgecolor=color_cfg["secondary_hex"],
                linewidth=1.8, zorder=5, alpha=0.95
            )
            ax.add_patch(halo)

            # Display jersey number if detected by OCR; if not, show track ID or clean dot
            label_text = ""
            if jersey_number is not None:
                label_text = str(jersey_number)
            elif track_id is not None:
                label_text = str(track_id)

            if label_text:
                ax.text(
                    px, py, label_text,
                    color=color_cfg["text_hex"],
                    fontsize=8, fontweight="bold",
                    ha="center", va="center", zorder=6
                )

        # Draw Ball
        if ball and ball.get("pitch_x") is not None and ball.get("pitch_y") is not None:
            bx, by = ball["pitch_x"], ball["pitch_y"]
            # Ball beacon ring
            beacon = patches.Circle((bx, by), radius=2.5, facecolor="#FACC15", alpha=0.3, zorder=7)
            ax.add_patch(beacon)
            ball_dot = patches.Circle((bx, by), radius=1.2, facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2, zorder=8)
            ax.add_patch(ball_dot)

        # Header titles & formation badges
        title_a = metrics_a.formation_name if metrics_a else "Team A"
        title_b = metrics_b.formation_name if metrics_b else "Team B"

        ax.text(
            15, -4.0, f"◀ {title_a}",
            color="#60A5FA", fontsize=11, fontweight="bold", ha="left"
        )
        ax.text(
            self.pitch_length - 15, -4.0, f"{title_b} ▶",
            color="#F87171", fontsize=11, fontweight="bold", ha="right"
        )

        ax.set_xlim(-5, self.pitch_length + 5)
        ax.set_ylim(-6, self.pitch_width + 5)
        ax.axis("off")
        plt.tight_layout()

        return fig

    def _draw_pitch_geometry(self, ax: plt.Axes, color: str):
        """Draw accurate pitch markings according to FIFA regulation sizes."""
        l = self.pitch_length
        w = self.pitch_width

        # Outer pitch boundary
        ax.add_patch(patches.Rectangle((0, 0), l, w, fill=False, edgecolor=color, linewidth=1.5))

        # Halfway line
        ax.plot([l / 2, l / 2], [0, w], color=color, linewidth=1.2)

        # Center circle (9.15m radius) & center spot
        center_circle = patches.Circle((l / 2, w / 2), 9.15, fill=False, edgecolor=color, linewidth=1.2)
        center_spot = patches.Circle((l / 2, w / 2), 0.5, facecolor=color)
        ax.add_patch(center_circle)
        ax.add_patch(center_spot)

        # Penalty areas (16.5m depth, 40.32m width centered)
        pen_w = 40.32
        pen_y = (w - pen_w) / 2
        ax.add_patch(patches.Rectangle((0, pen_y), 16.5, pen_w, fill=False, edgecolor=color, linewidth=1.2))
        ax.add_patch(patches.Rectangle((l - 16.5, pen_y), 16.5, pen_w, fill=False, edgecolor=color, linewidth=1.2))

        # Goal areas (5.5m depth, 18.32m width centered)
        goal_w = 18.32
        goal_y = (w - goal_w) / 2
        ax.add_patch(patches.Rectangle((0, goal_y), 5.5, goal_w, fill=False, edgecolor=color, linewidth=1.0))
        ax.add_patch(patches.Rectangle((l - 5.5, goal_y), 5.5, goal_w, fill=False, edgecolor=color, linewidth=1.0))

        # Penalty spots (11m from goal line)
        ax.add_patch(patches.Circle((11.0, w / 2), 0.4, facecolor=color))
        ax.add_patch(patches.Circle((l - 11.0, w / 2), 0.4, facecolor=color))

        # Penalty arcs (outside 16.5m box)
        arc_left = patches.Arc((11.0, w / 2), 18.3, 18.3, angle=0, theta1=307, theta2=53, edgecolor=color, linewidth=1.0)
        arc_right = patches.Arc((l - 11.0, w / 2), 18.3, 18.3, angle=0, theta1=127, theta2=233, edgecolor=color, linewidth=1.0)
        ax.add_patch(arc_left)
        ax.add_patch(arc_right)

    @staticmethod
    def _draw_team_lines(ax: plt.Axes, lines: List[List[Dict[str, Any]]], color: str, alpha: float):
        """Connect players within the same tactical line with dashed tactical links."""
        for line in lines:
            if len(line) < 2:
                continue
            xs = [p.get("pitch_x") for p in line if p.get("pitch_x") is not None]
            ys = [p.get("pitch_y") for p in line if p.get("pitch_y") is not None]
            if len(xs) >= 2:
                ax.plot(xs, ys, color=color, linestyle="--", linewidth=1.4, alpha=alpha, zorder=4)
