"""Pestaña de comparativa entre pilotos y Mapa de Calor del Circuito (SIE-F1)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components.charts import grafico_mapa_calor_circuito, grafico_ritmo_vueltas
from src.etl.openf1_service import extraer_mapa_calor_openf1


def _mejor_vuelta_piloto(laps_df: pd.DataFrame, piloto: str) -> pd.Series | None:
    col_p = "id_piloto" if "id_piloto" in laps_df.columns else "Driver"
    sub = laps_df[laps_df[col_p] == piloto].copy()
    if sub.empty:
        return None
    col_t = "tiempo_lap" if "tiempo_lap" in sub.columns else "LapTime"
    sub["_s"] = sub[col_t].apply(
        lambda v: v.total_seconds() if hasattr(v, "total_seconds") else pd.to_numeric(v, errors="coerce")
    )
    validas = sub[sub["_s"].notna() & (sub["_s"] > 0)]
    if validas.empty:
        return None
    return validas.loc[validas["_s"].idxmin()]


def render_comparativa_circuito(laps_df: pd.DataFrame, metadata: dict | None = None) -> None:
    """Comparativa cara a cara entre 2 pilotos + Mapa de Calor del Circuito por GP."""
    if laps_df is None or laps_df.empty:
        st.info("Carga una sesión (ej. desde OpenF1 API) para comparar pilotos y ver el mapa de calor.")
        return

    col_p = "id_piloto" if "id_piloto" in laps_df.columns else "Driver"
    pilotos = sorted(laps_df[col_p].dropna().unique().tolist())
    if not pilotos:
        st.warning("No hay pilotos disponibles en la sesión cargada.")
        return

    c1, c2, c3 = st.columns(3)
    p1 = c1.selectbox("Piloto 1", pilotos, index=0)
    p2 = c2.selectbox("Piloto 2", pilotos, index=min(1, len(pilotos) - 1))
    metrica_label = c3.selectbox(
        "Métrica del Mapa de Calor",
        ["Velocidad (km/h)", "Acelerador (%)", "Marcha"],
    )
    mapa_metrica = {"Velocidad (km/h)": "speed", "Acelerador (%)": "throttle", "Marcha": "n_gear"}
    metrica = mapa_metrica[metrica_label]

    # 1. Comparativa de ritmo entre los 2 pilotos
    sub_comp = laps_df[laps_df[col_p].isin([p1, p2])]
    fig_comp = grafico_ritmo_vueltas(
        sub_comp,
        excluir_anomalias=True,
        titulo=f"Comparativa de Ritmo por Vuelta: {p1} vs {p2}",
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # 2. Mapa de Calor del Circuito (vuelta rápida de cada piloto vía OpenF1)
    session_key = (metadata or {}).get("session_key")
    if not session_key or "DriverNumber" not in laps_df.columns or "LapStartDate" not in laps_df.columns:
        st.info(
            "El mapa de calor del circuito requiere coordenadas `(x, y)` de la sesión. "
            "Carga el GP desde **OpenF1 API** para generarlo automáticamente."
        )
        return

    if st.button("Generar Mapa de Calor del Circuito (Vuelta Rápida)", type="primary"):
        col_m1, col_m2 = st.columns(2)
        for col_ui, piloto in ((col_m1, p1), (col_m2, p2)):
            mejor = _mejor_vuelta_piloto(laps_df, piloto)
            if mejor is None or pd.isna(mejor.get("LapStartDate")):
                col_ui.warning(f"Sin vuelta rápida con timestamp para {piloto}.")
                continue
            with st.spinner(f"Descargando trazado y telemetría de {piloto}..."):
                try:
                    tel_df = extraer_mapa_calor_openf1(
                        session_key=int(session_key),
                        driver_number=int(mejor["DriverNumber"]),
                        lap_start_iso=str(mejor["LapStartDate"]),
                        lap_duration_s=float(mejor["_s"]),
                    )
                    fig_map = grafico_mapa_calor_circuito(
                        tel_df,
                        metrica=metrica,
                        titulo=f"{piloto} — Vuelta {int(mejor['numero_vuelta'])} ({mejor['_s']:.3f}s)",
                    )
                    col_ui.plotly_chart(fig_map, use_container_width=True)
                except Exception as exc:
                    col_ui.error(f"Error generando mapa para {piloto}: {exc}")
