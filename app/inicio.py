"""Inicio de Box Plots F1: portada editorial + monitor de telemetría de sesiones OpenF1."""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
for _p in (str(ROOT_DIR), str(APP_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import streamlit as st

from components.theme import (
    inject_editorial_theme,
    render_blueprint_banner,
    render_crt_header,
    render_racer_hero,
)
from tabs.comparativa_circuito import render_comparativa_circuito
from tabs.estrategia_neumaticos import render_estrategia_neumaticos
from tabs.resumen_sesion import render_resumen_sesion
from src.etl.openf1_service import extraer_sesion_openf1, listar_sesiones_openf1
from src.etl.transformer import transformar_vueltas

_ORDEN_SESIONES = {
    "Practice 1": 1, "Practice 2": 2, "Practice 3": 3,
    "Sprint Qualifying": 4, "Sprint Shootout": 4, "Sprint": 5,
    "Qualifying": 6, "Race": 7,
}
_NOMBRE_SESION_ES = {
    "Practice 1": "Libres 1", "Practice 2": "Libres 2", "Practice 3": "Libres 3",
    "Sprint Qualifying": "Clasif. Sprint", "Sprint Shootout": "Clasif. Sprint",
    "Sprint": "Sprint", "Qualifying": "Clasificación", "Race": "Carrera",
}


# ---------------------------------------------------------------------------
# Caché de llamadas a OpenF1 (compartida entre todos los usuarios del servidor)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _sesiones_temporada(anio: int) -> list[dict]:
    return listar_sesiones_openf1(int(anio))


@st.cache_data(ttl=24 * 3600, show_spinner=False, max_entries=40)
def _sesion_normalizada(session_key: int) -> tuple[pd.DataFrame, dict, list]:
    datos = extraer_sesion_openf1(int(session_key))
    df_norm, alertas = transformar_vueltas(datos["laps"])
    return df_norm, datos["metadata"], alertas


def _agrupar_por_gp(sesiones: list[dict]) -> dict[str, list[dict]]:
    grupos: dict[str, list[dict]] = {}
    for s in sesiones:
        pais = s.get("country_name") or ""
        lugar = s.get("location") or s.get("circuit_short_name") or ""
        etiqueta = f"{pais} · {lugar}" if lugar and lugar != pais else pais
        grupos.setdefault(etiqueta, []).append(s)
    for etiqueta in grupos:
        grupos[etiqueta].sort(key=lambda s: _ORDEN_SESIONES.get(s.get("session_name", ""), 9))
    return grupos


inject_editorial_theme()
render_blueprint_banner(titulo="BOX PLOTS F1 — TRAZANDO LA PISTA")
render_racer_hero(headline="CADA SEGUNDO CUENTA · 1950–2026")

# ---------------------------------------------------------------------------
# Selector de sesión (solo OpenF1)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Selector de Sesión")
    st.caption("Fuente: **OpenF1** · temporadas 2023 en adelante")
    anio = st.selectbox("Temporada", [2026, 2025, 2024, 2023], index=2)

    try:
        sesiones = _sesiones_temporada(int(anio))
    except Exception:
        sesiones = []
        st.warning("No fue posible conectar con OpenF1. Intenta nuevamente en unos segundos.")

    grupos = _agrupar_por_gp(sesiones)
    if not grupos:
        st.info(f"Aún no hay sesiones publicadas para {anio}.")
    else:
        gp_sel = st.selectbox(f"Gran Premio ({len(grupos)})", list(grupos.keys()))
        opciones_ses = {
            _NOMBRE_SESION_ES.get(s.get("session_name", ""), s.get("session_name", "")): s["session_key"]
            for s in grupos[gp_sel]
        }
        nombres = list(opciones_ses.keys())
        ses_sel = st.radio(
            "Sesión",
            nombres,
            index=nombres.index("Carrera") if "Carrera" in nombres else len(nombres) - 1,
        )

        if st.button("▶ Cargar sesión", type="primary", width="stretch"):
            with st.status(f"Sintonizando {gp_sel} — {ses_sel}…", expanded=False) as estado:
                try:
                    estado.write("Conectando con OpenF1…")
                    df_norm, metadata, alertas = _sesion_normalizada(int(opciones_ses[ses_sel]))
                    estado.write("Normalizando tiempos y stints…")
                    st.session_state["laps_activas"] = df_norm
                    st.session_state["metadata_activa"] = metadata
                    st.session_state["alertas_activas"] = alertas
                    st.session_state["etiqueta_activa"] = f"{gp_sel} — {ses_sel} {anio}"
                    estado.update(
                        label=f"Sesión lista · {len(df_norm)} vueltas", state="complete", expanded=False
                    )
                except Exception:
                    estado.update(label="No se pudo cargar la sesión", state="error")
                    st.error("OpenF1 no respondió correctamente. Prueba de nuevo o elige otra sesión.")

laps_activas = st.session_state.get("laps_activas", pd.DataFrame())
metadata_activa = st.session_state.get("metadata_activa", {})
etiqueta = st.session_state.get("etiqueta_activa")

render_crt_header(
    canal="CH 91 · LIVE TIMING" if etiqueta else "CH 91 · SIN SEÑAL",
    titulo=f"MONITOR DE TELEMETRÍA — {etiqueta.upper()}" if etiqueta else "MONITOR DE TELEMETRÍA — ESPERANDO SEÑAL",
    subtitulo=(
        f"{len(laps_activas)} vueltas cronometradas · Pilotos: {laps_activas['Driver'].nunique() if 'Driver' in laps_activas else '—'}"
        if etiqueta
        else "Elige temporada, Gran Premio y sesión en el panel izquierdo y pulsa «Cargar sesión»."
    ),
)

tab1, tab2, tab3 = st.tabs(
    ["📊 Resumen y Ritmo", "🗺️ Comparativa y Mapa de Calor", "🛞 Estrategia y Degradación"]
)
with tab1:
    render_resumen_sesion(laps_activas)
with tab2:
    render_comparativa_circuito(laps_activas, metadata=metadata_activa)
with tab3:
    render_estrategia_neumaticos(laps_activas)
