"""Generate multiple ad-free broadcast tactical match videos and synchronized telemetry."""

import base64
import json
import math
from pathlib import Path
import cv2
import numpy as np
import av

OUT_DIR = Path("data/videos")
OUT_DIR.mkdir(parents=True, exist_ok=True)
TELEMETRY_DIR = Path("data/demo_matches")
TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1280, 720
FPS = 25
DURATION_SEC = 8
TOTAL_FRAMES = FPS * DURATION_SEC


def generate_match(
    filename: str,
    title: str,
    competition: str,
    team_a_name: str,
    team_a_formation: str,
    team_a_color: tuple,
    team_a_roster: list,
    team_b_name: str,
    team_b_formation: str,
    team_b_color: tuple,
    team_b_roster: list,
    ball_traj_func
):
    temp_avi = OUT_DIR / f"temp_{filename}.avi"
    final_mp4 = OUT_DIR / f"{filename}.mp4"

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(str(temp_avi), fourcc, FPS, (WIDTH, HEIGHT))

    timeline = []

    for f in range(TOTAL_FRAMES):
        t = f / float(FPS)
        frame = np.full((HEIGHT, WIDTH, 3), (35, 78, 48), dtype=np.uint8)

        # Draw pitch markings in broadcast perspective
        cv2.line(frame, (120, 240), (1160, 240), (200, 220, 200), 2)
        cv2.line(frame, (40, 680), (1240, 680), (200, 220, 200), 3)
        cv2.line(frame, (640, 240), (640, 680), (200, 220, 200), 2)
        cv2.circle(frame, (640, 460), 85, (200, 220, 200), 2)
        # Center spot
        cv2.circle(frame, (640, 460), 5, (200, 220, 200), -1)

        # Penalty boxes
        cv2.rectangle(frame, (120, 310), (280, 610), (200, 220, 200), 2)
        cv2.rectangle(frame, (1000, 310), (1160, 610), (200, 220, 200), 2)

        players_frame = []

        # Render Team A
        for p in team_a_roster:
            dx = 15.0 * math.sin(t * 0.8 + p["track_id"])
            dy = 8.0 * math.cos(t * 0.6 + p["track_id"])
            sx = int(p["cam_x"] + dx)
            sy = int(p["cam_y"] + dy)

            # Feet contact point mapped to 2D pitch
            pitch_x = round(max(2.0, min(103.0, (sx - 40) / (1200) * 105.0)), 1)
            pitch_y = round(max(2.0, min(66.0, (sy - 240) / (440) * 68.0)), 1)

            # Draw player bounding box
            cv2.rectangle(frame, (sx - 16, sy - 42), (sx + 16, sy + 6), team_a_color, 2)
            cv2.circle(frame, (sx, sy - 18), 11, team_a_color, -1)

            num_str = str(p["number"]) if p["number"] is not None else ""
            if num_str:
                cv2.putText(frame, num_str, (sx - 7, sy - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
                label = f"#{num_str}"
            else:
                label = f"ID {p['track_id']}"

            cv2.putText(frame, label, (sx - 16, sy - 46), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)

            players_frame.append({
                "track_id": p["track_id"],
                "team_id": "team_a",
                "name": p["name"],
                "role": p["role"],
                "pitch_x": pitch_x,
                "pitch_y": pitch_y,
                "jersey_number": p["number"]
            })

        # Render Team B
        for p in team_b_roster:
            dx = 12.0 * math.cos(t * 0.8 + p["track_id"])
            dy = 7.0 * math.sin(t * 0.7 + p["track_id"])
            sx = int(p["cam_x"] + dx)
            sy = int(p["cam_y"] + dy)

            pitch_x = round(max(2.0, min(103.0, (sx - 40) / (1200) * 105.0)), 1)
            pitch_y = round(max(2.0, min(66.0, (sy - 240) / (440) * 68.0)), 1)

            cv2.rectangle(frame, (sx - 16, sy - 42), (sx + 16, sy + 6), team_b_color, 2)
            cv2.circle(frame, (sx, sy - 18), 11, team_b_color, -1)

            num_str = str(p["number"]) if p["number"] is not None else ""
            if num_str:
                cv2.putText(frame, num_str, (sx - 7, sy - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
                label = f"#{num_str}"
            else:
                label = f"ID {p['track_id']}"

            cv2.putText(frame, label, (sx - 16, sy - 46), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)

            players_frame.append({
                "track_id": p["track_id"],
                "team_id": "team_b",
                "name": p["name"],
                "role": p["role"],
                "pitch_x": pitch_x,
                "pitch_y": pitch_y,
                "jersey_number": p["number"]
            })

        # Render Ball
        bx, by = ball_traj_func(t)
        cv2.circle(frame, (int(bx), int(by)), 6, (0, 255, 255), -1)
        ball_pitch_x = round(max(2.0, min(103.0, (bx - 40) / (1200) * 105.0)), 1)
        ball_pitch_y = round(max(2.0, min(66.0, (by - 240) / (440) * 68.0)), 1)

        out.write(frame)

        timeline.append({
            "frame_idx": f,
            "timestamp": round(t, 2),
            "players": players_frame,
            "ball": {"pitch_x": ball_pitch_x, "pitch_y": ball_pitch_y}
        })

    out.release()

    # Transcode to clean web-compatible H.264 using PyAV
    input_c = av.open(str(temp_avi))
    output_c = av.open(str(final_mp4), mode='w')
    in_stream = input_c.streams.video[0]
    out_stream = output_c.add_stream('libx264', rate=FPS)
    out_stream.width = WIDTH
    out_stream.height = HEIGHT
    out_stream.pix_fmt = 'yuv420p'

    for frame in input_c.decode(in_stream):
        packet = out_stream.encode(frame)
        if packet:
            output_c.mux(packet)
    for packet in out_stream.encode(None):
        output_c.mux(packet)

    input_c.close()
    output_c.close()

    temp_avi.unlink(missing_ok=True)

    # Save Telemetry JSON
    telemetry_data = {
        "title": title,
        "competition": competition,
        "team_a": {"name": team_a_name, "formation": team_a_formation},
        "team_b": {"name": team_b_name, "formation": team_b_formation},
        "fps": FPS,
        "duration": DURATION_SEC,
        "total_frames": TOTAL_FRAMES,
        "timeline": timeline
    }
    with open(TELEMETRY_DIR / f"{filename}.json", "w", encoding="utf-8") as f:
        json.dump(telemetry_data, f, indent=2)

    print(f"Generated {final_mp4} ({final_mp4.stat().st_size / 1024:.1f} KB) and telemetry successfully!")


# --- MATCH 1: Man City vs Real Madrid ---
roster_city = [
    {"track_id": 1, "number": 31, "name": "Ederson", "role": "GK", "cam_x": 160, "cam_y": 460},
    {"track_id": 2, "number": None, "name": "Walker", "role": "RB", "cam_x": 340, "cam_y": 320},  # Unreadable
    {"track_id": 3, "number": 3, "name": "Dias", "role": "CB", "cam_x": 300, "cam_y": 410},
    {"track_id": 4, "number": 25, "name": "Akanji", "role": "CB", "cam_x": 300, "cam_y": 510},
    {"track_id": 5, "number": None, "name": "Gvardiol", "role": "LB", "cam_x": 340, "cam_y": 600}, # Unreadable
    {"track_id": 6, "number": 16, "name": "Rodri", "role": "DM", "cam_x": 480, "cam_y": 460},
    {"track_id": 7, "number": 17, "name": "De Bruyne", "role": "CM", "cam_x": 580, "cam_y": 370},
    {"track_id": 8, "number": 20, "name": "Bernardo", "role": "CM", "cam_x": 580, "cam_y": 550},
    {"track_id": 9, "number": 47, "name": "Foden", "role": "RW", "cam_x": 760, "cam_y": 330},
    {"track_id": 10, "number": 9, "name": "Haaland", "role": "ST", "cam_x": 800, "cam_y": 460},
    {"track_id": 11, "number": 10, "name": "Grealish", "role": "LW", "cam_x": 760, "cam_y": 590},
]
roster_real = [
    {"track_id": 12, "number": 1, "name": "Courtois", "role": "GK", "cam_x": 1120, "cam_y": 460},
    {"track_id": 13, "number": None, "name": "Carvajal", "role": "RB", "cam_x": 960, "cam_y": 330}, # Unreadable
    {"track_id": 14, "number": 3, "name": "Militao", "role": "CB", "cam_x": 980, "cam_y": 410},
    {"track_id": 15, "number": 22, "name": "Rudiger", "role": "CB", "cam_x": 980, "cam_y": 510},
    {"track_id": 16, "number": None, "name": "Mendy", "role": "LB", "cam_x": 960, "cam_y": 600}, # Unreadable
    {"track_id": 17, "number": 15, "name": "Valverde", "role": "RM", "cam_x": 820, "cam_y": 350},
    {"track_id": 18, "number": 8, "name": "Kroos", "role": "CM", "cam_x": 810, "cam_y": 420},
    {"track_id": 19, "number": 12, "name": "Camavinga", "role": "CM", "cam_x": 810, "cam_y": 500},
    {"track_id": 20, "number": 5, "name": "Bellingham", "role": "LM", "cam_x": 820, "cam_y": 570},
    {"track_id": 21, "number": 7, "name": "Vinicius Jr", "role": "ST", "cam_x": 670, "cam_y": 420},
    {"track_id": 22, "number": 11, "name": "Rodrygo", "role": "ST", "cam_x": 670, "cam_y": 500},
]

generate_match(
    filename="match_ucl_city_real",
    title="Manchester City vs Real Madrid",
    competition="UEFA Champions League",
    team_a_name="Manchester City",
    team_a_formation="4-3-3 Attack",
    team_a_color=(220, 80, 30),  # Blue in BGR
    team_a_roster=roster_city,
    team_b_name="Real Madrid",
    team_b_formation="4-4-2 Classic",
    team_b_color=(40, 40, 220),  # Red in BGR
    team_b_roster=roster_real,
    ball_traj_func=lambda t: (580 + 60 * math.sin(t * 1.5), 440 + 40 * math.cos(t * 1.5))
)


# --- MATCH 2: Arsenal vs Liverpool ---
roster_arsenal = [
    {"track_id": 1, "number": 22, "name": "Raya", "role": "GK", "cam_x": 160, "cam_y": 460},
    {"track_id": 2, "number": 4, "name": "White", "role": "RB", "cam_x": 330, "cam_y": 320},
    {"track_id": 3, "number": 2, "name": "Saliba", "role": "CB", "cam_x": 290, "cam_y": 410},
    {"track_id": 4, "number": 6, "name": "Gabriel", "role": "CB", "cam_x": 290, "cam_y": 510},
    {"track_id": 5, "number": None, "name": "Timber", "role": "LB", "cam_x": 330, "cam_y": 600},
    {"track_id": 6, "number": 41, "name": "Rice", "role": "DM", "cam_x": 460, "cam_y": 420},
    {"track_id": 7, "number": 5, "name": "Partey", "role": "DM", "cam_x": 460, "cam_y": 500},
    {"track_id": 8, "number": 8, "name": "Odegaard", "role": "AM", "cam_x": 620, "cam_y": 460},
    {"track_id": 9, "number": 7, "name": "Saka", "role": "RW", "cam_x": 780, "cam_y": 330},
    {"track_id": 10, "number": 29, "name": "Havertz", "role": "ST", "cam_x": 820, "cam_y": 460},
    {"track_id": 11, "number": 11, "name": "Martinelli", "role": "LW", "cam_x": 780, "cam_y": 590},
]
roster_liverpool = [
    {"track_id": 12, "number": 1, "name": "Alisson", "role": "GK", "cam_x": 1120, "cam_y": 460},
    {"track_id": 13, "number": 66, "name": "Trent", "role": "RB", "cam_x": 950, "cam_y": 320},
    {"track_id": 14, "number": 4, "name": "Van Dijk", "role": "CB", "cam_x": 980, "cam_y": 410},
    {"track_id": 15, "number": 5, "name": "Konate", "role": "CB", "cam_x": 980, "cam_y": 510},
    {"track_id": 16, "number": None, "name": "Robertson", "role": "LB", "cam_x": 950, "cam_y": 600},
    {"track_id": 17, "number": 38, "name": "Gravenberch", "role": "DM", "cam_x": 810, "cam_y": 460},
    {"track_id": 18, "number": 10, "name": "Mac Allister", "role": "CM", "cam_x": 790, "cam_y": 380},
    {"track_id": 19, "number": 8, "name": "Szoboszlai", "role": "CM", "cam_x": 790, "cam_y": 540},
    {"track_id": 20, "number": 11, "name": "Salah", "role": "RW", "cam_x": 650, "cam_y": 330},
    {"track_id": 21, "number": 9, "name": "Nunez", "role": "ST", "cam_x": 640, "cam_y": 460},
    {"track_id": 22, "number": 7, "name": "Diaz", "role": "LW", "cam_x": 650, "cam_y": 590},
]

generate_match(
    filename="match_pl_arsenal_liverpool",
    title="Arsenal vs Liverpool",
    competition="Premier League",
    team_a_name="Arsenal",
    team_a_formation="4-2-3-1 Modern",
    team_a_color=(40, 40, 220),   # Red
    team_a_roster=roster_arsenal,
    team_b_name="Liverpool",
    team_b_formation="4-3-3 Attack",
    team_b_color=(200, 200, 20),  # Teal / Green
    team_b_roster=roster_liverpool,
    ball_traj_func=lambda t: (640 + 100 * math.cos(t * 1.8), 460 + 50 * math.sin(t * 1.8))
)


# --- MATCH 3: Barcelona vs Bayern Munich ---
roster_barca = [
    {"track_id": 1, "number": 1, "name": "Ter Stegen", "role": "GK", "cam_x": 160, "cam_y": 460},
    {"track_id": 2, "number": 23, "name": "Kounde", "role": "RB", "cam_x": 330, "cam_y": 320},
    {"track_id": 3, "number": 2, "name": "Cubarsi", "role": "CB", "cam_x": 290, "cam_y": 410},
    {"track_id": 4, "number": 5, "name": "Martinez", "role": "CB", "cam_x": 290, "cam_y": 510},
    {"track_id": 5, "number": None, "name": "Balde", "role": "LB", "cam_x": 330, "cam_y": 600},
    {"track_id": 6, "number": 17, "name": "Casado", "role": "DM", "cam_x": 480, "cam_y": 410},
    {"track_id": 7, "number": 8, "name": "Pedri", "role": "CM", "cam_x": 580, "cam_y": 480},
    {"track_id": 8, "number": 20, "name": "Dani Olmo", "role": "AM", "cam_x": 640, "cam_y": 430},
    {"track_id": 9, "number": 19, "name": "Lamine Yamal", "role": "RW", "cam_x": 790, "cam_y": 330},
    {"track_id": 10, "number": 9, "name": "Lewandowski", "role": "ST", "cam_x": 820, "cam_y": 460},
    {"track_id": 11, "number": 11, "name": "Raphinha", "role": "LW", "cam_x": 790, "cam_y": 590},
]
roster_bayern = [
    {"track_id": 12, "number": 1, "name": "Neuer", "role": "GK", "cam_x": 1120, "cam_y": 460},
    {"track_id": 13, "number": 22, "name": "Guerreiro", "role": "RB", "cam_x": 950, "cam_y": 320},
    {"track_id": 14, "number": 2, "name": "Upamecano", "role": "CB", "cam_x": 980, "cam_y": 410},
    {"track_id": 15, "number": 3, "name": "Kim Min-jae", "role": "CB", "cam_x": 980, "cam_y": 510},
    {"track_id": 16, "number": None, "name": "Davies", "role": "LB", "cam_x": 950, "cam_y": 600},
    {"track_id": 17, "number": 16, "name": "Palhinha", "role": "DM", "cam_x": 820, "cam_y": 420},
    {"track_id": 18, "number": 6, "name": "Kimmich", "role": "DM", "cam_x": 820, "cam_y": 500},
    {"track_id": 19, "number": 42, "name": "Musiala", "role": "AM", "cam_x": 700, "cam_y": 460},
    {"track_id": 20, "number": 17, "name": "Olise", "role": "RW", "cam_x": 660, "cam_y": 330},
    {"track_id": 21, "number": 9, "name": "Kane", "role": "ST", "cam_x": 640, "cam_y": 460},
    {"track_id": 22, "number": 7, "name": "Gnabry", "role": "LW", "cam_x": 660, "cam_y": 590},
]

generate_match(
    filename="match_ucl_barca_bayern",
    title="Barcelona vs Bayern Munich",
    competition="UEFA Champions League",
    team_a_name="Barcelona",
    team_a_formation="4-2-3-1 Modern",
    team_a_color=(160, 40, 100),   # Blaugrana
    team_a_roster=roster_barca,
    team_b_name="Bayern Munich",
    team_b_formation="4-2-3-1 High Press",
    team_b_color=(30, 30, 200),    # Red
    team_b_roster=roster_bayern,
    ball_traj_func=lambda t: (600 + 70 * math.sin(t * 1.3), 440 + 60 * math.cos(t * 1.3))
)

print("All match videos and telemetry generated!")
