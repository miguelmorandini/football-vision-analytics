"""Generator for realistic demo match telemetry dataset."""

import json
import math
from pathlib import Path

OUT_FILE = Path("data/demo_matches/match_demo.json")
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Team A (Man City - 4-3-3 attacking left to right)
TEAM_A_ROSTER = [
    {"track_id": 1, "number": 31, "name": "Ederson", "role": "GK", "base_x": 6.5, "base_y": 34.0},
    {"track_id": 2, "number": 2, "name": "Walker", "role": "RB", "base_x": 26.0, "base_y": 12.0},
    {"track_id": 3, "number": 3, "name": "Dias", "role": "CB", "base_x": 23.0, "base_y": 27.0},
    {"track_id": 4, "number": 25, "name": "Akanji", "role": "CB", "base_x": 23.0, "base_y": 41.0},
    {"track_id": 5, "number": 24, "name": "Gvardiol", "role": "LB", "base_x": 27.0, "base_y": 57.0},
    {"track_id": 6, "number": 16, "name": "Rodri", "role": "DM", "base_x": 42.0, "base_y": 34.0},
    {"track_id": 7, "number": 17, "name": "De Bruyne", "role": "CM", "base_x": 56.0, "base_y": 23.0},
    {"track_id": 8, "number": 20, "name": "Bernardo", "role": "CM", "base_x": 55.0, "base_y": 46.0},
    {"track_id": 9, "number": 20, "name": "Bernardo", "role": "RW", "base_x": 72.0, "base_y": 14.0},
    {"track_id": 10, "number": 9, "name": "Haaland", "role": "ST", "base_x": 76.0, "base_y": 34.0},
    {"track_id": 11, "number": 47, "name": "Foden", "role": "LW", "base_x": 71.0, "base_y": 54.0},
]

# Team B (Real Madrid - 4-4-2 mid-block defending right to left)
TEAM_B_ROSTER = [
    {"track_id": 12, "number": 1, "name": "Courtois", "role": "GK", "base_x": 98.5, "base_y": 34.0},
    {"track_id": 13, "number": 2, "name": "Carvajal", "role": "RB", "base_x": 78.0, "base_y": 15.0},
    {"track_id": 14, "number": 3, "name": "Militao", "role": "CB", "base_x": 81.0, "base_y": 28.0},
    {"track_id": 15, "number": 22, "name": "Rudiger", "role": "CB", "base_x": 81.0, "base_y": 40.0},
    {"track_id": 16, "number": 23, "name": "Mendy", "role": "LB", "base_x": 79.0, "base_y": 53.0},
    {"track_id": 17, "number": 15, "name": "Valverde", "role": "RM", "base_x": 64.0, "base_y": 18.0},
    {"track_id": 18, "number": 8, "name": "Kroos", "role": "CM", "base_x": 66.0, "base_y": 30.0},
    {"track_id": 19, "number": 12, "name": "Camavinga", "role": "CM", "base_x": 66.0, "base_y": 40.0},
    {"track_id": 20, "number": 5, "name": "Bellingham", "role": "LM", "base_x": 63.0, "base_y": 50.0},
    {"track_id": 21, "number": 11, "name": "Rodrygo", "role": "ST", "base_x": 51.0, "base_y": 29.0},
    {"track_id": 22, "number": 7, "name": "Vinicius Jr", "role": "ST", "base_x": 50.0, "base_y": 42.0},
]

# Notice: some players will have None as jersey number (simulating unreadable backs, as requested by user!)
TEAM_A_UNREADABLE = {2, 5}   # Walker and Gvardiol facing front
TEAM_B_UNREADABLE = {13, 16} # Carvajal and Mendy facing front

TOTAL_FRAMES = 80
timeline = []

for f in range(TOTAL_FRAMES):
    t = f / 15.0  # Time in seconds
    players = []

    # Team A motion (advancing possession phase)
    shift_x = 4.0 * math.sin(t * 0.5)
    for p in TEAM_A_ROSTER:
        # Subtle organic player movement
        dx = shift_x + 1.2 * math.sin(t + p["track_id"])
        dy = 1.0 * math.cos(t * 0.8 + p["track_id"])
        px = round(max(2.0, min(103.0, p["base_x"] + dx)), 2)
        py = round(max(3.0, min(65.0, p["base_y"] + dy)), 2)

        # Apply strict user rule: None if jersey number not legible
        num = None if p["track_id"] in TEAM_A_UNREADABLE else p["number"]

        players.append({
            "track_id": p["track_id"],
            "team_id": "team_a",
            "name": p["name"],
            "role": p["role"],
            "pitch_x": px,
            "pitch_y": py,
            "jersey_number": num,
            "confidence": 0.94
        })

    # Team B motion (sliding defensive block)
    for p in TEAM_B_ROSTER:
        dx = (shift_x * 0.7) + 0.9 * math.cos(t * 0.9 + p["track_id"])
        dy = 1.1 * math.sin(t * 0.7 + p["track_id"])
        px = round(max(2.0, min(103.0, p["base_x"] + dx)), 2)
        py = round(max(3.0, min(65.0, p["base_y"] + dy)), 2)

        num = None if p["track_id"] in TEAM_B_UNREADABLE else p["number"]

        players.append({
            "track_id": p["track_id"],
            "team_id": "team_b",
            "name": p["name"],
            "role": p["role"],
            "pitch_x": px,
            "pitch_y": py,
            "jersey_number": num,
            "confidence": 0.92
        })

    # Ball motion: circulating between De Bruyne (track 7) and Bernardo (track 8)
    ball_x = round(55.5 + 4.0 * math.sin(t * 0.8), 2)
    ball_y = round(34.0 + 8.0 * math.cos(t * 0.8), 2)

    frame_entry = {
        "frame_idx": f,
        "timestamp_sec": round(f / 25.0, 2),
        "players": players,
        "ball": {"pitch_x": ball_x, "pitch_y": ball_y},
        "team_a": {
            "formation": "4-3-3 Attack",
            "line_counts": [4, 3, 3],
            "compactness_width": 46.5,
            "compactness_depth": 53.0,
            "centroid": [47.2, 33.8]
        },
        "team_b": {
            "formation": "4-4-2 Classic",
            "line_counts": [4, 4, 2],
            "compactness_width": 38.0,
            "compactness_depth": 32.5,
            "centroid": [71.5, 34.2]
        }
    }
    timeline.append(frame_entry)

demo_dataset = {
    "match_id": "ucl_final_demo",
    "match_title": "Manchester City vs Real Madrid - Tactical Broadcast",
    "competition": "UEFA Champions League",
    "teams": {
        "team_a": {"name": "Manchester City", "formation": "4-3-3 Attack", "color": "#1E40AF"},
        "team_b": {"name": "Real Madrid", "formation": "4-4-2 Classic", "color": "#DC2626"}
    },
    "total_frames": TOTAL_FRAMES,
    "fps": 25.0,
    "timeline": timeline
}

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(demo_dataset, f, indent=2)

print(f"Generated {TOTAL_FRAMES} frames of match telemetry in {OUT_FILE}")
