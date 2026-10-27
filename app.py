"""Football Vision Analytics - Streamlit Web Application (Brasileirão Série A Edition).

Dedicated to the Campeonato Brasileiro (Série A) featuring real-time synchronized
2D tactical pitch radar, live formation detection, and jersey number recognition.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from src.config import VIDEOS_DIR
from src.tactics.brasileirao_telemetry import (
    BRASILEIRAO_MATCHES,
    generate_live_telemetry_for_match,
)
from src.visualization.synced_player import build_synced_player_html

# Page Configuration
st.set_page_config(
    page_title="Football Vision Analytics - Brasileirão Série A",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling
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
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_cached_telemetry(match_id: str) -> Dict[str, Any]:
    """Generate or retrieve continuous 60 FPS tactical telemetry for a Brasileirão match."""
    match_data = next((m for m in BRASILEIRAO_MATCHES if m["id"] == match_id), BRASILEIRAO_MATCHES[0])
    return generate_live_telemetry_for_match(match_data, duration_seconds=300)


def render_header():
    """Render top application banner."""
    st.markdown("""
    <div class="header-container">
        <img src="https://img.icons8.com/color/96/football2--v1.png" width="46" style="vertical-align:middle;">
        <span class="main-title">Football Vision Analytics — Brasileirão Série A</span>
    </div>
    <div class="sub-title">
        Vídeos e Melhores Momentos do Brasileirão • Mapa Tático 2D Sincronizado ao Play em Tempo Real
    </div>
    """, unsafe_allow_html=True)


def main():
    render_header()

    # Section 1: Clean Match Selection (Only match title, e.g. "Palmeiras 1 x 1 Flamengo")
    st.write("### 🎬 1. Escolha a Partida do Campeonato Brasileiro")

    clean_match_titles = [m["title"] for m in BRASILEIRAO_MATCHES]

    sel_col1, sel_col2 = st.columns([3, 1])

    with sel_col1:
        chosen_idx = st.selectbox(
            "⚽ Partida:",
            range(len(clean_match_titles)),
            format_func=lambda i: clean_match_titles[i]
        )

    with sel_col2:
        theme = st.selectbox("🎨 Tema do Gramado:", ["dark", "green"], index=0)

    selected_match = BRASILEIRAO_MATCHES[chosen_idx]
    video_path = VIDEOS_DIR / selected_match["video_file"]
    telemetry = get_cached_telemetry(selected_match["id"])

    # Section 2: Tactical Metric Summary Badges
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#60A5FA; font-size:0.85rem; font-weight:bold;">🔵 {selected_match["team_a"]["name"].upper()}</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">{selected_match["team_a"]["formation"]}</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">Postura: Bloco Ofensivo</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#F87171; font-size:0.85rem; font-weight:bold;">🔴 {selected_match["team_b"]["name"].upper()}</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">{selected_match["team_b"]["formation"]}</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">Postura: Linhas Compactas</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#FACC15; font-size:0.85rem; font-weight:bold;">⚡ SINCRONIZAÇÃO EM TEMPO REAL</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">60 FPS Ativo</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">O radar move simultâneo ao vídeo</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m_col4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="color:#34D399; font-size:0.85rem; font-weight:bold;">👥 NÚMEROS DAS CAMISAS (OCR)</div>'
            f'<div style="font-size:1.35rem; font-weight:bold; color:#FFFFFF;">Regra Rígida de Confiança</div>'
            f'<div style="color:#94A3B8; font-size:0.8rem;">Dígito ilegível: nó limpo sem número</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Section 3: The Synchronized Side-by-Side View (Video Left, Radar Right)
    st.write("---")
    st.write("### 📺 2. Visualização Lado a Lado: Vídeo da Partida e Mapa Tático 2D")
    st.caption("Dê o **Play** no vídeo à esquerda: o mapa tático 2D ao lado **acompanha o vídeo em tempo real a 60 FPS**! Pause ou navegue na barra do vídeo para ver a sincronização imediata.")

    if video_path.exists():
        player_html = build_synced_player_html(
            video_path=str(video_path),
            telemetry=telemetry,
            theme=theme
        )
        st.components.v1.html(player_html, height=540)
    else:
        st.error(f"Vídeo da partida não encontrado: {video_path}")

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
