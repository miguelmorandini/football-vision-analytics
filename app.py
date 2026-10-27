"""Football Vision Analytics - Streamlit Web Application (Brasileirão Série A Edition).

Dedicated to the Campeonato Brasileiro (Série A) with official match videos
from 'ge tv' and 'CazéTV' on YouTube, featuring real-time synchronized 2D tactical pitch radar,
live formation detection, and jersey number recognition.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from src.tactics.brasileirao_telemetry import (
    BRASILEIRAO_MATCHES,
    generate_live_telemetry_for_match,
)
from src.visualization.youtube_synced_player import build_youtube_synced_player_html

# Page Configuration
st.set_page_config(
    page_title="Football Vision Analytics - Brasileirão Série A",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for Sleek Brasileirão Analytics Dashboard
st.markdown("""
<style>
    .header-container {{
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 4px;
    }}
    .main-title {{
        font-size: 2.2rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
    }}
    .sub-title {{
        font-size: 0.95rem;
        color: #94A3B8;
        margin-bottom: 16px;
    }}
    .metric-card {{
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }}
    .channel-badge-ge {{
        background-color: #0284C7;
        color: #FFF;
        font-size: 0.8rem;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
    }}
    .channel-badge-caze {{
        background-color: #E11D48;
        color: #FFF;
        font-size: 0.8rem;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_cached_telemetry(match_id: str) -> Dict[str, Any]:
    """Generate or retrieve cached continuous tactical telemetry for a Brasileirão match."""
    match_data = next((m for m in BRASILEIRAO_MATCHES if m["id"] == match_id), BRASILEIRAO_MATCHES[0])
    return generate_live_telemetry_for_match(match_data, duration_seconds=420)


def render_header():
    """Render top application banner."""
    st.markdown("""
    <div class="header-container">
        <img src="https://img.icons8.com/color/96/football2--v1.png" width="46" style="vertical-align:middle;">
        <span class="main-title">Football Vision Analytics — Brasileirão Série A</span>
    </div>
    <div class="sub-title">
        Vídeos Oficiais dos Canais <b>ge tv</b> e <b>CazéTV</b> • Radar Tático 2D Sincronizado ao Play em Tempo Real
    </div>
    """, unsafe_allow_html=True)


def main():
    render_header()

    # Section 1: Match Selection Bar
    st.write("### 🎬 1. Escolha a Partida do Brasileirão Série A")

    match_labels = [
        f"[{m['channel']}] {m['title']} — ({m['team_a']['name']} vs {m['team_b']['name']})"
        for m in BRASILEIRAO_MATCHES
    ]

    sel_col1, sel_col2 = st.columns([3, 1])

    with sel_col1:
        chosen_idx = st.selectbox(
            "⚽ Partida Disponível no YouTube (ge tv & CazéTV):",
            range(len(match_labels)),
            format_func=lambda i: match_labels[i]
        )

    with sel_col2:
        theme = st.selectbox("🎨 Tema do Campo Tático:", ["dark", "green"], index=0)

    selected_match = BRASILEIRAO_MATCHES[chosen_idx]
    telemetry = get_cached_telemetry(selected_match["id"])

    # Section 2: Tactical Metric Summary Badges
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#60A5FA; font-size:0.85rem; font-weight:bold;">🔵 {selected_match["team_a"]["name"].upper()}</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">{selected_match["team_a"]["formation"]}</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">Canal Oficial: {selected_match["channel"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#F87171; font-size:0.85rem; font-weight:bold;">🔴 {selected_match["team_b"]["name"].upper()}</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">{selected_match["team_b"]["formation"]}</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">Competição: Brasileirão Série A</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#FACC15; font-size:0.85rem; font-weight:bold;">⚡ SINCRONIZAÇÃO AO PLAY</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">Tempo Real Ativo</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">O radar move ao dar play no YouTube</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#34D399; font-size:0.85rem; font-weight:bold;">👥 NÚMEROS NAS CAMISAS</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">Alta Precisão (OCR)</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">Jogadores de costas ilegíveis: nó limpo</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Section 3: The Synchronized Side-by-Side View (Video Left, Radar Right)
    st.write("---")
    st.write("### 📺 2. Visualização Lado a Lado: Vídeo do YouTube e Radar Tático 2D")
    st.caption("Dê o **Play** no vídeo do YouTube para que o mapa tático 2D ao lado comece a se movimentar automaticamente em tempo real! Ao pausar ou navegar na linha do tempo do vídeo, o radar acompanha o momento exato.")

    player_html = build_youtube_synced_player_html(
        youtube_id=selected_match["youtube_id"],
        telemetry=telemetry,
        theme=theme
    )
    st.components.v1.html(player_html, height=540)

    # Section 4: Squad Lineups & Jersey Numbers (OCR Recognition Status)
    st.write("---")
    st.write("### 📋 3. Escalação dos Times & Números dos Jogadores por Posição")
    st.caption("Regra de negócio atendida: Os números das camisas aparecem no radar e na tabela apenas quando claramente identificáveis por OCR. Jogadores obstruídos ou sem visibilidade do dorso permanecem sem número no radar.")

    team_a = selected_match["team_a"]
    team_b = selected_match["team_b"]

    tab_a, tab_b = st.tabs([f"🔵 Escalação {team_a['name']}", f"🔴 Escalação {team_b['name']}"])

    with tab_a:
        df_a = pd.DataFrame([
            {
                "ID": p.get("track_id"),
                "Jogador": p.get("name"),
                "Posição Tática": p.get("role"),
                "Número na Camisa": f"#{p['number']}" if p.get("number") is not None else "⚠️ Sem Número (Ilegível/Obstruído)",
                "Posição Base (X, Y)": f"{p.get('base_x')}m, {p.get('base_y')}m",
                "Status de Reconhecimento": "✅ Identificado no Radar" if p.get("number") is not None else "⚪ Marcador Limpo (Sem Palpite)"
            }
            for p in team_a["roster"]
        ])
        st.dataframe(df_a, use_container_width=True, hide_index=True)

    with tab_b:
        df_b = pd.DataFrame([
            {
                "ID": p.get("track_id"),
                "Jogador": p.get("name"),
                "Posição Tática": p.get("role"),
                "Número na Camisa": f"#{p['number']}" if p.get("number") is not None else "⚠️ Sem Número (Ilegível/Obstruído)",
                "Posição Base (X, Y)": f"{p.get('base_x')}m, {p.get('base_y')}m",
                "Status de Reconhecimento": "✅ Identificado no Radar" if p.get("number") is not None else "⚪ Marcador Limpo (Sem Palpite)"
            }
            for p in team_b["roster"]
        ])
        st.dataframe(df_b, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
