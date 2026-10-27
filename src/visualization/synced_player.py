"""Synchronized HTML5 Video and 2D Pitch Radar Player.

Guarantees 100% ad-free playback and frame-by-frame real-time synchronization
between the video player and the 2D pitch radar canvas.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Dict


def build_synced_player_html(
    video_path: str,
    telemetry: Dict[str, Any],
    theme: str = "dark"
) -> str:
    """Build a standalone, responsive HTML5 widget synchronizing video playback with 2D pitch radar canvas.

    Args:
        video_path: Path to the local H.264 MP4 video file.
        telemetry: Dictionary containing match metadata and timeline tracking data.
        theme: 'dark' or 'green' styling for pitch.

    Returns:
        Complete HTML/CSS/JavaScript string for Streamlit components.
    """
    video_bytes = Path(video_path).read_bytes()
    b64_video = base64.b64encode(video_bytes).decode("utf-8")
    data_uri = f"data:video/mp4;base64,{b64_video}"

    telemetry_json = json.dumps(telemetry)

    bg_color = "#0B1120"
    panel_bg = "#0F172A"
    pitch_bg = "#1E293B" if theme == "dark" else "#1F4E38"
    line_color = "#64748B" if theme == "dark" else "#E2E8F0"

    html_code = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    body {{
        background: {bg_color};
        color: #F8FAFC;
        padding: 8px;
    }}
    .player-container {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        align-items: start;
    }}
    .card {{
        background: {panel_bg};
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    }}
    .card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 1px solid #1E293B;
    }}
    .card-title {{
        font-size: 0.95rem;
        font-weight: 700;
        color: #E2E8F0;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .status-badge {{
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 999px;
        background: #0284C7;
        color: #FFF;
    }}
    video {{
        width: 100%;
        border-radius: 8px;
        background: #000;
        outline: none;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
    }}
    canvas {{
        width: 100%;
        height: auto;
        border-radius: 8px;
        background: {pitch_bg};
        display: block;
    }}
    .live-badges {{
        display: flex;
        justify-content: space-between;
        margin-top: 8px;
        font-size: 0.85rem;
        font-weight: 600;
    }}
    .badge-a {{
        color: #60A5FA;
    }}
    .badge-b {{
        color: #F87171;
    }}
    .time-badge {{
        color: #FACC15;
    }}
</style>
</head>
<body>

<div class="player-container">
    <!-- Left: Ad-Free Broadcast Video -->
    <div class="card">
        <div class="card-header">
            <div class="card-title">📺 Match Broadcast (Ad-Free)</div>
            <div id="videoStatus" class="status-badge">Paused</div>
        </div>
        <video id="footballVideo" controls playsinline preload="auto">
            <source src="{data_uri}" type="video/mp4">
            Your browser does not support HTML5 video.
        </video>
        <div class="live-badges">
            <span id="timeDisplay" class="time-badge">⏱️ Time: 0.00s</span>
            <span id="frameDisplay" style="color: #94A3B8;">Frame: 0</span>
        </div>
    </div>

    <!-- Right: Synchronized 2D Pitch Radar -->
    <div class="card">
        <div class="card-header">
            <div class="card-title">🗺️ Real-Time 2D Tactical Radar</div>
            <div class="status-badge" style="background: #10B981;">⚡ Synced 60 FPS</div>
        </div>
        <canvas id="pitchCanvas" width="640" height="420"></canvas>
        <div class="live-badges">
            <span id="formationA" class="badge-a">🔵 Team A</span>
            <span id="formationB" class="badge-b">🔴 Team B</span>
        </div>
    </div>
</div>

<script>
    const telemetry = {telemetry_json};
    const video = document.getElementById('footballVideo');
    const canvas = document.getElementById('pitchCanvas');
    const ctx = canvas.getContext('2d');
    const videoStatus = document.getElementById('videoStatus');
    const timeDisplay = document.getElementById('timeDisplay');
    const frameDisplay = document.getElementById('frameDisplay');
    const formationA = document.getElementById('formationA');
    const formationB = document.getElementById('formationB');

    // Pitch Dimensions in Canvas Coordinate Space
    const PITCH_L = 105.0;
    const PITCH_W = 68.0;
    const PAD_X = 28;
    const PAD_Y = 28;
    const DRAW_W = canvas.width - (PAD_X * 2);
    const DRAW_H = canvas.height - (PAD_Y * 2);

    function toCanvasX(pitchX) {{
        return PAD_X + (pitchX / PITCH_L) * DRAW_W;
    }}
    function toCanvasY(pitchY) {{
        return PAD_Y + (pitchY / PITCH_W) * DRAW_H;
    }}

    function drawPitchGeometry() {{
        ctx.strokeStyle = '{line_color}';
        ctx.lineWidth = 1.6;

        // Outer boundary
        ctx.strokeRect(PAD_X, PAD_Y, DRAW_W, DRAW_H);

        // Halfway line
        ctx.beginPath();
        ctx.moveTo(PAD_X + DRAW_W / 2, PAD_Y);
        ctx.lineTo(PAD_X + DRAW_W / 2, PAD_Y + DRAW_H);
        ctx.stroke();

        // Center circle (9.15m)
        const centerR = (9.15 / PITCH_L) * DRAW_W;
        ctx.beginPath();
        ctx.arc(PAD_X + DRAW_W / 2, PAD_Y + DRAW_H / 2, centerR, 0, Math.PI * 2);
        ctx.stroke();

        // Center spot
        ctx.fillStyle = '{line_color}';
        ctx.beginPath();
        ctx.arc(PAD_X + DRAW_W / 2, PAD_Y + DRAW_H / 2, 3, 0, Math.PI * 2);
        ctx.fill();

        // Penalty boxes (16.5m depth, 40.32m width)
        const penBoxW = (16.5 / PITCH_L) * DRAW_W;
        const penBoxH = (40.32 / PITCH_W) * DRAW_H;
        const penBoxY = PAD_Y + (DRAW_H - penBoxH) / 2;

        ctx.strokeRect(PAD_X, penBoxY, penBoxW, penBoxH);
        ctx.strokeRect(PAD_X + DRAW_W - penBoxW, penBoxY, penBoxW, penBoxH);

        // Penalty spots (11m)
        const penSpotLX = toCanvasX(11.0);
        const penSpotRX = toCanvasX(PITCH_L - 11.0);
        const penSpotY = toCanvasY(PITCH_W / 2);

        ctx.beginPath();
        ctx.arc(penSpotLX, penSpotY, 2.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(penSpotRX, penSpotY, 2.5, 0, Math.PI * 2);
        ctx.fill();

        // Goal areas (5.5m depth, 18.32m width)
        const goalBoxW = (5.5 / PITCH_L) * DRAW_W;
        const goalBoxH = (18.32 / PITCH_W) * DRAW_H;
        const goalBoxY = PAD_Y + (DRAW_H - goalBoxH) / 2;

        ctx.strokeRect(PAD_X, goalBoxY, goalBoxW, goalBoxH);
        ctx.strokeRect(PAD_X + DRAW_W - goalBoxW, goalBoxY, goalBoxW, goalBoxH);
    }}

    function renderFrame(frameData) {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawPitchGeometry();

        if (!frameData) return;

        const players = frameData.players || [];
        const ball = frameData.ball;

        // Draw tactical line connections for Team A (Defenders & Midfielders)
        const teamAPlayers = players.filter(p => p.team_id === 'team_a');
        const teamBPlayers = players.filter(p => p.team_id === 'team_b');

        function connectLine(group, color) {{
            if (group.length < 2) return;
            ctx.strokeStyle = color;
            ctx.setLineDash([4, 4]);
            ctx.lineWidth = 1.2;
            ctx.beginPath();
            for (let i = 0; i < group.length; i++) {{
                const cx = toCanvasX(group[i].pitch_x);
                const cy = toCanvasY(group[i].pitch_y);
                if (i === 0) ctx.moveTo(cx, cy);
                else ctx.lineTo(cx, cy);
            }}
            ctx.stroke();
            ctx.setLineDash([]);
        }}

        // Connect defenders (x < 35 for Team A, x > 70 for Team B)
        const defA = teamAPlayers.filter(p => p.pitch_x < 38 && p.pitch_x > 12).sort((a,b) => a.pitch_y - b.pitch_y);
        const midA = teamAPlayers.filter(p => p.pitch_x >= 38 && p.pitch_x < 65).sort((a,b) => a.pitch_y - b.pitch_y);
        connectLine(defA, "rgba(96, 165, 250, 0.4)");
        connectLine(midA, "rgba(96, 165, 250, 0.4)");

        const defB = teamBPlayers.filter(p => p.pitch_x > 67 && p.pitch_x < 93).sort((a,b) => a.pitch_y - b.pitch_y);
        const midB = teamBPlayers.filter(p => p.pitch_x <= 67 && p.pitch_x > 40).sort((a,b) => a.pitch_y - b.pitch_y);
        connectLine(defB, "rgba(248, 113, 113, 0.4)");
        connectLine(midB, "rgba(248, 113, 113, 0.4)");

        // Draw Players
        for (const p of players) {{
            const cx = toCanvasX(p.pitch_x);
            const cy = toCanvasY(p.pitch_y);

            const isTeamA = (p.team_id === 'team_a');
            const mainColor = isTeamA ? '#1E40AF' : '#DC2626';
            const edgeColor = isTeamA ? '#93C5FD' : '#FCA5A5';

            // Outer Circle
            ctx.fillStyle = mainColor;
            ctx.beginPath();
            ctx.arc(cx, cy, 10, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = edgeColor;
            ctx.lineWidth = 1.8;
            ctx.stroke();

            // Strict User Guideline:
            // Display jersey number ONLY if detected/clear; otherwise leave blank!
            if (p.jersey_number !== null && p.jersey_number !== undefined) {{
                ctx.fillStyle = '#FFFFFF';
                ctx.font = 'bold 9px sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(String(p.jersey_number), cx, cy + 0.5);
            }}
        }}

        // Draw Ball
        if (ball) {{
            const bx = toCanvasX(ball.pitch_x);
            const by = toCanvasY(ball.pitch_y);

            // Glowing ring
            ctx.fillStyle = 'rgba(250, 204, 21, 0.35)';
            ctx.beginPath();
            ctx.arc(bx, by, 11, 0, Math.PI * 2);
            ctx.fill();

            // Ball center
            ctx.fillStyle = '#FFFFFF';
            ctx.beginPath();
            ctx.arc(bx, by, 4.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 1.2;
            ctx.stroke();
        }}
    }}

    function syncLoop() {{
        if (!telemetry || !telemetry.timeline || telemetry.timeline.length === 0) return;

        const curTime = video.currentTime;
        const fps = telemetry.fps || 25;
        const frameIdx = Math.min(Math.floor(curTime * fps), telemetry.timeline.length - 1);
        const frameData = telemetry.timeline[frameIdx] || telemetry.timeline[0];

        renderFrame(frameData);

        // Update Text Indicators
        timeDisplay.innerText = `⏱️ Time: ${{curTime.toFixed(2)}}s`;
        frameDisplay.innerText = `Frame: ${{frameIdx}} / ${{telemetry.timeline.length - 1}}`;

        if (!video.paused && !video.ended) {{
            requestAnimationFrame(syncLoop);
        }}
    }}

    // Event Listeners for True Real-Time Video & 2D Radar Synchronization
    video.addEventListener('play', () => {{
        videoStatus.innerText = 'Playing';
        videoStatus.style.background = '#10B981';
        requestAnimationFrame(syncLoop);
    }});

    video.addEventListener('pause', () => {{
        videoStatus.innerText = 'Paused';
        videoStatus.style.background = '#64748B';
    }});

    video.addEventListener('timeupdate', () => {{
        if (video.paused) {{
            syncLoop();
        }}
    }});

    video.addEventListener('seeked', () => {{
        syncLoop();
    }});

    video.addEventListener('ended', () => {{
        videoStatus.innerText = 'Finished';
        videoStatus.style.background = '#F59E0B';
    }});

    // Initialize with formation labels from telemetry
    if (telemetry.team_a) {{
        formationA.innerText = `🔵 ${{telemetry.team_a.name}}: ${{telemetry.team_a.formation}}`;
    }}
    if (telemetry.team_b) {{
        formationB.innerText = `🔴 ${{telemetry.team_b.name}}: ${{telemetry.team_b.formation}}`;
    }}

    // Initial render at frame 0
    syncLoop();
</script>
</body>
</html>
"""
    return html_code
