"""Football Vision Analytics - Streamlit Web Application.

Designed for Databricks Apps and Local Execution.
Provides real-time computer vision analysis, 2D tactical pitch radar mapping,
formation detection (4-3-3, 4-4-2, etc.), jersey number OCR, and ScoreBat free API video feeds.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.api.scorebat import ScoreBatClient
from src.config import DEMO_DIR, TEAM_COLORS
from src.tactics.formation_detector import FormationDetector
from src.tactics.pitch_visualizer import PitchVisualizer

# Page Configuration
st.set_page_config(
    page_title="Football Vision Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .formation-badge {
        font-size: 1.1rem;
        font-weight: bold;
        padding: 6px 12px;
        border-radius: 6px;
        display: inline-block;
    }
    .badge-teama {
        background-color: #1E40AF;
        color: #FFFFFF;
        border: 1px solid #60A5FA;
    }
    .badge-teamb {
        background-color: #DC2626;
        color: #FFFFFF;
        border: 1px solid #F87171;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_scorebat_matches() -> List[Dict[str, Any]]:
    """Fetch recent matches from ScoreBat API client."""
    client = ScoreBatClient()
    return client.get_matches()


@st.cache_data
def load_demo_match() -> Dict[str, Any]:
    """Load pre-computed demo match telemetry dataset."""
    demo_file = DEMO_DIR / "match_demo.json"
    if demo_file.exists():
        with open(demo_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def render_sidebar():
    """Render application sidebar with navigation and settings."""
    st.sidebar.image("https://img.icons8.com/color/96/football2--v1.png", width=64)
    st.sidebar.title("Football Vision")
    st.sidebar.caption("Computer Vision & Tactical Tracking")

    mode = st.sidebar.radio(
        "Navigation",
        [
            "📊 Tactical Match Center",
            "⚡ Video AI Processor",
            "🌐 ScoreBat Highlights (Free API)"
        ]
    )

    st.sidebar.divider()
    st.sidebar.subheader("Pitch Visualization Settings")
    pitch_theme = st.sidebar.selectbox("Pitch Style", ["dark", "green"], index=0)
    show_lines = st.sidebar.checkbox("Draw Tactical Chains (Lines)", value=True)
    show_numbers = st.sidebar.checkbox("Show Jersey Numbers / IDs", value=True)

    st.sidebar.divider()
    st.sidebar.info(
        "💡 **Databricks Apps Ready**\n\n"
        "Runs on Databricks serverless compute with standard `streamlit run app.py`."
    )

    return {
        "mode": mode,
        "pitch_theme": pitch_theme,
        "show_lines": show_lines,
        "show_numbers": show_numbers
    }


def page_tactical_match_center(settings: Dict[str, Any]):
    """Render the main split-screen tactical dashboard."""
    demo_data = load_demo_match()
    if not demo_data or "timeline" not in demo_data:
        st.error("Demo match dataset not found. Please run the data generator script.")
        return

    timeline = demo_data["timeline"]
    total_frames = len(timeline)

    st.markdown('<div class="main-title">📊 Tactical Match Center</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-title">{demo_data.get("match_title", "Match Analysis")} • '
        f'{demo_data.get("competition", "Competition")}</div>',
        unsafe_allow_html=True
    )

    # Frame Playback Timeline Control
    st.write("##### ⏱️ Match Frame Playback Timeline")
    frame_idx = st.slider(
        "Scrub through video frames",
        min_value=0,
        max_value=total_frames - 1,
        value=15,
        step=1,
        format="Frame %d"
    )

    current_frame = timeline[frame_idx]
    timestamp = current_frame.get("timestamp_sec", 0.0)
    players = current_frame.get("players", [])
    ball = current_frame.get("ball")

    # Filter out numbers if user unchecked them
    rendered_players = []
    for p in players:
        p_copy = dict(p)
        if not settings["show_numbers"]:
            p_copy["jersey_number"] = None
            p_copy["track_id"] = None
        rendered_players.append(p_copy)

    # Compute tactical metrics
    f_detector = FormationDetector()
    team_a_players = [p for p in players if p.get("team_id") == "team_a"]
    team_b_players = [p for p in players if p.get("team_id") == "team_b"]

    metrics_a = f_detector.detect_formation(team_a_players, attacking_left_to_right=True)
    metrics_b = f_detector.detect_formation(team_b_players, attacking_left_to_right=False)

    # Formation Header Indicators
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#60A5FA;font-size:0.85rem;">TEAM A FORMATION</div>'
            f'<div style="font-size:1.3rem;font-weight:bold;color:#FFFFFF;">{metrics_a.formation_name}</div>'
            f'<div style="color:#94A3B8;font-size:0.8rem;">Width: {metrics_a.compactness_width}m • Depth: {metrics_a.compactness_depth}m</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#F87171;font-size:0.85rem;">TEAM B FORMATION</div>'
            f'<div style="font-size:1.3rem;font-weight:bold;color:#FFFFFF;">{metrics_b.formation_name}</div>'
            f'<div style="color:#94A3B8;font-size:0.8rem;">Width: {metrics_b.compactness_width}m • Depth: {metrics_b.compactness_depth}m</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#FACC15;font-size:0.85rem;">BALL LOCATION (2D)</div>'
            f'<div style="font-size:1.3rem;font-weight:bold;color:#FFFFFF;">'
            f'X: {ball.get("pitch_x", 0.0)}m | Y: {ball.get("pitch_y", 0.0)}m</div>'
            f'<div style="color:#94A3B8;font-size:0.8rem;">Pitch Sector: Midfield Attacking 3rd</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#34D399;font-size:0.85rem;">TRACKED ATHLETES</div>'
            f'<div style="font-size:1.3rem;font-weight:bold;color:#FFFFFF;">{len(players)} Players</div>'
            f'<div style="color:#94A3B8;font-size:0.8rem;">Frame: {frame_idx} • Time: {timestamp:.2f}s</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Split View: Left (Broadcast / Player View) & Right (2D Tactical Pitch Radar)
    st.write("---")
    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.subheader("📺 Broadcast Tactical Camera")
        # Visual representation of the broadcast camera view with detected players
        st.markdown("""
        <div style="background:#0F172A; border:1px solid #334155; border-radius:8px; padding:16px; text-align:center;">
            <p style="color:#94A3B8; font-size:0.9rem; margin-bottom:12px;">
                Simulated 1080p Tactical Broadcast Frame • Bounding Boxes & AI Tracking Active
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Tactical summary cards
        st.write("#### 🛡️ Defensive Line Heights")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.metric("Team A Defensive Line", f"{metrics_a.team_centroid[0]:.1f}m", delta="High Press")
        with d_col2:
            st.metric("Team B Defensive Line", f"{105.0 - metrics_b.team_centroid[0]:.1f}m", delta="-Medium Block")

    with col_right:
        st.subheader("🗺️ 2D Tactical Pitch Radar (Minimap)")
        visualizer = PitchVisualizer(theme=settings["pitch_theme"])
        fig = visualizer.render(
            players=rendered_players,
            ball=ball,
            metrics_a=metrics_a,
            metrics_b=metrics_b,
            show_tactical_lines=settings["show_lines"]
        )
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    # Player Roster and Jersey Number OCR Table
    st.write("---")
    st.subheader("👥 Tracked Players & Jersey Number OCR Status")
    st.caption("Numbers are displayed only when confidently recognized via OCR. Unclear or front-facing players remain without number.")

    tab_team_a, tab_team_b = st.tabs(["🔵 Team A Roster", "🔴 Team B Roster"])

    with tab_team_a:
        df_a = pd.DataFrame([
            {
                "Track ID": p.get("track_id"),
                "Player Name": p.get("name", "Player"),
                "Position": p.get("role", "Field"),
                "Jersey Number": f"#{p['jersey_number']}" if p.get("jersey_number") is not None else "⚠️ Not Legible (Left Blank)",
                "Pitch X (m)": p.get("pitch_x"),
                "Pitch Y (m)": p.get("pitch_y"),
                "Detection Conf": f"{p.get('confidence', 0.9) * 100:.0f}%"
            }
            for p in team_a_players
        ])
        st.dataframe(df_a, use_container_width=True, hide_index=True)

    with tab_team_b:
        df_b = pd.DataFrame([
            {
                "Track ID": p.get("track_id"),
                "Player Name": p.get("name", "Player"),
                "Position": p.get("role", "Field"),
                "Jersey Number": f"#{p['jersey_number']}" if p.get("jersey_number") is not None else "⚠️ Not Legible (Left Blank)",
                "Pitch X (m)": p.get("pitch_x"),
                "Pitch Y (m)": p.get("pitch_y"),
                "Detection Conf": f"{p.get('confidence', 0.9) * 100:.0f}%"
            }
            for p in team_b_players
        ])
        st.dataframe(df_b, use_container_width=True, hide_index=True)


def page_video_processor():
    """Render the upload and custom video processing tab."""
    st.markdown('<div class="main-title">⚡ Video AI Processor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Upload and analyze soccer match footage with the end-to-end computer vision pipeline</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Football Match Video (MP4 / MOV)", type=["mp4", "mov"])

    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        max_frames = st.slider("Max Frames to Process", min_value=30, max_value=300, value=90, step=30)
    with p_col2:
        frame_stride = st.slider("Frame Stride (Sample Rate)", min_value=1, max_value=5, value=2)
    with p_col3:
        conf_thresh = st.slider("Detection Confidence", min_value=0.2, max_value=0.8, value=0.35, step=0.05)

    if uploaded_file is not None:
        st.success(f"Video uploaded: **{uploaded_file.name}** ({uploaded_file.size / 1024 / 1024:.2f} MB)")

        if st.button("🚀 Run Computer Vision Pipeline", type="primary"):
            temp_path = Path("temp_videos") / uploaded_file.name
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            progress_bar = st.progress(0.0)
            status_text = st.empty()

            try:
                from src.pipeline import FootballVideoPipeline
                pipeline = FootballVideoPipeline()

                def update_progress(pct: float, msg: str):
                    progress_bar.progress(pct)
                    status_text.text(msg)

                telemetry = pipeline.process_video(
                    video_path=str(temp_path),
                    max_frames=max_frames,
                    frame_stride=frame_stride,
                    progress_callback=update_progress
                )

                st.success(f"Analysis Complete! Processed {telemetry['processed_frames']} frames.")
                st.json(telemetry["timeline"][:2])
            except Exception as e:
                st.error(f"Error during video processing: {e}")
                st.info("Ensure OpenCV, PyTorch, and YOLO models are loaded.")


def page_scorebat_explorer():
    """Render the ScoreBat Free Football Video API highlights browser."""
    st.markdown('<div class="main-title">🌐 ScoreBat Highlights Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Watch official match highlights and goals from top worldwide leagues via free API feeds</div>', unsafe_allow_html=True)

    client = ScoreBatClient()
    matches = client.get_matches()
    competitions = client.get_competitions()

    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        query = st.text_input("🔍 Search by Team or Match Title", placeholder="e.g. Madrid, Arsenal, Chelsea...")
    with f_col2:
        comp_filter = st.selectbox("🏆 Filter by Competition", ["All Competitions"] + competitions)

    filtered_matches = client.search_matches(
        query=query if query else None,
        competition=comp_filter if comp_filter != "All Competitions" else None,
        limit=24
    )

    st.write(f"Showing **{len(filtered_matches)}** match highlights:")

    # Grid of matches (3 columns)
    cols = st.columns(3)
    for idx, match in enumerate(filtered_matches):
        col = cols[idx % 3]
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-weight:bold; font-size:1.05rem; color:#F8FAFC;">{match.get('title', 'Match')}</div>
                <div style="color:#94A3B8; font-size:0.85rem; margin-bottom:8px;">
                    {match.get('competition', {}).get('name', 'Football Match')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            thumbnail = match.get("thumbnail")
            if thumbnail:
                st.image(thumbnail, use_container_width=True)

            with st.expander("▶️ Watch Highlights"):
                embed_html = match.get("embed", "")
                if embed_html:
                    st.components.v1.html(embed_html, height=420)
                else:
                    st.info("Embedded highlights player unavailable for this match.")


def main():
    """Main application controller."""
    settings = render_sidebar()

    if settings["mode"] == "📊 Tactical Match Center":
        page_tactical_match_center(settings)
    elif settings["mode"] == "⚡ Video AI Processor":
        page_video_processor()
    elif settings["mode"] == "🌐 ScoreBat Highlights (Free API)":
        page_scorebat_explorer()


if __name__ == "__main__":
    main()
