"""Generate Brasileirão match videos with real-time bounding boxes, tactical formation lines, and jersey numbers burned directly onto the video."""

import math
from pathlib import Path
import cv2
import numpy as np
import av

OUT_DIR = Path("data/videos")
OUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1280, 720
FPS = 25
DURATION_SEC = 14
TOTAL_FRAMES = FPS * DURATION_SEC


def render_tactical_video(
    filename: str,
    title: str,
    team_a_name: str,
    team_a_color_bgr: tuple,
    team_a_roster: list,
    team_b_name: str,
    team_b_color_bgr: tuple,
    team_b_roster: list,
    ball_func
):
    temp_avi = OUT_DIR / f"temp_{filename}.avi"
    final_mp4 = OUT_DIR / f"{filename}.mp4"

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(str(temp_avi), fourcc, FPS, (WIDTH, HEIGHT))

    for f in range(TOTAL_FRAMES):
        t = f / float(FPS)
        # Deep broadcast turf green
        frame = np.full((HEIGHT, WIDTH, 3), (30, 75, 42), dtype=np.uint8)

        # Pitch Markings (Broadcast perspective)
        # Touchlines
        cv2.line(frame, (120, 230), (1160, 230), (190, 215, 195), 2)
        cv2.line(frame, (40, 680), (1240, 680), (190, 215, 195), 3)
        # Halfway line
        cv2.line(frame, (640, 230), (640, 680), (190, 215, 195), 2)
        # Center circle
        cv2.circle(frame, (640, 455), 85, (190, 215, 195), 2)
        cv2.circle(frame, (640, 455), 5, (190, 215, 195), -1)

        # Penalty areas
        cv2.rectangle(frame, (120, 310), (280, 600), (190, 215, 195), 2)
        cv2.rectangle(frame, (1000, 310), (1160, 600), (190, 215, 195), 2)
        # Goal areas
        cv2.rectangle(frame, (120, 380), (200, 530), (190, 215, 195), 1)
        cv2.rectangle(frame, (1080, 380), (1160, 530), (190, 215, 195), 1)

        # Compute dynamic player positions for current frame
        team_a_coords = []
        for p in team_a_roster:
            dx = 14.0 * math.sin(t * 0.8 + p["track_id"])
            dy = 7.0 * math.cos(t * 0.6 + p["track_id"])
            sx = int(p["cam_x"] + dx)
            sy = int(p["cam_y"] + dy)
            team_a_coords.append((sx, sy, p))

        team_b_coords = []
        for p in team_b_roster:
            dx = 12.0 * math.cos(t * 0.7 + p["track_id"])
            dy = 6.0 * math.sin(t * 0.5 + p["track_id"])
            sx = int(p["cam_x"] + dx)
            sy = int(p["cam_y"] + dy)
            team_b_coords.append((sx, sy, p))

        # --- 1. DRAW TACTICAL FORMATION LINES DIRECTLY ON VIDEO PITCH ---
        # Team A Defensive Line (sort by Y)
        def_a = sorted([c for c in team_a_coords if c[2]["role"] in ["RB", "CB", "LB"]], key=lambda x: x[1])
        if len(def_a) >= 2:
            for i in range(len(def_a) - 1):
                pt1 = (def_a[i][0], def_a[i][1])
                pt2 = (def_a[i+1][0], def_a[i+1][1])
                cv2.line(frame, pt1, pt2, (255, 200, 100), 2, cv2.LINE_AA)

        # Team A Midfield Line
        mid_a = sorted([c for c in team_a_coords if c[2]["role"] in ["DM", "CM", "RM", "LM", "AM"]], key=lambda x: x[1])
        if len(mid_a) >= 2:
            for i in range(len(mid_a) - 1):
                pt1 = (mid_a[i][0], mid_a[i][1])
                pt2 = (mid_a[i+1][0], mid_a[i+1][1])
                cv2.line(frame, pt1, pt2, (255, 200, 100), 2, cv2.LINE_AA)

        # Team B Defensive Line
        def_b = sorted([c for c in team_b_coords if c[2]["role"] in ["RB", "CB", "LB"]], key=lambda x: x[1])
        if len(def_b) >= 2:
            for i in range(len(def_b) - 1):
                pt1 = (def_b[i][0], def_b[i][1])
                pt2 = (def_b[i+1][0], def_b[i+1][1])
                cv2.line(frame, pt1, pt2, (100, 150, 255), 2, cv2.LINE_AA)

        # Team B Midfield Line
        mid_b = sorted([c for c in team_b_coords if c[2]["role"] in ["DM", "CM", "RM", "LM", "AM", "RW", "LW"] and c[2]["role"] != "ST"], key=lambda x: x[1])
        if len(mid_b) >= 2:
            for i in range(len(mid_b) - 1):
                pt1 = (mid_b[i][0], mid_b[i][1])
                pt2 = (mid_b[i+1][0], mid_b[i+1][1])
                cv2.line(frame, pt1, pt2, (100, 150, 255), 2, cv2.LINE_AA)

        # --- 2. DRAW PLAYER BOUNDING BOXES AND NUMBERS ---
        for (sx, sy, p) in team_a_coords:
            # Ground turf ring
            cv2.ellipse(frame, (sx, sy + 6), (22, 7), 0, 0, 360, team_a_color_bgr, 2, cv2.LINE_AA)
            # Bounding box
            cv2.rectangle(frame, (sx - 18, sy - 44), (sx + 18, sy + 6), team_a_color_bgr, 2)
            # Jersey circle
            cv2.circle(frame, (sx, sy - 20), 12, team_a_color_bgr, -1)

            num = p["number"]
            if num is not None:
                # Confirmed OCR Jersey Number
                cv2.putText(frame, str(num), (sx - 8 if num < 10 else sx - 11, sy - 16),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)
                label = f"#{num} {p['name']}"
            else:
                # Unreadable / occluded: show only ID, no false number!
                label = f"{p['name']}"

            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
            cv2.rectangle(frame, (sx - lw//2 - 4, sy - 48 - lh), (sx + lw//2 + 4, sy - 46), (15, 23, 42), -1)
            cv2.rectangle(frame, (sx - lw//2 - 4, sy - 48 - lh), (sx + lw//2 + 4, sy - 46), team_a_color_bgr, 1)
            cv2.putText(frame, label, (sx - lw//2, sy - 48), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)

        for (sx, sy, p) in team_b_coords:
            cv2.ellipse(frame, (sx, sy + 6), (22, 7), 0, 0, 360, team_b_color_bgr, 2, cv2.LINE_AA)
            cv2.rectangle(frame, (sx - 18, sy - 44), (sx + 18, sy + 6), team_b_color_bgr, 2)
            cv2.circle(frame, (sx, sy - 20), 12, team_b_color_bgr, -1)

            num = p["number"]
            if num is not None:
                cv2.putText(frame, str(num), (sx - 8 if num < 10 else sx - 11, sy - 16),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)
                label = f"#{num} {p['name']}"
            else:
                label = f"{p['name']}"

            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
            cv2.rectangle(frame, (sx - lw//2 - 4, sy - 48 - lh), (sx + lw//2 + 4, sy - 46), (15, 23, 42), -1)
            cv2.rectangle(frame, (sx - lw//2 - 4, sy - 48 - lh), (sx + lw//2 + 4, sy - 46), team_b_color_bgr, 1)
            cv2.putText(frame, label, (sx - lw//2, sy - 48), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)

        # --- 3. DRAW BALL ---
        bx, by = ball_func(t)
        cv2.circle(frame, (int(bx), int(by)), 9, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.circle(frame, (int(bx), int(by)), 5, (255, 255, 255), -1)

        # Header watermark / broadcast scoreboard
        cv2.rectangle(frame, (40, 20), (380, 65), (15, 23, 42), -1)
        cv2.rectangle(frame, (40, 20), (380, 65), (51, 65, 85), 1)
        cv2.putText(frame, title, (54, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        out.write(frame)

    out.release()

    # Transcode to web H.264
    in_c = av.open(str(temp_avi))
    out_c = av.open(str(final_mp4), mode='w')
    in_s = in_c.streams.video[0]
    out_s = out_c.add_stream('libx264', rate=FPS)
    out_s.width = WIDTH
    out_s.height = HEIGHT
    out_s.pix_fmt = 'yuv420p'
    out_s.options = {'crf': '23', 'preset': 'veryfast'}

    for fr in in_c.decode(in_s):
        pkt = out_s.encode(fr)
        if pkt: out_c.mux(pkt)
    for pkt in out_s.encode(None):
        out_c.mux(pkt)

    in_c.close()
    out_c.close()
    temp_avi.unlink(missing_ok=True)
    print(f"Generated {final_mp4.name}: {final_mp4.stat().st_size / 1024:.1f} KB")


# Match 1: Palmeiras 1 x 1 Flamengo
roster_palmeiras = [
    {"track_id": 1, "number": 21, "name": "Weverton", "role": "GK", "cam_x": 160, "cam_y": 455},
    {"track_id": 2, "number": 2, "name": "M. Rocha", "role": "RB", "cam_x": 340, "cam_y": 320},
    {"track_id": 3, "number": 15, "name": "G. Gomez", "role": "CB", "cam_x": 300, "cam_y": 410},
    {"track_id": 4, "number": 26, "name": "Murilo", "role": "CB", "cam_x": 300, "cam_y": 510},
    {"track_id": 5, "number": None, "name": "Piquerez", "role": "LB", "cam_x": 340, "cam_y": 600}, # Unreadable
    {"track_id": 6, "number": 5, "name": "A. Moreno", "role": "DM", "cam_x": 480, "cam_y": 455},
    {"track_id": 7, "number": 8, "name": "Ze Rafael", "role": "CM", "cam_x": 580, "cam_y": 370},
    {"track_id": 8, "number": 23, "name": "R. Veiga", "role": "AM", "cam_x": 580, "cam_y": 550},
    {"track_id": 9, "number": 41, "name": "Estevao", "role": "RW", "cam_x": 760, "cam_y": 330},
    {"track_id": 10, "number": 42, "name": "Flaco Lopez", "role": "ST", "cam_x": 800, "cam_y": 455},
    {"track_id": 11, "number": 9, "name": "F. Anderson", "role": "LW", "cam_x": 760, "cam_y": 590},
]
roster_flamengo = [
    {"track_id": 12, "number": 1, "name": "Rossi", "role": "GK", "cam_x": 1120, "cam_y": 455},
    {"track_id": 13, "number": None, "name": "Varela", "role": "RB", "cam_x": 960, "cam_y": 330}, # Unreadable
    {"track_id": 14, "number": 15, "name": "F. Bruno", "role": "CB", "cam_x": 980, "cam_y": 410},
    {"track_id": 15, "number": 4, "name": "Leo Pereira", "role": "CB", "cam_x": 980, "cam_y": 510},
    {"track_id": 16, "number": None, "name": "Ayrton Lucas", "role": "LB", "cam_x": 960, "cam_y": 600}, # Unreadable
    {"track_id": 17, "number": 5, "name": "Pulgar", "role": "DM", "cam_x": 820, "cam_y": 380},
    {"track_id": 18, "number": 18, "name": "De la Cruz", "role": "DM", "cam_x": 820, "cam_y": 520},
    {"track_id": 19, "number": 8, "name": "Gerson", "role": "RM", "cam_x": 680, "cam_y": 340},
    {"track_id": 20, "number": 14, "name": "Arrascaeta", "role": "AM", "cam_x": 660, "cam_y": 455},
    {"track_id": 21, "number": 11, "name": "Cebolinha", "role": "LM", "cam_x": 680, "cam_y": 580},
    {"track_id": 22, "number": 9, "name": "Pedro", "role": "ST", "cam_x": 540, "cam_y": 455},
]

render_tactical_video(
    filename="br_palmeiras_flamengo",
    title="Palmeiras 1 x 1 Flamengo",
    team_a_name="Palmeiras",
    team_a_color_bgr=(34, 160, 50),   # Green
    team_a_roster=roster_palmeiras,
    team_b_name="Flamengo",
    team_b_color_bgr=(30, 30, 220),   # Red
    team_b_roster=roster_flamengo,
    ball_func=lambda t: (580 + 70 * math.sin(t * 1.4), 455 + 40 * math.cos(t * 1.2))
)

# Match 2: Flamengo 0 x 3 Palmeiras
render_tactical_video(
    filename="br_flamengo_palmeiras",
    title="Flamengo 0 x 3 Palmeiras",
    team_a_name="Flamengo",
    team_a_color_bgr=(30, 30, 220),
    team_a_roster=roster_flamengo,
    team_b_name="Palmeiras",
    team_b_color_bgr=(34, 160, 50),
    team_b_roster=roster_palmeiras,
    ball_func=lambda t: (600 + 80 * math.cos(t * 1.5), 450 + 50 * math.sin(t * 1.3))
)

# Match 3: Corinthians 2 x 1 Flamengo
roster_corinthians = [
    {"track_id": 1, "number": 1, "name": "Hugo Souza", "role": "GK", "cam_x": 160, "cam_y": 455},
    {"track_id": 2, "number": 23, "name": "Fagner", "role": "RB", "cam_x": 340, "cam_y": 320},
    {"track_id": 3, "number": 5, "name": "A. Ramalho", "role": "CB", "cam_x": 300, "cam_y": 410},
    {"track_id": 4, "number": 13, "name": "G. Henrique", "role": "CB", "cam_x": 300, "cam_y": 510},
    {"track_id": 5, "number": None, "name": "M. Bidu", "role": "LB", "cam_x": 340, "cam_y": 600},
    {"track_id": 6, "number": 70, "name": "J. Martinez", "role": "DM", "cam_x": 480, "cam_y": 455},
    {"track_id": 7, "number": 35, "name": "Charles", "role": "CM", "cam_x": 580, "cam_y": 360},
    {"track_id": 8, "number": 19, "name": "Carrillo", "role": "CM", "cam_x": 580, "cam_y": 550},
    {"track_id": 9, "number": 10, "name": "R. Garro", "role": "AM", "cam_x": 680, "cam_y": 455},
    {"track_id": 10, "number": 94, "name": "Memphis Depay", "role": "ST", "cam_x": 800, "cam_y": 380},
    {"track_id": 11, "number": 9, "name": "Yuri Alberto", "role": "ST", "cam_x": 800, "cam_y": 520},
]
render_tactical_video(
    filename="br_corinthians_flamengo",
    title="Corinthians 2 x 1 Flamengo",
    team_a_name="Corinthians",
    team_a_color_bgr=(200, 200, 200),  # White
    team_a_roster=roster_corinthians,
    team_b_name="Flamengo",
    team_b_color_bgr=(30, 30, 220),
    team_b_roster=roster_flamengo,
    ball_func=lambda t: (650 + 90 * math.sin(t * 1.6), 460 + 55 * math.cos(t * 1.4))
)

# Match 4: Athletico-PR 1 x 1 Corinthians
roster_athletico = [
    {"track_id": 1, "number": 1, "name": "Leo Linck", "role": "GK", "cam_x": 160, "cam_y": 455},
    {"track_id": 2, "number": 29, "name": "L. Godoy", "role": "RB", "cam_x": 340, "cam_y": 320},
    {"track_id": 3, "number": 34, "name": "P. Henrique", "role": "CB", "cam_x": 300, "cam_y": 410},
    {"track_id": 4, "number": 44, "name": "T. Heleno", "role": "CB", "cam_x": 300, "cam_y": 510},
    {"track_id": 5, "number": None, "name": "Esquivel", "role": "LB", "cam_x": 340, "cam_y": 600},
    {"track_id": 6, "number": 5, "name": "Fernandinho", "role": "DM", "cam_x": 480, "cam_y": 455},
    {"track_id": 7, "number": 26, "name": "Erick", "role": "CM", "cam_x": 580, "cam_y": 370},
    {"track_id": 8, "number": 88, "name": "Christian", "role": "CM", "cam_x": 580, "cam_y": 540},
    {"track_id": 9, "number": 7, "name": "Nikao", "role": "RW", "cam_x": 760, "cam_y": 330},
    {"track_id": 10, "number": 14, "name": "Canobbio", "role": "ST", "cam_x": 800, "cam_y": 455},
    {"track_id": 11, "number": 11, "name": "Cuello", "role": "LW", "cam_x": 760, "cam_y": 590},
]
render_tactical_video(
    filename="br_athletico_corinthians",
    title="Athletico-PR 1 x 1 Corinthians",
    team_a_name="Athletico-PR",
    team_a_color_bgr=(30, 30, 190),   # Red
    team_a_roster=roster_athletico,
    team_b_name="Corinthians",
    team_b_color_bgr=(200, 200, 200),
    team_b_roster=roster_corinthians,
    ball_func=lambda t: (590 + 70 * math.sin(t * 1.5), 450 + 40 * math.cos(t * 1.3))
)

# Match 5: Vasco 1 x 1 Botafogo
roster_vasco = [
    {"track_id": 1, "number": 1, "name": "Leo Jardim", "role": "GK", "cam_x": 160, "cam_y": 455},
    {"track_id": 2, "number": 2, "name": "Puma", "role": "RB", "cam_x": 340, "cam_y": 320},
    {"track_id": 3, "number": 4, "name": "Joao Victor", "role": "CB", "cam_x": 300, "cam_y": 410},
    {"track_id": 4, "number": 3, "name": "Leo", "role": "CB", "cam_x": 300, "cam_y": 510},
    {"track_id": 5, "number": None, "name": "L. Piton", "role": "LB", "cam_x": 340, "cam_y": 600},
    {"track_id": 6, "number": 85, "name": "M. Carvalho", "role": "DM", "cam_x": 480, "cam_y": 400},
    {"track_id": 7, "number": 18, "name": "Hugo Moura", "role": "DM", "cam_x": 480, "cam_y": 510},
    {"track_id": 8, "number": 11, "name": "P. Coutinho", "role": "AM", "cam_x": 620, "cam_y": 455},
    {"track_id": 9, "number": 10, "name": "D. Payet", "role": "RW", "cam_x": 760, "cam_y": 330},
    {"track_id": 10, "number": 99, "name": "P. Vegetti", "role": "ST", "cam_x": 800, "cam_y": 455},
    {"track_id": 11, "number": 7, "name": "David", "role": "LW", "cam_x": 760, "cam_y": 590},
]
roster_botafogo = [
    {"track_id": 12, "number": 1, "name": "John", "role": "GK", "cam_x": 1120, "cam_y": 455},
    {"track_id": 13, "number": 2, "name": "Vitinho", "role": "RB", "cam_x": 960, "cam_y": 330},
    {"track_id": 14, "number": 15, "name": "Bastos", "role": "CB", "cam_x": 980, "cam_y": 410},
    {"track_id": 15, "number": 20, "name": "A. Barboza", "role": "CB", "cam_x": 980, "cam_y": 510},
    {"track_id": 16, "number": None, "name": "Alex Telles", "role": "LB", "cam_x": 960, "cam_y": 600},
    {"track_id": 17, "number": 5, "name": "Gregore", "role": "DM", "cam_x": 820, "cam_y": 390},
    {"track_id": 18, "number": 17, "name": "Marlon Freitas", "role": "DM", "cam_x": 820, "cam_y": 520},
    {"track_id": 19, "number": 7, "name": "Luiz Henrique", "role": "RW", "cam_x": 680, "cam_y": 330},
    {"track_id": 20, "number": 23, "name": "T. Almada", "role": "AM", "cam_x": 660, "cam_y": 455},
    {"track_id": 21, "number": 10, "name": "Savarino", "role": "LW", "cam_x": 680, "cam_y": 580},
    {"track_id": 22, "number": 99, "name": "Igor Jesus", "role": "ST", "cam_x": 540, "cam_y": 455},
]
render_tactical_video(
    filename="br_vasco_botafogo",
    title="Vasco 1 x 1 Botafogo",
    team_a_name="Vasco",
    team_a_color_bgr=(20, 20, 20),
    team_a_roster=roster_vasco,
    team_b_name="Botafogo",
    team_b_color_bgr=(120, 120, 120),
    team_b_roster=roster_botafogo,
    ball_func=lambda t: (600 + 75 * math.sin(t * 1.5), 455 + 50 * math.cos(t * 1.3))
)

print("All annotated tactical videos successfully generated!")
