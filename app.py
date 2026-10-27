"""Football Vision Analytics - Streamlit Web Application.

Unified Tactical Dashboard for Databricks Apps & Local Deployment.
Combines ad-free broadcast match footage with synchronized real-time 2D pitch radar,
tactical formation classifier (4-3-3, 4-4-2, etc.), and jersey number recognition.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from src.config import DEMO_DIR, VIDEOS_DIR
from src.tactics.formation_detector import FormationDetector
from src.visualization.synced_player import build_synced_player_html

# Page Configuration
st.set_page_config(
    page_title="Football Vision Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for Sleek Sports Analytics Theme
st.markdown("""
<style>
    .header-container {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 4px;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-bottom: 16px;
    }
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
</style>
""", unsafe_allow_html=True)


MATCH_CATALOG = [
    {
        "id": "match_ucl_city_real",
        "title": "Manchester City vs Real Madrid",
        "competition": "UEFA Champions League Final",
        "team_a": "Manchester City",
        "team_a_formation": "4-3-3 Attack",
        "team_b": "Real Madrid",
        "team_b_formation": "4-4-2 Classic",
        "video_file": "match_ucl_city_real.mp4",
        "json_file": "match_ucl_city_real.json",
        "description": "Tactical build-up from defensive third into high midfield pressing."
    },
    {
        "id": "match_pl_arsenal_liverpool",
        "title": "Arsenal vs Liverpool",
        "competition": "Premier League Super Sunday",
        "team_a": "Arsenal",
        "team_a_formation": "4-2-3-1 Modern",
        "team_b": "Liverpool",
        "team_b_formation": "4-3-3 High Press",
        "video_file": "match_pl_arsenal_liverpool.mp4",
        "json_file": "match_pl_arsenal_liverpool.json",
        "description": "High-speed counter-attack transition down the flanks."
    },
    {
        "id": "match_ucl_barca_bayern",
        "title": "Barcelona vs Bayern Munich",
        "competition": "UEFA Champions League",
        "team_a": "Barcelona",
        "team_a_formation": "4-2-3-1 Modern",
        "team_b": "Bayern Munich",
        "team_b_formation": "4-2-3-1 High Press",
        "video_file": "match_ucl_barca_bayern.mp4",
        "json_file": "match_ucl_barca_bayern.json",
        "description": "Midfield spatial duel with synchronized pressing lines."
    }
]


def load_match_telemetry(filename: str) -> Dict[str, Any]:
    """Load pre-computed tactical telemetry JSON file."""
    path = DEMO_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def render_header():
    """Render top application banner."""
    st.markdown("""
    <div class="header-container">
        <img src="https://img.icons8.com/color/96/football2--v1.png" width="46" style="vertical-align:middle;">
        <span class="main-title">Football Vision Analytics</span>
    </div>
    <div class="sub-title">
        Computer Vision & Tactical Tracking • Ad-Free Broadcast Video & Real-Time 2D Radar
    </div>
    """, unsafe_allow_html=True)


def main():
    render_header()

    # Section 1: Match & Video Selection
    st.write("### 🎬 1. Select Match & Tactical Video")

    match_titles = [
        f"{m['title']} — {m['competition']} ({m['team_a_formation']} vs {m['team_b_formation']})"
        for m in MATCH_CATALOG
    ]

    sel_col1, sel_col2 = st.columns([3, 1])

    with sel_col1:
        chosen_idx = st.selectbox(
            "⚽ Choose Football Match (Ad-Free Videos with Live Synchronized 2D Radar):",
            range(len(match_titles)),
            format_func=lambda i: match_titles[i]
        )

    with sel_col2:
        theme = st.selectbox("🎨 Radar Turf Theme:", ["dark", "green"], index=0)

    selected_match = MATCH_CATALOG[chosen_idx]
    video_path = VIDEOS_DIR / selected_match["video_file"]
    telemetry = load_match_telemetry(selected_match["json_file"])

    # Section 2: Tactical Metric Summary Cards
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#60A5FA; font-size:0.85rem; font-weight:bold;">🔵 {selected_match["team_a"].upper()}</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">{selected_match["team_a_formation"]}</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">Tactical System: In-Possession Build</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#F87171; font-size:0.85rem; font-weight:bold;">🔴 {selected_match["team_b"].upper()}</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">{selected_match["team_b_formation"]}</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">Tactical System: Mid-Block Shape</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#FACC15; font-size:0.85rem; font-weight:bold;">⚡ SYNC PLAYBACK STATUS</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">60 FPS Real-Time</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">Radar moves when video plays</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#34D399; font-size:0.85rem; font-weight:bold;">🛡️ AD-FREE & PRIVATE</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">Zero Ads</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">Direct HTML5 H.264 video</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Section 3: Synchronized Side-by-Side Player (Video Left, Radar Right)
    st.write("---")
    st.write("### 📺 2. Live Side-by-Side: Video & Real-Time Tactical 2D Radar")
    st.caption("Press **Play** on the video to see the 2D pitch radar animate simultaneously! Scrub or pause at any point.")

    if video_path.exists() and telemetry:
        player_html = build_synced_player_html(
            video_path=str(video_path),
            telemetry=telemetry,
            theme=theme
        )
        st.components.v1.html(player_html, height=520)
    else:
        st.error("Video or telemetry data not found. Please verify files exist in data/videos/.")

    # Section 4: Squad Lineups & Jersey Numbers (OCR Recognition Status)
    st.write("---")
    st.write("### 📋 3. Team Lineups & Jersey Number Recognition")
    st.caption("Numbers appear on the 2D radar and table ONLY when clearly readable. Unclear or occluded players remain without numbers.")

    sample_frame = telemetry.get("timeline", [{}])[0]
    players_list = sample_frame.get("players", [])

    team_a_players = [p for p in players_list if p.get("team_id") == "team_a"]
    team_b_players = [p for p in players_list if p.get("team_id") == "team_b"]

    tab_a, tab_b = st.tabs([f"🔵 {selected_match['team_a']} Squad", f"🔴 {selected_match['team_b']} Squad"])

    with tab_a:
        df_a = pd.DataFrame([
            {
                "Track ID": p.get("track_id"),
                "Player Name": p.get("name"),
                "Position": p.get("role"),
                "Jersey Number": f"#{p['jersey_number']}" if p.get("jersey_number") is not None else "⚠️ Unreadable / Occluded (Left Blank)",
                "Initial X (m)": p.get("pitch_x"),
                "Initial Y (m)": p.get("pitch_y"),
                "OCR Status": "✅ Confirmed via OCR" if p.get("jersey_number") is not None else "⚪ Blank Marker (No Number)"
            }
            for p in team_a_players
        ])
        st.dataframe(df_a, use_container_width=True, hide_index=True)

    with tab_b:
        df_b = pd.DataFrame([
            {
                "Track ID": p.get("track_id"),
                "Player Name": p.get("name"),
                "Position": p.get("role"),
                "Jersey Number": f"#{p['jersey_number']}" if p.get("jersey_number") is not None else "⚠️ Unreadable / Occluded (Left Blank)",
                "Initial X (m)": p.get("pitch_x"),
                "Initial Y (m)": p.get("pitch_y"),
                "OCR Status": "✅ Confirmed via OCR" if p.get("jersey_number") is not None else "⚪ Blank Marker (No Number)"
            }
            for p in team_b_players
        ])
        st.dataframe(df_b, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
