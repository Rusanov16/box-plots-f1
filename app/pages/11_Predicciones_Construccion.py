"""Página 11: Predicciones (En Pits)."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = APP_DIR.parent
for _p in (str(ROOT_DIR), str(APP_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

from components.theme import inject_editorial_theme, render_crt_header

st.set_page_config(page_title="Predicciones (En Pits) — Box Plots F1", layout="wide")
inject_editorial_theme()
render_crt_header(
    canal="CH 07 · EN PITS",
    titulo="🎲 Predicciones (En Pits)",
    subtitulo="Módulo en boxes — próximamente disponible.",
)

img_path = APP_DIR / "assets" / "gato_mecanico.jpg"
img_html = ""
if img_path.exists():
    b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
    img_html = (
        f'<div style="background:#F2EAD7; border:1px solid #D8D0BE; border-radius:8px; padding:10px;">'
        f'<img src="data:image/jpeg;base64,{b64}" style="width:100%; max-height:340px; object-fit:contain; '
        f'border-radius:6px; display:block; margin:0 auto;" /></div>'
    )

st.markdown(
    f'<div style="background:#FFFFFF; border:1px solid #DDD6C5; border-top:4px solid #E11D24; '
    f'border-radius:10px; padding:24px 26px; max-width:820px; margin:16px auto; '
    f'display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:24px; align-items:center;">'
    f'{img_html}'
    f'<div>'
    f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.74rem; color:#E11D24; font-weight:700; letter-spacing:0.14em; text-transform:uppercase;">'
    f'● BOX BOX</div>'
    f'<div style="font-family:\'Plus Jakarta Sans\',sans-serif; font-size:2.05rem; font-weight:800; color:#1C1C1C; margin:6px 0 12px 0; line-height:1.1;">'
    f'En Pits</div>'
    f'<p style="font-family:\'IBM Plex Mono\',monospace; font-size:0.86rem; color:#5A564E; margin:0; line-height:1.6;">'
    f'Nuestro jefe de mecánicos sigue apretando las últimas tuercas antes de liberar esta sección a pista.</p>'
    f'</div></div>',
    unsafe_allow_html=True,
)
