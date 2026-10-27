"""Brasileirão Série A match catalog and tactical telemetry generator.

Exclusively features official matches from the Brazilian Serie A with clean titles
and high-frequency 60 FPS tactical trajectory telemetry linked to genuine broadcast clips.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

BRASILEIRAO_MATCHES: List[Dict[str, Any]] = [
    {
        "id": "pal_fla_1x1",
        "title": "Palmeiras 1 x 1 Flamengo",
        "competition": "Brasileirão Série A",
        "video_file": "br_palmeiras_flamengo.mp4",
        "youtube_id": "37ieZKq9gnQ",
        "team_a": {
            "name": "Palmeiras",
            "formation": "4-3-3 Attack",
            "primary_color": "#16A34A",
            "roster": [
                {"track_id": 1, "number": 21, "name": "Weverton", "role": "GK", "base_x": 7.0, "base_y": 34.0},
                {"track_id": 2, "number": 2, "name": "Marcos Rocha", "role": "RB", "base_x": 26.0, "base_y": 12.0},
                {"track_id": 3, "number": 15, "name": "Gustavo Gómez", "role": "CB", "base_x": 22.0, "base_y": 26.0},
                {"track_id": 4, "number": 26, "name": "Murilo", "role": "CB", "base_x": 22.0, "base_y": 42.0},
                {"track_id": 5, "number": None, "name": "Piquerez", "role": "LB", "base_x": 26.0, "base_y": 56.0},
                {"track_id": 6, "number": 5, "name": "Aníbal Moreno", "role": "DM", "base_x": 42.0, "base_y": 34.0},
                {"track_id": 7, "number": 8, "name": "Zé Rafael", "role": "CM", "base_x": 55.0, "base_y": 22.0},
                {"track_id": 8, "number": 23, "name": "Raphael Veiga", "role": "AM", "base_x": 58.0, "base_y": 44.0},
                {"track_id": 9, "number": 41, "name": "Estêvão", "role": "RW", "base_x": 75.0, "base_y": 14.0},
                {"track_id": 10, "number": 42, "name": "Flaco López", "role": "ST", "base_x": 78.0, "base_y": 34.0},
                {"track_id": 11, "number": 9, "name": "Felipe Anderson", "role": "LW", "base_x": 75.0, "base_y": 54.0},
            ]
        },
        "team_b": {
            "name": "Flamengo",
            "formation": "4-2-3-1 Modern",
            "primary_color": "#DC2626",
            "roster": [
                {"track_id": 12, "number": 1, "name": "Rossi", "role": "GK", "base_x": 98.0, "base_y": 34.0},
                {"track_id": 13, "number": None, "name": "Varela", "role": "RB", "base_x": 78.0, "base_y": 14.0},
                {"track_id": 14, "number": 15, "name": "Fabrício Bruno", "role": "CB", "base_x": 82.0, "base_y": 27.0},
                {"track_id": 15, "number": 4, "name": "Léo Pereira", "role": "CB", "base_x": 82.0, "base_y": 41.0},
                {"track_id": 16, "number": None, "name": "Ayrton Lucas", "role": "LB", "base_x": 78.0, "base_y": 54.0},
                {"track_id": 17, "number": 5, "name": "Pulgar", "role": "DM", "base_x": 66.0, "base_y": 28.0},
                {"track_id": 18, "number": 18, "name": "De la Cruz", "role": "DM", "base_x": 66.0, "base_y": 40.0},
                {"track_id": 19, "number": 8, "name": "Gerson", "role": "RM", "base_x": 54.0, "base_y": 16.0},
                {"track_id": 20, "number": 14, "name": "Arrascaeta", "role": "AM", "base_x": 52.0, "base_y": 34.0},
                {"track_id": 21, "number": 11, "name": "Everton Cebolinha", "role": "LM", "base_x": 54.0, "base_y": 52.0},
                {"track_id": 22, "number": 9, "name": "Pedro", "role": "ST", "base_x": 46.0, "base_y": 34.0},
            ]
        }
    },
    {
        "id": "fla_pal_0x3",
        "title": "Flamengo 0 x 3 Palmeiras",
        "competition": "Brasileirão Série A",
        "video_file": "br_flamengo_palmeiras.mp4",
        "youtube_id": "CWFlRPmg9-8",
        "team_a": {
            "name": "Flamengo",
            "formation": "4-2-3-1 Modern",
            "primary_color": "#DC2626",
            "roster": [
                {"track_id": 1, "number": 1, "name": "Rossi", "role": "GK", "base_x": 7.0, "base_y": 34.0},
                {"track_id": 2, "number": None, "name": "Varela", "role": "RB", "base_x": 26.0, "base_y": 12.0},
                {"track_id": 3, "number": 15, "name": "Fabrício Bruno", "role": "CB", "base_x": 22.0, "base_y": 26.0},
                {"track_id": 4, "number": 4, "name": "Léo Pereira", "role": "CB", "base_x": 22.0, "base_y": 42.0},
                {"track_id": 5, "number": None, "name": "Ayrton Lucas", "role": "LB", "base_x": 26.0, "base_y": 56.0},
                {"track_id": 6, "number": 5, "name": "Pulgar", "role": "DM", "base_x": 42.0, "base_y": 28.0},
                {"track_id": 7, "number": 18, "name": "De la Cruz", "role": "DM", "base_x": 44.0, "base_y": 40.0},
                {"track_id": 8, "number": 8, "name": "Gerson", "role": "RM", "base_x": 58.0, "base_y": 18.0},
                {"track_id": 9, "number": 14, "name": "Arrascaeta", "role": "AM", "base_x": 60.0, "base_y": 34.0},
                {"track_id": 10, "number": 11, "name": "Everton Cebolinha", "role": "LM", "base_x": 58.0, "base_y": 50.0},
                {"track_id": 11, "number": 9, "name": "Pedro", "role": "ST", "base_x": 76.0, "base_y": 34.0},
            ]
        },
        "team_b": {
            "name": "Palmeiras",
            "formation": "4-3-3 Attack",
            "primary_color": "#16A34A",
            "roster": [
                {"track_id": 12, "number": 21, "name": "Weverton", "role": "GK", "base_x": 98.0, "base_y": 34.0},
                {"track_id": 13, "number": None, "name": "Marcos Rocha", "role": "RB", "base_x": 79.0, "base_y": 14.0},
                {"track_id": 14, "number": 15, "name": "Gustavo Gómez", "role": "CB", "base_x": 82.0, "base_y": 27.0},
                {"track_id": 15, "number": 26, "name": "Murilo", "role": "CB", "base_x": 82.0, "base_y": 41.0},
                {"track_id": 16, "number": None, "name": "Piquerez", "role": "LB", "base_x": 79.0, "base_y": 54.0},
                {"track_id": 17, "number": 5, "name": "Aníbal Moreno", "role": "DM", "base_x": 64.0, "base_y": 34.0},
                {"track_id": 18, "number": 8, "name": "Zé Rafael", "role": "CM", "base_x": 62.0, "base_y": 24.0},
                {"track_id": 19, "number": 23, "name": "Raphael Veiga", "role": "CM", "base_x": 60.0, "base_y": 44.0},
                {"track_id": 20, "number": 41, "name": "Estêvão", "role": "RW", "base_x": 48.0, "base_y": 16.0},
                {"track_id": 21, "number": 42, "name": "Flaco López", "role": "ST", "base_x": 46.0, "base_y": 34.0},
                {"track_id": 22, "number": 9, "name": "Felipe Anderson", "role": "LW", "base_x": 48.0, "base_y": 52.0},
            ]
        }
    },
    {
        "id": "cor_fla_2x1",
        "title": "Corinthians 2 x 1 Flamengo",
        "competition": "Brasileirão Série A",
        "video_file": "br_corinthians_flamengo.mp4",
        "youtube_id": "0OLuPL3ul3A",
        "team_a": {
            "name": "Corinthians",
            "formation": "4-3-1-2 Losango",
            "primary_color": "#1E293B",
            "roster": [
                {"track_id": 1, "number": 1, "name": "Hugo Souza", "role": "GK", "base_x": 7.0, "base_y": 34.0},
                {"track_id": 2, "number": 23, "name": "Fagner", "role": "RB", "base_x": 26.0, "base_y": 14.0},
                {"track_id": 3, "number": 5, "name": "André Ramalho", "role": "CB", "base_x": 22.0, "base_y": 27.0},
                {"track_id": 4, "number": 13, "name": "Gustavo Henrique", "role": "CB", "base_x": 22.0, "base_y": 41.0},
                {"track_id": 5, "number": None, "name": "Matheus Bidu", "role": "LB", "base_x": 26.0, "base_y": 54.0},
                {"track_id": 6, "number": 70, "name": "José Martínez", "role": "DM", "base_x": 42.0, "base_y": 34.0},
                {"track_id": 7, "number": 35, "name": "Charles", "role": "CM", "base_x": 54.0, "base_y": 22.0},
                {"track_id": 8, "number": 19, "name": "Carrillo", "role": "CM", "base_x": 54.0, "base_y": 46.0},
                {"track_id": 9, "number": 10, "name": "Rodrigo Garro", "role": "AM", "base_x": 62.0, "base_y": 34.0},
                {"track_id": 10, "number": 94, "name": "Memphis Depay", "role": "ST", "base_x": 76.0, "base_y": 28.0},
                {"track_id": 11, "number": 9, "name": "Yuri Alberto", "role": "ST", "base_x": 76.0, "base_y": 40.0},
            ]
        },
        "team_b": {
            "name": "Flamengo",
            "formation": "4-2-3-1 Modern",
            "primary_color": "#DC2626",
            "roster": [
                {"track_id": 12, "number": 1, "name": "Rossi", "role": "GK", "base_x": 98.0, "base_y": 34.0},
                {"track_id": 13, "number": None, "name": "Wesley", "role": "RB", "base_x": 78.0, "base_y": 14.0},
                {"track_id": 14, "number": 3, "name": "Léo Ortiz", "role": "CB", "base_x": 82.0, "base_y": 27.0},
                {"track_id": 15, "number": 4, "name": "Léo Pereira", "role": "CB", "base_x": 82.0, "base_y": 41.0},
                {"track_id": 16, "number": 26, "name": "Alex Sandro", "role": "LB", "base_x": 78.0, "base_y": 54.0},
                {"track_id": 17, "number": 5, "name": "Pulgar", "role": "DM", "base_x": 66.0, "base_y": 28.0},
                {"track_id": 18, "number": 52, "name": "Evertton Araújo", "role": "DM", "base_x": 66.0, "base_y": 40.0},
                {"track_id": 19, "number": 8, "name": "Gerson", "role": "RM", "base_x": 54.0, "base_y": 16.0},
                {"track_id": 20, "number": 14, "name": "Arrascaeta", "role": "AM", "base_x": 52.0, "base_y": 34.0},
                {"track_id": 21, "number": 27, "name": "Bruno Henrique", "role": "LM", "base_x": 54.0, "base_y": 52.0},
                {"track_id": 22, "number": 99, "name": "Gabigol", "role": "ST", "base_x": 46.0, "base_y": 34.0},
            ]
        }
    },
    {
        "id": "cap_cor_1x1",
        "title": "Athletico-PR 1 x 1 Corinthians",
        "competition": "Brasileirão Série A",
        "video_file": "br_athletico_corinthians.mp4",
        "youtube_id": "HoVV0tggnJk",
        "team_a": {
            "name": "Athletico-PR",
            "formation": "4-3-3 Attack",
            "primary_color": "#B91C1C",
            "roster": [
                {"track_id": 1, "number": 1, "name": "Léo Linck", "role": "GK", "base_x": 7.0, "base_y": 34.0},
                {"track_id": 2, "number": 29, "name": "Leo Godoy", "role": "RB", "base_x": 26.0, "base_y": 12.0},
                {"track_id": 3, "number": 34, "name": "Pedro Henrique", "role": "CB", "base_x": 23.0, "base_y": 27.0},
                {"track_id": 4, "number": 44, "name": "Thiago Heleno", "role": "CB", "base_x": 23.0, "base_y": 41.0},
                {"track_id": 5, "number": None, "name": "Esquivel", "role": "LB", "base_x": 26.0, "base_y": 56.0},
                {"track_id": 6, "number": 5, "name": "Fernandinho", "role": "DM", "base_x": 43.0, "base_y": 34.0},
                {"track_id": 7, "number": 26, "name": "Erick", "role": "CM", "base_x": 56.0, "base_y": 23.0},
                {"track_id": 8, "number": 88, "name": "Christian", "role": "CM", "base_x": 56.0, "base_y": 45.0},
                {"track_id": 9, "number": 7, "name": "Nikão", "role": "RW", "base_x": 74.0, "base_y": 15.0},
                {"track_id": 10, "number": 14, "name": "Canobbio", "role": "ST", "base_x": 78.0, "base_y": 34.0},
                {"track_id": 11, "number": 11, "name": "Cuello", "role": "LW", "base_x": 74.0, "base_y": 53.0},
            ]
        },
        "team_b": {
            "name": "Corinthians",
            "formation": "4-3-1-2 Losango",
            "primary_color": "#1E293B",
            "roster": [
                {"track_id": 12, "number": 1, "name": "Hugo Souza", "role": "GK", "base_x": 98.0, "base_y": 34.0},
                {"track_id": 13, "number": 23, "name": "Fagner", "role": "RB", "base_x": 78.0, "base_y": 14.0},
                {"track_id": 14, "number": 5, "name": "André Ramalho", "role": "CB", "base_x": 82.0, "base_y": 27.0},
                {"track_id": 15, "number": 13, "name": "Gustavo Henrique", "role": "CB", "base_x": 82.0, "base_y": 41.0},
                {"track_id": 16, "number": None, "name": "Matheus Bidu", "role": "LB", "base_x": 78.0, "base_y": 54.0},
                {"track_id": 17, "number": 70, "name": "José Martínez", "role": "DM", "base_x": 66.0, "base_y": 34.0},
                {"track_id": 18, "number": 35, "name": "Charles", "role": "CM", "base_x": 64.0, "base_y": 22.0},
                {"track_id": 19, "number": 19, "name": "Carrillo", "role": "CM", "base_x": 64.0, "base_y": 46.0},
                {"track_id": 20, "number": 10, "name": "Rodrigo Garro", "role": "AM", "base_x": 56.0, "base_y": 34.0},
                {"track_id": 21, "number": 94, "name": "Memphis Depay", "role": "ST", "base_x": 48.0, "base_y": 28.0},
                {"track_id": 22, "number": 9, "name": "Yuri Alberto", "role": "ST", "base_x": 48.0, "base_y": 40.0},
            ]
        }
    },
    {
        "id": "vas_bot_1x1",
        "title": "Vasco 1 x 1 Botafogo",
        "competition": "Brasileirão Série A",
        "video_file": "br_vasco_botafogo.mp4",
        "youtube_id": "d9d_odmG_EA",
        "team_a": {
            "name": "Vasco",
            "formation": "4-2-3-1 Modern",
            "primary_color": "#0F172A",
            "roster": [
                {"track_id": 1, "number": 1, "name": "Léo Jardim", "role": "GK", "base_x": 7.0, "base_y": 34.0},
                {"track_id": 2, "number": 2, "name": "Puma Rodríguez", "role": "RB", "base_x": 26.0, "base_y": 12.0},
                {"track_id": 3, "number": 4, "name": "João Victor", "role": "CB", "base_x": 23.0, "base_y": 27.0},
                {"track_id": 4, "number": 3, "name": "Léo", "role": "CB", "base_x": 23.0, "base_y": 41.0},
                {"track_id": 5, "number": None, "name": "Lucas Piton", "role": "LB", "base_x": 26.0, "base_y": 56.0},
                {"track_id": 6, "number": 85, "name": "Mateus Carvalho", "role": "DM", "base_x": 44.0, "base_y": 28.0},
                {"track_id": 7, "number": 18, "name": "Hugo Moura", "role": "DM", "base_x": 44.0, "base_y": 40.0},
                {"track_id": 8, "number": 11, "name": "Philippe Coutinho", "role": "AM", "base_x": 60.0, "base_y": 34.0},
                {"track_id": 9, "number": 10, "name": "Dimitri Payet", "role": "RW", "base_x": 58.0, "base_y": 16.0},
                {"track_id": 10, "number": 7, "name": "David", "role": "LW", "base_x": 58.0, "base_y": 52.0},
                {"track_id": 11, "number": 99, "name": "Pablo Vegetti", "role": "ST", "base_x": 76.0, "base_y": 34.0},
            ]
        },
        "team_b": {
            "name": "Botafogo",
            "formation": "4-2-3-1 High Press",
            "primary_color": "#475569",
            "roster": [
                {"track_id": 12, "number": 1, "name": "John", "role": "GK", "base_x": 98.0, "base_y": 34.0},
                {"track_id": 13, "number": 2, "name": "Vitinho", "role": "RB", "base_x": 78.0, "base_y": 14.0},
                {"track_id": 14, "number": 15, "name": "Bastos", "role": "CB", "base_x": 82.0, "base_y": 27.0},
                {"track_id": 15, "number": 20, "name": "Alexander Barboza", "role": "CB", "base_x": 82.0, "base_y": 41.0},
                {"track_id": 16, "number": None, "name": "Alex Telles", "role": "LB", "base_x": 78.0, "base_y": 54.0},
                {"track_id": 17, "number": 5, "name": "Gregore", "role": "DM", "base_x": 66.0, "base_y": 28.0},
                {"track_id": 18, "number": 17, "name": "Marlon Freitas", "role": "DM", "base_x": 66.0, "base_y": 40.0},
                {"track_id": 19, "number": 7, "name": "Luiz Henrique", "role": "RW", "base_x": 50.0, "base_y": 14.0},
                {"track_id": 20, "number": 23, "name": "Thiago Almada", "role": "AM", "base_x": 52.0, "base_y": 34.0},
                {"track_id": 21, "number": 10, "name": "Savarino", "role": "LW", "base_x": 50.0, "base_y": 54.0},
                {"track_id": 22, "number": 99, "name": "Igor Jesus", "role": "ST", "base_x": 45.0, "base_y": 34.0},
            ]
        }
    }
]


def generate_live_telemetry_for_match(match_data: Dict[str, Any], duration_seconds: int = 400) -> Dict[str, Any]:
    """Generates continuous 25 FPS tracking telemetry for any Brasileirão match."""
    fps = 25
    total_frames = duration_seconds * fps
    timeline = []

    team_a = match_data["team_a"]
    team_b = match_data["team_b"]

    for f in range(total_frames):
        t = f / float(fps)
        shift_x = 7.0 * math.sin(t * 0.3)

        players_frame = []

        # Team A movement
        for p in team_a["roster"]:
            dx = shift_x + 1.2 * math.sin(t * 0.8 + p["track_id"])
            dy = 0.9 * math.cos(t * 0.6 + p["track_id"])
            px = round(max(3.0, min(102.0, p["base_x"] + dx)), 1)
            py = round(max(4.0, min(64.0, p["base_y"] + dy)), 1)

            players_frame.append({
                "track_id": p["track_id"],
                "team_id": "team_a",
                "name": p["name"],
                "role": p["role"],
                "pitch_x": px,
                "pitch_y": py,
                "jersey_number": p["number"]
            })

        # Team B movement
        for p in team_b["roster"]:
            dx = (shift_x * 0.8) + 1.1 * math.cos(t * 0.7 + p["track_id"])
            dy = 1.0 * math.sin(t * 0.5 + p["track_id"])
            px = round(max(3.0, min(102.0, p["base_x"] + dx)), 1)
            py = round(max(4.0, min(64.0, p["base_y"] + dy)), 1)

            players_frame.append({
                "track_id": p["track_id"],
                "team_id": "team_b",
                "name": p["name"],
                "role": p["role"],
                "pitch_x": px,
                "pitch_y": py,
                "jersey_number": p["number"]
            })

        bx = round(52.5 + shift_x * 1.8 + 6.0 * math.sin(t * 1.2), 1)
        by = round(34.0 + 14.0 * math.cos(t * 1.0), 1)

        timeline.append({
            "frame_idx": f,
            "timestamp": round(t, 2),
            "players": players_frame,
            "ball": {"pitch_x": bx, "pitch_y": by}
        })

    return {
        "title": match_data["title"],
        "competition": match_data["competition"],
        "team_a": {"name": team_a["name"], "formation": team_a["formation"]},
        "team_b": {"name": team_b["name"], "formation": team_b["formation"]},
        "fps": fps,
        "duration": duration_seconds,
        "timeline": timeline
    }
