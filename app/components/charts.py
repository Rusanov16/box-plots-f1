"""Componentes visuales Plotly reutilizables para SIE-F1."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _laptime_segundos(df: pd.DataFrame) -> pd.Series:
    col = "tiempo_lap" if "tiempo_lap" in df.columns else "LapTime"
    serie = df[col]
    if pd.api.types.is_timedelta64_dtype(serie):
        return serie.dt.total_seconds()
    return serie.apply(lambda v: v.total_seconds() if hasattr(v, "total_seconds") else pd.to_numeric(v, errors="coerce"))


def grafico_ritmo_vueltas(
    laps_df: pd.DataFrame,
    excluir_anomalias: bool = True,
    titulo: str = "Evolución de Ritmo por Vuelta",
) -> go.Figure:
    """Genera gráfico de líneas de tiempo por vuelta con filtro opcional de anomalías."""
    if laps_df is None or laps_df.empty:
        return go.Figure().update_layout(title="Sin datos de vueltas para graficar")

    df = laps_df.copy()
    df["segundos"] = _laptime_segundos(df)
    df = df[df["segundos"].notna() & (df["segundos"] > 0)]

    if excluir_anomalias and "es_anomalia" in df.columns:
        df = df[~df["es_anomalia"].astype(bool)]

    if df.empty:
        return go.Figure().update_layout(title="No hay vueltas válidas tras aplicar el filtro")

    col_vuelta = "numero_vuelta" if "numero_vuelta" in df.columns else "LapNumber"
    col_piloto = "id_piloto" if "id_piloto" in df.columns else "Driver"

    fig = px.line(
        df,
        x=col_vuelta,
        y="segundos",
        color=col_piloto,
        markers=True,
        title=titulo,
        labels={col_vuelta: "Número de vuelta", "segundos": "Tiempo (s)", col_piloto: "Piloto"},
    )
    fig.update_layout(hovermode="x unified")
    return fig


def grafico_degradacion_stints(degradacion: list[dict]) -> go.Figure:
    """Genera gráfico de barras de degradación (s/vuelta) por piloto y stint."""
    if not degradacion:
        return go.Figure().update_layout(title="Sin stints suficientes para calcular degradación")

    df = pd.DataFrame(degradacion)
    df["etiqueta"] = df["id_piloto"].astype(str) + " - S" + df["stint"].astype(str)
    fig = px.bar(
        df,
        x="etiqueta",
        y="degradacion_s_por_vuelta",
        color="compuesto",
        title="Degradación Estimada por Stint (s/vuelta)",
        labels={
            "etiqueta": "Piloto / Stint",
            "degradacion_s_por_vuelta": "Degradación (s/vuelta)",
            "compuesto": "Compuesto",
        },
    )
    return fig


def grafico_mapa_calor_circuito(
    tel_df: pd.DataFrame,
    metrica: str = "speed",
    titulo: str = "Mapa de Calor del Circuito",
) -> go.Figure:
    """Renderiza el trazado `(x, y)` del circuito coloreado por velocidad, acelerador o marcha."""
    if tel_df is None or tel_df.empty or "x" not in tel_df.columns or "y" not in tel_df.columns:
        return go.Figure().update_layout(title="Sin coordenadas de circuito disponibles")

    etiquetas = {
        "speed": ("Velocidad (km/h)", "Turbo"),
        "throttle": ("Acelerador (%)", "Viridis"),
        "n_gear": ("Marcha", "Plasma"),
    }
    label, escala = etiquetas.get(metrica, (metrica, "Turbo"))

    fig = go.Figure(
        data=go.Scatter(
            x=tel_df["x"],
            y=tel_df["y"],
            mode="markers",
            marker=dict(
                size=5,
                color=tel_df[metrica],
                colorscale=escala,
                colorbar=dict(title=label),
                showscale=True,
            ),
            text=[
                f"Vel: {r.speed} km/h | Acel: {r.throttle}% | Marcha: {r.n_gear}"
                for r in tel_df.itertuples(index=False)
            ],
            hoverinfo="text",
        )
    )
    fig.update_layout(
        title=titulo,
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=40, b=10),
        height=460,
    )
    return fig


COLORES_PIRELLI = {
    "SOFT": "#E10600",
    "MEDIUM": "#FFD12E",
    "HARD": "#E8E8E8",
    "INTERMEDIATE": "#43B02A",
    "WET": "#0067AD",
}


def grafico_stints_pirelli(laps_df: pd.DataFrame) -> go.Figure:
    """Gráfico de barras horizontales de stints por piloto con colores oficiales Pirelli."""
    if laps_df is None or laps_df.empty:
        return go.Figure().update_layout(title="Sin datos de stints disponibles")

    col_p = "id_piloto" if "id_piloto" in laps_df.columns else "Driver"
    col_s = "Stint" if "Stint" in laps_df.columns else "stint"
    col_c = "compuesto" if "compuesto" in laps_df.columns else "Compound"
    col_v = "numero_vuelta" if "numero_vuelta" in laps_df.columns else "LapNumber"

    if col_p not in laps_df.columns or col_c not in laps_df.columns:
        return go.Figure().update_layout(title="Faltan columnas de piloto o compuesto")

    df = laps_df.copy()
    if col_s not in df.columns:
        df[col_s] = 1
    df = df.dropna(subset=[col_p, col_c, col_v])
    if df.empty:
        return go.Figure().update_layout(title="Sin stints válidos para graficar")

    stints = (
        df.groupby([col_p, col_s, col_c], as_index=False)
        .agg(vuelta_ini=(col_v, "min"), vuelta_fin=(col_v, "max"), vueltas=(col_v, "count"))
        .sort_values([col_p, col_s])
    )

    fig = go.Figure()
    compuestos_en_leyenda = set()
    for _, row in stints.iterrows():
        comp = str(row[col_c]).upper()
        mostrar_leyenda = comp not in compuestos_en_leyenda
        compuestos_en_leyenda.add(comp)
        fig.add_trace(
            go.Bar(
                y=[str(row[col_p])],
                x=[int(row["vueltas"])],
                base=[int(row["vuelta_ini"]) - 1],
                orientation="h",
                name=comp,
                legendgroup=comp,
                showlegend=mostrar_leyenda,
                marker=dict(color=COLORES_PIRELLI.get(comp, "#888888"), line=dict(color="#111", width=1)),
                hovertemplate=(
                    f"<b>{row[col_p]}</b> — Stint {int(row[col_s])}<br>"
                    f"Compuesto: {comp}<br>Vueltas: {int(row['vuelta_ini'])}–{int(row['vuelta_fin'])} "
                    f"({int(row['vueltas'])} v)<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title="Estrategia de Neumáticos por Piloto",
        barmode="stack",
        xaxis_title="Número de Vuelta",
        yaxis_title="Piloto",
        height=max(420, int(stints[col_p].nunique()) * 26),
    )
    return fig
