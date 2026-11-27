"""Sistema visual editorial Motorsport + Monitor TV RCA XL-100 CRT para Box Plots F1."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"

# Paleta Editorial (Maqueta RCA XL-91 + Motor Sport + RACER 1993)
PAPER_CREAM = "#F7F4EC"
INK_CHARCOAL = "#1C1C1C"
INK_MUTED = "#5A564E"
BAR_CHARCOAL = "#2A2A2A"
BAR_WARM_GRAY = "#6E695E"
MCLAREN_RED = "#E11D24"
SENNA_YELLOW = "#FFD100"
MOTORSPORT_GREEN = "#277B47"
RACER_NAVY = "#28368C"
OSD_GREEN = "#6CFF7A"


def _img_to_b64(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")


def inject_editorial_theme() -> None:
    """Inyecta fuentes Google, paleta papel crema y estilos editoriales/CRT globales."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=Oswald:wght@600;700&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');

        :root {{
            --paper-cream: {PAPER_CREAM};
            --ink-charcoal: {INK_CHARCOAL};
            --ink-muted: {INK_MUTED};
            --mclaren-red: {MCLAREN_RED};
            --senna-yellow: {SENNA_YELLOW};
            --motorsport-green: {MOTORSPORT_GREEN};
            --osd-green: {OSD_GREEN};
        }}

        /* Fondo editorial papel crema */
        .stApp {{
            background-color: var(--paper-cream);
            color: var(--ink-charcoal);
            font-family: 'Inter', sans-serif;
        }}

        /* Sidebar oscuro elegante estilo consola F1 */
        [data-testid="stSidebar"] {{
            background-color: #161B26 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}
        [data-testid="stSidebar"] * {{
            color: #EAE5D9 !important;
        }}
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background-color: #232A3B !important;
            color: #FFFFFF !important;
            border-color: rgba(255, 255, 255, 0.16) !important;
        }}
        [data-testid="stSidebar"] div.stButton > button {{
            background-color: #232A3B !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }}
        [data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
            background-color: var(--mclaren-red) !important;
            border-color: var(--mclaren-red) !important;
            color: #FFFFFF !important;
        }}

        h1, h2, h3, .stSubheader {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            color: var(--ink-charcoal) !important;
            letter-spacing: -0.02em;
        }}

        /* Contraste de widgets, etiquetas, pestañas y botones sobre papel crema */
        [data-testid="stAppViewContainer"] section.main label,
        [data-testid="stAppViewContainer"] section.main .stCheckbox p,
        [data-testid="stAppViewContainer"] section.main .stRadio p,
        [data-testid="stAppViewContainer"] section.main .stMarkdown p,
        [data-testid="stAppViewContainer"] section.main [data-testid="stWidgetLabel"] p {{
            color: var(--ink-charcoal) !important;
        }}

        /* Pestañas (st.tabs) legibles en carbón y rojo McLaren al seleccionar */
        [data-testid="stAppViewContainer"] section.main button[data-baseweb="tab"] {{
            color: #2A2A2A !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            opacity: 0.85;
        }}
        [data-testid="stAppViewContainer"] section.main button[data-baseweb="tab"]:hover {{
            color: var(--mclaren-red) !important;
            opacity: 1;
        }}
        [data-testid="stAppViewContainer"] section.main button[data-baseweb="tab"][aria-selected="true"] {{
            color: var(--mclaren-red) !important;
            font-weight: 700 !important;
            opacity: 1;
        }}

        /* Botones con alto contraste (carbón / rojo McLaren) */
        [data-testid="stAppViewContainer"] section.main div.stButton > button {{
            background-color: #1C1C1C !important;
            color: #F7F4EC !important;
            border: 1px solid #1C1C1C !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-weight: 600 !important;
        }}
        [data-testid="stAppViewContainer"] section.main div.stButton > button:hover {{
            background-color: var(--mclaren-red) !important;
            border-color: var(--mclaren-red) !important;
            color: #FFFFFF !important;
        }}
        [data-testid="stAppViewContainer"] section.main div.stButton > button[kind="primary"] {{
            background-color: var(--mclaren-red) !important;
            border-color: var(--mclaren-red) !important;
            color: #FFFFFF !important;
        }}
        [data-testid="stAppViewContainer"] section.main div.stButton > button p {{
            color: inherit !important;
        }}

        /* Métricas estilo telemetría monoespaciada */
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.55);
            border: 1px solid rgba(28, 28, 28, 0.14);
            border-top: 3px solid var(--mclaren-red);
            border-radius: 6px;
            padding: 12px 14px;
        }}
        [data-testid="stMetricValue"] {{
            font-family: 'IBM Plex Mono', monospace !important;
            color: var(--ink-charcoal) !important;
            font-weight: 700 !important;
        }}
        [data-testid="stMetricLabel"] {{
            font-family: 'IBM Plex Mono', monospace !important;
            text-transform: uppercase;
            font-size: 0.72rem !important;
            letter-spacing: 0.05em;
            color: var(--ink-muted) !important;
        }}

        /* Contenedor Plotly con marco editorial sutil */
        .stPlotlyChart {{
            background: rgba(247, 244, 236, 0.65);
            border: 1px solid rgba(28, 28, 28, 0.14);
            border-radius: 10px;
            padding: 8px 6px 4px 6px;
            box-shadow: inset 0 0 18px rgba(28, 24, 18, 0.05);
        }}

        /* Barra Chevron McLaren 1991 */
        .mclaren-chevron-bar {{
            height: 7px;
            width: 100%;
            margin: 10px 0 14px 0;
            background: linear-gradient(
                118deg,
                var(--mclaren-red) 0%,
                var(--mclaren-red) 34%,
                var(--paper-cream) 34%,
                var(--paper-cream) 36.5%,
                var(--mclaren-red) 36.5%,
                var(--mclaren-red) 42%,
                var(--paper-cream) 42%,
                var(--paper-cream) 100%
            );
            border-bottom: 1px solid rgba(28, 28, 28, 0.18);
        }}

        /* Portada estilo Revista RACER (1993) */
        .racer-cover {{
            border: 2px solid #1C1C1C;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 14px 32px rgba(28, 24, 18, 0.18);
            margin-bottom: 18px;
            background: #141414;
        }}
        .racer-top-strip {{
            background: {RACER_NAVY};
            color: #FFFFFF;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 5px 14px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .racer-masthead {{
            background: {MCLAREN_RED};
            padding: 8px 18px 6px 18px;
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            flex-wrap: wrap;
            border-bottom: 3px solid #141414;
        }}
        .racer-masthead-title {{
            font-family: 'Oswald', sans-serif;
            font-style: italic;
            font-weight: 700;
            font-size: clamp(2.4rem, 5vw, 4.1rem);
            line-height: 0.95;
            color: #FFFFFF;
            letter-spacing: 0.03em;
            text-shadow: 3px 3px 0 rgba(0, 0, 0, 0.25);
        }}
        .racer-masthead-sub {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            color: #FFE8E8;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }}
        .racer-hero-stage {{
            position: relative;
            min-height: 290px;
            background-size: cover;
            background-position: center 45%;
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            padding: 22px 24px;
        }}
        .racer-hero-overlay {{
            position: absolute;
            inset: 0;
            background: linear-gradient(95deg, rgba(12,12,12,0.82) 0%, rgba(12,12,12,0.38) 48%, rgba(12,12,12,0.18) 100%);
        }}
        .racer-hero-copy {{
            position: relative;
            z-index: 2;
            max-width: 560px;
        }}
        .racer-headline {{
            font-family: 'Oswald', sans-serif;
            font-weight: 700;
            font-size: clamp(2.0rem, 4vw, 3.2rem);
            line-height: 0.96;
            color: {SENNA_YELLOW};
            text-transform: uppercase;
            text-shadow: 2px 2px 0 #141414;
            margin: 0 0 8px 0;
        }}
        .racer-deck {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #F7F4EC;
            font-size: 0.96rem;
            font-weight: 600;
            margin: 0;
            text-shadow: 0 1px 4px rgba(0,0,0,0.8);
        }}
        .racer-bottom-strip {{
            background: {RACER_NAVY};
            color: #F7F4EC;
            padding: 9px 18px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            border-top: 2px solid #141414;
        }}

        /* Encabezado Monitor TV RCA XL-100 CRT */
        .rca-crt-header {{
            background: linear-gradient(145deg, #3A2518 0%, #22150D 60%, #161616 100%);
            border: 2px solid #8C8574;
            border-radius: 12px;
            padding: 12px 18px;
            margin: 8px 0 12px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.22), inset 0 1px 1px rgba(255,230,200,0.18);
        }}
        .rca-crt-title {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #F7F4EC;
            font-weight: 700;
            font-size: 1.05rem;
            margin: 0;
        }}
        .rca-crt-sub {{
            font-family: 'IBM Plex Mono', monospace;
            color: #C8C0AA;
            font-size: 0.75rem;
            margin: 2px 0 0 0;
        }}
        .rca-osd-pill {{
            background: rgba(16, 22, 16, 0.92);
            border: 1px solid rgba(108, 255, 122, 0.55);
            color: {OSD_GREEN};
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.76rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 4px;
            letter-spacing: 0.08em;
            text-shadow: 0 0 6px rgba(108, 255, 122, 0.45);
        }}

        /* Banner Técnico Editorial (Estilo Lámina Ferrari F2002) */
        .blueprint-banner {{
            display: grid;
            grid-template-columns: 42% 58%;
            background: {PAPER_CREAM};
            border: 1px solid rgba(28, 28, 28, 0.16);
            border-bottom: 3px solid {INK_CHARCOAL};
            border-radius: 6px;
            overflow: hidden;
            margin-bottom: 18px;
            min-height: 260px;
            box-shadow: 0 10px 26px rgba(28, 24, 18, 0.08);
        }}
        .blueprint-art {{
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            border-right: 1px solid rgba(28, 28, 28, 0.18);
            min-height: 260px;
        }}
        .blueprint-copy {{
            padding: 24px 30px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
        }}
        .blueprint-top-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .blueprint-kicker {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            color: {INK_MUTED};
            text-transform: uppercase;
        }}
        .blueprint-title {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-style: italic;
            font-weight: 800;
            font-size: clamp(1.5rem, 2.7vw, 2.35rem);
            line-height: 1.12;
            color: #C8102E;
            text-transform: uppercase;
            margin: 14px 0 10px 0;
        }}
        .blueprint-meta {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.76rem;
            color: {INK_MUTED};
            border-top: 1px solid rgba(28, 28, 28, 0.14);
            padding-top: 10px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
        }}
        @media (max-width: 780px) {{
            .blueprint-banner {{
                grid-template-columns: 1fr;
            }}
            .blueprint-art {{
                min-height: 180px;
                border-right: none;
                border-bottom: 1px solid rgba(28, 28, 28, 0.18);
            }}
            .blueprint-copy {{
                padding: 16px 18px;
            }}
            .racer-hero-stage {{
                min-height: 210px;
                padding: 16px;
            }}
            .rca-crt-header {{
                padding: 10px 14px;
            }}
            .stApp {{
                overflow-x: hidden;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_blueprint_banner(
    titulo: str = "BOX PLOTS F1 — TRAZANDO LA PISTA",
    subtitulo: str = "76 TEMPORADAS · RESULTADOS, TELEMETRÍA, DUELOS Y ESTRATEGIA",
) -> None:
    """Renderiza el banner editorial con lámina técnica del Ferrari F2002 a la izquierda y título rojo itálica."""
    img_b64 = _img_to_b64(ASSETS_DIR / "blueprint_f2002.jpg")
    art_style = (
        f"background-image: url('data:image/jpeg;base64,{img_b64}');"
        if img_b64
        else "background: #EFECE2;"
    )
    sil_b64 = _img_to_b64(ASSETS_DIR / "f1_silhouette.png")
    f1_logo = (
        f'<img src="data:image/png;base64,{sil_b64}" alt="F1" '
        f'style="height: 34px; width: auto; mix-blend-mode: multiply; opacity: 0.92;" />'
        if sil_b64
        else ""
    )
    st.markdown(
        f"""
        <div class="blueprint-banner">
            <div class="blueprint-art" style="{art_style}"></div>
            <div class="blueprint-copy">
                <div class="blueprint-top-row">
                    <span class="blueprint-kicker">ARCHIVO TÉCNICO · 1950–2026</span>
                    {f1_logo}
                </div>
                <div class="blueprint-title">{titulo}</div>
                <div class="blueprint-meta">
                    <span>{subtitulo}</span>
                    <span>FUENTES: ERGAST / JOLPICA · OPENF1</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_racer_hero(
    headline: str = "CADA SEGUNDO CUENTA · 1950–2026",
    deck: str = "Telemetría en vivo, archivo histórico de mundiales, duelos cabeza a cabeza y estrategia de neumáticos.",
    issue_tag: str = "EDICIÓN ARCHIVO XL-91",
) -> None:
    """Renderiza la portada estilo revista RACER (1993) con la foto de Senna en McLaren."""
    img_b64 = _img_to_b64(ASSETS_DIR / "hero_senna_mclaren.jpg")
    bg_style = (
        f"background-image: url('data:image/jpeg;base64,{img_b64}');"
        if img_b64
        else "background: linear-gradient(120deg, #1E1E1E 0%, #3A1214 100%);"
    )
    st.markdown(
        f"""
        <div class="racer-cover">
            <div class="racer-top-strip">
                <span>BOX PLOTS F1 · REVISTA DE DATOS DE FÓRMULA 1</span>
                <span>{issue_tag}</span>
            </div>
            <div class="racer-masthead">
                <div class="racer-masthead-title">SIE-F1 RACER</div>
                <div class="racer-masthead-sub">STATISTICAL MOTORSPORT MAGAZINE · TELEMETRY &amp; ARCHIVE</div>
            </div>
            <div class="racer-hero-stage" style="{bg_style}">
                <div class="racer-hero-overlay"></div>
                <div class="racer-hero-copy">
                    <div class="racer-headline">{headline}</div>
                    <p class="racer-deck">{deck}</p>
                </div>
            </div>
            <div class="racer-bottom-strip">
                <span>🏆 ARCHIVO DE TEMPORADAS</span>
                <span>⚔️ DUELOS H2H &amp; FIABILIDAD</span>
                <span>🏛️ CIRCUITOS &amp; LEYENDAS</span>
                <span>📖 GLOSARIO &amp; 2026</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer(
    firma: str = "RUSSANOV & NINA MOTORSPORT",
    subtexto: str = "BOX PLOTS F1 · TRAZANDO LA PISTA · OPENF1 & JOLPICA",
) -> None:
    """Renderiza un colofón editorial limpio al pie de la página."""
    st.markdown(
        f'<div style="margin-top:42px; padding-top:14px; border-top:1px solid rgba(28,28,28,0.16); '
        f'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; '
        f'font-family:\'IBM Plex Mono\',monospace; font-size:0.72rem; color:#5A564E; letter-spacing:0.08em;">'
        f'<span><strong style="color:#1C1C1C;">{firma}</strong> · <span style="color:#E11D24;">●</span> 2026</span>'
        f'<span>{subtexto}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_crt_header(canal: str, titulo: str, subtitulo: str = "") -> None:
    """Renderiza un encabezado de monitor TV RCA XL-100 CRT con OSD verde fósforo."""
    st.markdown(
        f"""
        <div class="rca-crt-header">
            <div>
                <div class="rca-crt-title">{titulo}</div>
                <div class="rca-crt-sub">{subtitulo}</div>
            </div>
            <div class="rca-osd-pill">● {canal}</div>
        </div>
        <div class="mclaren-chevron-bar"></div>
        """,
        unsafe_allow_html=True,
    )


def estilizar_plotly_editorial(
    fig: go.Figure,
    titulo: Optional[str] = None,
    altura: Optional[int] = None,
) -> go.Figure:
    """Aplica estética editorial Motorsport: fondo transparente, IBM Plex Mono y grid punteado suave."""
    layout_kwargs = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Mono, monospace", color=INK_CHARCOAL, size=11),
        title_font=dict(family="Plus Jakarta Sans, sans-serif", color=INK_CHARCOAL, size=16),
        margin=dict(l=16, r=76, t=56, b=24),
        legend=dict(
            bgcolor="rgba(247,244,236,0.75)",
            bordercolor="rgba(28,28,28,0.12)",
            borderwidth=1,
            font=dict(family="IBM Plex Mono, monospace", size=10),
        ),
    )
    if titulo is not None:
        layout_kwargs["title"] = titulo
    if altura is not None:
        layout_kwargs["height"] = altura

    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(28,28,28,0.11)",
        griddash="dot",
        zeroline=False,
        linecolor="rgba(28,28,28,0.25)",
        tickfont=dict(family="IBM Plex Mono, monospace", size=10, color=INK_CHARCOAL),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(28,28,28,0.11)",
        griddash="dot",
        zeroline=False,
        linecolor="rgba(28,28,28,0.25)",
        tickfont=dict(family="IBM Plex Mono, monospace", size=10, color=INK_CHARCOAL),
    )
    return fig


def grafico_barras_editorial(
    df: pd.DataFrame,
    categoria_col: str,
    valor_col: str,
    titulo: str,
    sufijo_texto: str = "",
    color_lider: str = MCLAREN_RED,
    color_resto: str = BAR_CHARCOAL,
    formato_valor: str = ".1f",
    altura_min: int = 320,
) -> go.Figure:
    """Barras horizontales ordenadas de mayor a menor con color con intención solo en el líder."""
    data = df[[categoria_col, valor_col]].dropna().copy()
    data = data.sort_values(valor_col, ascending=True)  # ascending=True pone el mayor arriba en orientación 'h'

    n = len(data)
    colores = [color_resto] * n
    if n > 0:
        colores[-1] = color_lider  # el último en orden ascendente es el líder (arriba)

    etiquetas = [f"{v:{formato_valor}}{sufijo_texto}" for v in data[valor_col]]
    altura = max(altura_min, 32 * n + 90)

    fig = go.Figure(
        go.Bar(
            x=data[valor_col],
            y=data[categoria_col],
            orientation="h",
            marker=dict(color=colores, line=dict(width=0)),
            text=etiquetas,
            textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=11, color=INK_CHARCOAL),
            cliponaxis=False,
            hovertemplate=f"<b>%{{y}}</b><br>{valor_col}: %{{x:{formato_valor}}}{sufijo_texto}<extra></extra>",
        )
    )
    estilizar_plotly_editorial(fig, titulo=titulo, altura=altura)
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showticklabels=False, showgrid=True)
    return fig
