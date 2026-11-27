"""Pestaña de estrategia de neumáticos y degradación por stint (SIE-F1)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components.charts import grafico_degradacion_stints, grafico_stints_pirelli
from src.domain.indicators import calcular_degradacion_stints, estimar_ventana_undercut


def render_estrategia_neumaticos(laps_df: pd.DataFrame) -> None:
    """Calcula y muestra estrategia visual Pirelli, degradación y ventana de undercut."""
    if laps_df is None or laps_df.empty:
        st.info("No hay vueltas cargadas para analizar estrategia de neumáticos.")
        return

    st.plotly_chart(grafico_stints_pirelli(laps_df), width="stretch")
    st.divider()

    c1, c2 = st.columns(2)
    excluir = c1.checkbox(
        "Excluir vueltas de Pit, Safety Car y tráfico",
        value=True,
        help="Oculta entradas/salidas de boxes, Safety Car, VSC y banderas amarillas para medir el desgaste real del neumático.",
    )
    pit_loss = c2.slider("Tiempo perdido en Pit Lane (s)", min_value=16.0, max_value=28.0, value=22.0, step=0.5)
    degradacion = calcular_degradacion_stints(laps_df, excluir_anomalias=excluir)

    if not degradacion:
        st.warning("No hay stints con suficientes vueltas válidas para estimar degradación.")
        return

    st.subheader("⏱️ Ventana de Undercut y Degradación por Compuesto")
    ventana = estimar_ventana_undercut(degradacion, tiempo_pit_lane_s=float(pit_loss))
    if ventana:
        df_vent = pd.DataFrame(ventana).rename(
            columns={"Vueltas para compensar Pit (~22s)": f"Vueltas para compensar Pit ({pit_loss:.1f}s)"}
        )
        st.dataframe(df_vent, width="stretch", hide_index=True)
    else:
        st.info(
            f"Con **{pit_loss:.1f} s** de pérdida estimada en Pit Lane no se detecta una ventana positiva de undercut en estos stints."
        )

    fig = grafico_degradacion_stints(degradacion)
    st.plotly_chart(fig, width="stretch")
    st.dataframe(pd.DataFrame(degradacion), width="stretch")
