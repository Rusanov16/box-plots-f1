"""Pestaña de resumen de sesión y ritmo de vueltas (SIE-F1)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components.charts import grafico_ritmo_vueltas


def render_resumen_sesion(laps_df: pd.DataFrame) -> None:
    """Renderiza KPIs, selector de filtro de ritmo y tabla de vueltas."""
    if laps_df is None or laps_df.empty:
        st.info("Selecciona o carga una sesión con vueltas para visualizar el resumen.")
        return

    col_piloto = "id_piloto" if "id_piloto" in laps_df.columns else "Driver"
    total_vueltas = len(laps_df)
    total_pilotos = int(laps_df[col_piloto].nunique()) if col_piloto in laps_df.columns else 0
    total_anomalias = int(laps_df["es_anomalia"].sum()) if "es_anomalia" in laps_df.columns else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total de vueltas", total_vueltas)
    c2.metric("Pilotos", total_pilotos)
    c3.metric(
        "Vueltas de Pit / SC / lentas",
        total_anomalias,
        help="Vueltas fuera del ritmo normal (boxes, Safety Car, VSC o banderas amarillas).",
    )

    excluir = st.toggle(
        "Excluir vueltas lentas / Pit / Safety Car en gráfico de ritmo",
        value=True,
        help="Los registros nunca se eliminan; solo se ocultan para analizar ritmo puro.",
    )
    fig = grafico_ritmo_vueltas(laps_df, excluir_anomalias=excluir)
    st.plotly_chart(fig, width="stretch")
