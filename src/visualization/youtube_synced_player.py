"""YouTube-Synchronized 2D Pitch Radar Player for Brasileirão Série A.

Features dual-layer synchronization:
1. Native YouTube postMessage & IFrame API listeners (detects video play/pause/seek events).
2. Integrated high-precision 60 FPS canvas clock that animates the 2D pitch radar
   continuously in sync with video playback.
3. Interactive control buttons (Play/Pause/Scrubber) that simultaneously control
   both the YouTube player and the 2D pitch radar.
"""

from __future__ import annotations

import json
from typing import Any, Dict


def build_youtube_synced_player_html(
    youtube_id: str,
    telemetry: Dict[str, Any],
    theme: str = "dark"
) -> str:
    """Build an HTML/JS widget coupling the YouTube player with real-time 2D pitch radar."""
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
        padding: 6px;
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
        padding: 3px 10px;
        border-radius: 999px;
        background: #0284C7;
        color: #FFF;
        transition: background 0.3s ease;
    }}
    .video-wrapper {{
        position: relative;
        padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
        height: 0;
        overflow: hidden;
        border-radius: 8px;
        background: #000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }}
    .video-wrapper iframe {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border: 0;
    }}
    canvas {{
        width: 100%;
        height: auto;
        border-radius: 8px;
        background: {pitch_bg};
        display: block;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
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
    .controls-panel {{
        margin-top: 10px;
        background: #020617;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 10px 14px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .btn {{
        background: #2563EB;
        color: white;
        border: none;
        padding: 7px 14px;
        font-size: 0.85rem;
        font-weight: 700;
        border-radius: 6px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: background 0.2s ease, transform 0.1s ease;
    }}
    .btn:hover {{
        background: #1D4ED8;
    }}
    .btn:active {{
        transform: scale(0.97);
    }}
    .btn-pause {{
        background: #475569;
    }}
    .btn-pause:hover {{
        background: #334155;
    }}
    .scrubber {{
        flex-grow: 1;
        cursor: pointer;
        accent-color: #38BDF8;
    }}
</style>
</head>
<body>

<div class="player-container">
    <!-- Left: YouTube Video Player -->
    <div class="card">
        <div class="card-header">
            <div class="card-title">📺 Transmissão Oficial no YouTube</div>
            <div id="videoStatus" class="status-badge">Pronto para Tocar</div>
        </div>
        <div class="video-wrapper">
            <iframe id="ytIframe"
                    src="https://www.youtube.com/embed/{youtube_id}?enablejsapi=1&version=3&autoplay=0&rel=0&playsinline=1"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen>
            </iframe>
        </div>
        <div class="live-badges">
            <span id="timeDisplay" class="time-badge">⏱️ Tempo: 0.00s</span>
            <span id="syncNotice" style="color: #34D399;">⚡ Sincronização 60 FPS Ativa</span>
        </div>
    </div>

    <!-- Right: 2D Tactical Pitch Radar -->
    <div class="card">
        <div class="card-header">
            <div class="card-title">🗺️ Mapa Tático 2D em Tempo Real</div>
            <div id="radarStatus" class="status-badge" style="background: #10B981;">⚡ Sincronizado ao Vídeo</div>
        </div>
        <canvas id="pitchCanvas" width="640" height="420"></canvas>
        <div class="live-badges">
            <span id="formationA" class="badge-a">🔵 Time A</span>
            <span id="formationB" class="badge-b">🔴 Time B</span>
        </div>
    </div>
</div>

<!-- Interactive Synced Controls Bar -->
<div class="controls-panel">
    <button id="btnPlay" class="btn">▶️ Play Tático & Vídeo</button>
    <button id="btnPause" class="btn btn-pause">⏸️ Pausar</button>
    <span style="font-size:0.8rem; color:#94A3B8; font-weight:600;">Sincronia:</span>
    <input type="range" id="timeScrubber" class="scrubber" min="0" max="300" step="0.1" value="0">
    <span id="scrubberTime" style="font-size:0.85rem; color:#F8FAFC; font-weight:bold; min-width:60px;">0.0s</span>
</div>

<script>
    const telemetry = {telemetry_json};
    const canvas = document.getElementById('pitchCanvas');
    const ctx = canvas.getContext('2d');
    const ytIframe = document.getElementById('ytIframe');
    const videoStatus = document.getElementById('videoStatus');
    const radarStatus = document.getElementById('radarStatus');
    const timeDisplay = document.getElementById('timeDisplay');
    const formationA = document.getElementById('formationA');
    const formationB = document.getElementById('formationB');
    const btnPlay = document.getElementById('btnPlay');
    const btnPause = document.getElementById('btnPause');
    const timeScrubber = document.getElementById('timeScrubber');
    const scrubberTime = document.getElementById('scrubberTime');

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

        // Tactical connection chains
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

        const defA = teamAPlayers.filter(p => p.pitch_x < 36 && p.pitch_x > 10).sort((a,b) => a.pitch_y - b.pitch_y);
        const midA = teamAPlayers.filter(p => p.pitch_x >= 36 && p.pitch_x < 65).sort((a,b) => a.pitch_y - b.pitch_y);
        connectLine(defA, "rgba(96, 165, 250, 0.45)");
        connectLine(midA, "rgba(96, 165, 250, 0.45)");

        const defB = teamBPlayers.filter(p => p.pitch_x > 69 && p.pitch_x < 95).sort((a,b) => a.pitch_y - b.pitch_y);
        const midB = teamBPlayers.filter(p => p.pitch_x <= 69 && p.pitch_x > 40).sort((a,b) => a.pitch_y - b.pitch_y);
        connectLine(defB, "rgba(248, 113, 113, 0.45)");
        connectLine(midB, "rgba(248, 113, 113, 0.45)");

        // Draw Players
        for (const p of players) {{
            const cx = toCanvasX(p.pitch_x);
            const cy = toCanvasY(p.pitch_y);

            const isTeamA = (p.team_id === 'team_a');
            const mainColor = isTeamA ? '#1E40AF' : '#DC2626';
            const edgeColor = isTeamA ? '#93C5FD' : '#FCA5A5';

            ctx.fillStyle = mainColor;
            ctx.beginPath();
            ctx.arc(cx, cy, 10, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = edgeColor;
            ctx.lineWidth = 1.8;
            ctx.stroke();

            // Strict user guideline:
            // Display jersey number ONLY if confirmed/readable; otherwise leave node blank!
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

            ctx.fillStyle = 'rgba(250, 204, 21, 0.35)';
            ctx.beginPath();
            ctx.arc(bx, by, 11, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#FFFFFF';
            ctx.beginPath();
            ctx.arc(bx, by, 4.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 1.2;
            ctx.stroke();
        }}
    }}

    // Real-Time Playback Synchronization Engine
    let isPlaying = false;
    let playbackTime = 0.0;
    let lastAnimTimestamp = null;
    let animationFrameId = null;

    function syncPitchAtTime(curTime) {{
        if (!telemetry || !telemetry.timeline || telemetry.timeline.length === 0) return;

        const fps = telemetry.fps || 25;
        const frameIdx = Math.min(Math.floor(curTime * fps), telemetry.timeline.length - 1);
        const frameData = telemetry.timeline[frameIdx] || telemetry.timeline[0];

        renderFrame(frameData);

        timeDisplay.innerText = `⏱️ Tempo: ${{curTime.toFixed(1)}}s`;
        scrubberTime.innerText = `${{curTime.toFixed(1)}}s`;
        timeScrubber.value = curTime;
    }}

    function animationTick(currentTimestamp) {{
        if (!isPlaying) return;

        if (lastAnimTimestamp !== null) {{
            const deltaSec = (currentTimestamp - lastAnimTimestamp) / 1000.0;
            playbackTime += deltaSec;
            if (telemetry.duration && playbackTime >= telemetry.duration) {{
                playbackTime = 0.0; // Loop seamlessly
            }}
            syncPitchAtTime(playbackTime);
        }}

        lastAnimTimestamp = currentTimestamp;
        animationFrameId = requestAnimationFrame(animationTick);
    }}

    function startPlayback() {{
        if (isPlaying) return;
        isPlaying = true;
        lastAnimTimestamp = performance.now();
        animationFrameId = requestAnimationFrame(animationTick);

        videoStatus.innerText = 'Em Reprodução (Sincronizado)';
        videoStatus.style.background = '#10B981';
        radarStatus.innerText = '⚡ Radar Movendo em Tempo Real';
        radarStatus.style.background = '#10B981';

        // Send command to YouTube iframe to start video
        sendYouTubeCommand('playVideo');
    }}

    function pausePlayback() {{
        isPlaying = false;
        if (animationFrameId) {{
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }}
        lastAnimTimestamp = null;

        videoStatus.innerText = 'Pausado';
        videoStatus.style.background = '#64748B';
        radarStatus.innerText = 'Pausado';
        radarStatus.style.background = '#64748B';

        sendYouTubeCommand('pauseVideo');
    }}

    function seekToTime(seconds) {{
        playbackTime = parseFloat(seconds);
        syncPitchAtTime(playbackTime);
        sendYouTubeCommand('seekTo', [playbackTime, true]);
    }}

    function sendYouTubeCommand(funcName, args = []) {{
        if (ytIframe && ytIframe.contentWindow) {{
            ytIframe.contentWindow.postMessage(JSON.stringify({{
                'event': 'command',
                'func': funcName,
                'args': args
            }}), '*');
        }}
    }}

    // Dual-Layer postMessage Listener from YouTube IFrame
    window.addEventListener('message', function(event) {{
        try {{
            const data = (typeof event.data === 'string') ? JSON.parse(event.data) : event.data;
            if (data && data.event === 'infoDelivery' && data.info) {{
                if (data.info.currentTime !== undefined) {{
                    const ytTime = parseFloat(data.info.currentTime);
                    if (Math.abs(ytTime - playbackTime) > 0.8) {{
                        playbackTime = ytTime;
                    }}
                }}
                if (data.info.playerState !== undefined) {{
                    if (data.info.playerState === 1 && !isPlaying) {{ // Playing
                        startPlayback();
                    }} else if (data.info.playerState === 2 && isPlaying) {{ // Paused
                        pausePlayback();
                    }}
                }}
            }}
        }} catch(e) {{}}
    }});

    // Button event listeners
    btnPlay.addEventListener('click', () => {{
        startPlayback();
    }});

    btnPause.addEventListener('click', () => {{
        pausePlayback();
    }});

    timeScrubber.addEventListener('input', (e) => {{
        seekToTime(e.target.value);
    }});

    // Initialize labels
    if (telemetry.team_a) {{
        formationA.innerText = `🔵 ${{telemetry.team_a.name}}: ${{telemetry.team_a.formation}}`;
    }}
    if (telemetry.team_b) {{
        formationB.innerText = `🔴 ${{telemetry.team_b.name}}: ${{telemetry.team_b.formation}}`;
    }}

    // Render frame 0 immediately
    syncPitchAtTime(0.0);
</script>
</body>
</html>
"""
    return html_code
