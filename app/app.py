"""Punto de entrada de Box Plots F1: navegación principal (st.navigation)."""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
for _p in (str(ROOT_DIR), str(APP_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

from components.theme import render_footer

st.set_page_config(page_title="Box Plots F1", page_icon="🏁", layout="wide")

PAGES_DIR = APP_DIR / "pages"

# Nota: la sección predictiva (pages/07_Predicciones_IA.py) queda reservada para la v2.
navegacion = st.navigation(
    [
        st.Page(str(APP_DIR / "inicio.py"), title="Pit Wall · Telemetría", icon="🏁", default=True),
        st.Page(str(PAGES_DIR / "05_Mundiales_GP.py"), title="Archivo de Temporadas", icon="🏆"),
        st.Page(str(PAGES_DIR / "06_Duelos_y_Fiabilidad.py"), title="Duelos H2H & Fiabilidad", icon="⚔️"),
        st.Page(str(PAGES_DIR / "08_Mapa_y_Salon_Fama.py"), title="Circuitos & Leyendas", icon="🏛️"),
        st.Page(str(PAGES_DIR / "09_Glosario_y_Reglamento_2026.py"), title="Glosario & 2026", icon="📖"),
        st.Page(str(PAGES_DIR / "10_Raceboxd.py"), title="Raceboxd", icon="🏎️"),
        st.Page(str(PAGES_DIR / "11_Predicciones_Construccion.py"), title="Predicciones (En Pits)", icon="🎲"),
    ]
)
navegacion.run()
render_footer()
