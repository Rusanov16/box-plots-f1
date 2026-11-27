"""Página 06: Duelos Históricos (Head-to-Head 1950–actualidad) y Fiabilidad."""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = APP_DIR.parent
for _p in (str(ROOT_DIR), str(APP_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import plotly.express as px
import streamlit as st

from components.theme import (
    INK_CHARCOAL,
    MCLAREN_RED,
    MOTORSPORT_GREEN,
    estilizar_plotly_editorial,
    grafico_barras_editorial,
    inject_editorial_theme,
    render_crt_header,
)
from src.etl.extractor import extraer_temporada_completa_ergast, extraer_vueltas_piloto_ergast

st.set_page_config(page_title="Duelos H2H y Fiabilidad — Box Plots F1", layout="wide")
inject_editorial_theme()


def _preparar_df_temporada(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "givenName" in out.columns and "familyName" in out.columns:
        out["Piloto"] = (
            out["givenName"].fillna("").astype(str).str.strip()
            + " "
            + out["familyName"].fillna("").astype(str).str.strip()
        ).str.strip()
    else:
        out["Piloto"] = out.get("driverId", "Desconocido").astype(str)
    out["points"] = pd.to_numeric(out.get("points", 0), errors="coerce").fillna(0.0)
    out["position"] = pd.to_numeric(out.get("position"), errors="coerce")
    out["grid"] = pd.to_numeric(out.get("grid"), errors="coerce")
    out["round"] = pd.to_numeric(out.get("round", 0), errors="coerce").fillna(0).astype(int)
    return out


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _cargar_temporada_duelos(anio: int) -> pd.DataFrame:
    raw = extraer_temporada_completa_ergast(int(anio))
    return _preparar_df_temporada(raw) if not raw.empty else pd.DataFrame()


@st.cache_data(ttl=24 * 3600, show_spinner=False, max_entries=60)
def _cargar_vueltas_gp(anio: int, ronda: int, id1: str, id2: str) -> pd.DataFrame:
    return extraer_vueltas_piloto_ergast(int(anio), int(ronda), [id1, id2])


col_sel, col_info = st.columns([1, 3])
anios_disp = list(range(2026, 1949, -1))
anio = col_sel.selectbox(
    "Temporada",
    anios_disp,
    index=anios_disp.index(1988),
    help="Ejemplos icónicos: 1988 (Senna vs Prost), 2005/2006 (Alonso vs Schumacher), 2021 (Verstappen vs Hamilton).",
)

render_crt_header(
    canal=f"CH 03 · DUELOS & FIABILIDAD {anio}",
    titulo=f"⚔️ Duelos H2H, Fiabilidad y Movilidad en Carrera — {anio}",
    subtitulo="Comparativa cabeza a cabeza, tasa de abandonos por escudería y balance Parrilla → Meta · Fuente: Ergast / Jolpica",
)

with st.spinner(f"Cargando temporada {anio}..."):
    try:
        df_temp = _cargar_temporada_duelos(int(anio))
    except Exception as exc:
        st.error(f"Error consultando Ergast/Jolpica para {anio}: {exc}")
        df_temp = pd.DataFrame()

anio_cargado = int(anio)
n_rondas = int(df_temp["round"].nunique()) if not df_temp.empty else 0
col_info.markdown(
    f"<div style='padding-top:32px; font-family:\"IBM Plex Mono\",monospace; font-size:0.78rem; color:#5A564E;'>"
    f"Temporada {anio_cargado} · {n_rondas} carreras cargadas"
    f"</div>",
    unsafe_allow_html=True,
)

if df_temp is not None and not df_temp.empty:
    tab_h2h, tab_fiab, tab_adel = st.tabs(
        ["⚔️ Duelo Head-to-Head", "🔧 Fiabilidad y Abandonos", "📊 Movilidad en Carrera (Parrilla → Meta)"]
    )

    with tab_h2h:
        pilotos = (
            df_temp.groupby("Piloto")["points"].sum().sort_values(ascending=False).index.tolist()
        )
        c1, c2 = st.columns(2)
        p1 = c1.selectbox("Piloto 1", pilotos, index=0)
        p2 = c2.selectbox("Piloto 2", pilotos, index=min(1, len(pilotos) - 1))

        d1 = df_temp[df_temp["Piloto"] == p1].sort_values("round")
        d2 = df_temp[df_temp["Piloto"] == p2].sort_values("round")

        merged = pd.merge(
            d1[["round", "raceName", "position", "grid", "points", "status", "driverId"]],
            d2[["round", "position", "grid", "points", "status", "driverId"]],
            on="round",
            how="outer",
            suffixes=("_1", "_2"),
        ).sort_values("round")

        merged["pts_acum_1"] = merged["points_1"].fillna(0).cumsum()
        merged["pts_acum_2"] = merged["points_2"].fillna(0).cumsum()

        ambos = merged.dropna(subset=["position_1", "position_2"])
        gana_1 = int((ambos["position_1"] < ambos["position_2"]).sum())
        gana_2 = int((ambos["position_2"] < ambos["position_1"]).sum())

        ap1 = p1.split()[-1] if p1 else p1
        ap2 = p2.split()[-1] if p2 else p2
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(f"Puntos · {ap1}", f"{d1['points'].sum():.1f}")
        m2.metric(f"Puntos · {ap2}", f"{d2['points'].sum():.1f}")
        m3.metric(f"Carrera H2H · {ap1}", gana_1)
        m4.metric(f"Carrera H2H · {ap2}", gana_2)

        # Curva acumulada de puntos
        curva = pd.DataFrame(
            {
                "Ronda": list(merged["round"]) * 2,
                "Piloto": [p1] * len(merged) + [p2] * len(merged),
                "Puntos Acumulados": list(merged["pts_acum_1"]) + list(merged["pts_acum_2"]),
            }
        )
        fig_curva = px.line(
            curva,
            x="Ronda",
            y="Puntos Acumulados",
            color="Piloto",
            markers=True,
            color_discrete_sequence=[MCLAREN_RED, INK_CHARCOAL],
            title=f"Evolución del Campeonato {anio_cargado}: {ap1} vs {ap2}",
        )
        estilizar_plotly_editorial(fig_curva)
        fig_curva.update_layout(
            margin=dict(t=82),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, title_text=""),
        )
        st.plotly_chart(fig_curva, width="stretch")

        # Ritmo vuelta a vuelta (disponible desde 1996)
        if anio_cargado >= 1996 and "raceName" in merged.columns:
            st.divider()
            st.subheader("⏱️ Duelo Vuelta a Vuelta (Disponible desde 1996)")
            carreras = merged[["round", "raceName"]].dropna().drop_duplicates()
            opciones_gp = {f"R{int(r['round'])} — {r['raceName']}": int(r["round"]) for _, r in carreras.iterrows()}
            gp_sel = st.selectbox("Selecciona un Gran Premio para ver ritmo vuelta a vuelta", list(opciones_gp.keys()))
            if st.button("Comparar tiempos vuelta a vuelta"):
                id1 = str(d1["driverId"].iloc[0]) if not d1.empty else ""
                id2 = str(d2["driverId"].iloc[0]) if not d2.empty else ""
                with st.spinner("Cargando tiempos vuelta a vuelta..."):
                    error_api = False
                    try:
                        laps_raw = _cargar_vueltas_gp(anio_cargado, opciones_gp[gp_sel], id1, id2)
                    except Exception:
                        error_api = True
                        st.warning(
                            "El servicio de datos históricos limitó temporalmente las peticiones. "
                            "Espera unos segundos y pulsa el botón nuevamente."
                        )
                        laps_raw = pd.DataFrame()
                    if not error_api and (laps_raw.empty or "driverId" not in laps_raw.columns):
                        st.info("No hay tiempos vuelta a vuelta disponibles para este GP.")
                    elif not error_api:
                        sub = laps_raw[laps_raw["driverId"].isin([id1, id2])].copy()
                        if sub.empty:
                            st.warning("Ninguno de los dos pilotos registró vueltas en este GP.")
                        else:
                            sub["Piloto"] = sub["driverId"].map({id1: p1, id2: p2})

                            def _parse_lap_s(val: object) -> float:
                                s = str(val or "").strip()
                                if ":" in s:
                                    partes = s.split(":")
                                    try:
                                        if len(partes) == 2:
                                            return float(partes[0]) * 60.0 + float(partes[1])
                                        if len(partes) == 3:
                                            return float(partes[0]) * 3600.0 + float(partes[1]) * 60.0 + float(partes[2])
                                    except ValueError:
                                        return float("nan")
                                td = pd.to_timedelta(s, errors="coerce")
                                return float(td.total_seconds()) if pd.notna(td) else float("nan")

                            sub["Segundos"] = sub["time"].apply(_parse_lap_s)
                            sub = sub[sub["Segundos"].notna() & (sub["Segundos"] > 0)]
                            fig_v = px.line(
                                sub,
                                x="number",
                                y="Segundos",
                                color="Piloto",
                                markers=True,
                                color_discrete_sequence=[MCLAREN_RED, INK_CHARCOAL],
                                title=f"Ritmo Vuelta a Vuelta — {gp_sel} ({anio_cargado})",
                                labels={"number": "Vuelta", "Segundos": "Tiempo (s)"},
                            )
                            estilizar_plotly_editorial(fig_v)
                            fig_v.update_layout(
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text="")
                            )
                            st.plotly_chart(fig_v, width="stretch")

    with tab_fiab:
        st.subheader(f"Análisis de Fiabilidad y Causas de Abandono — Temporada {anio_cargado}")
        df_f = df_temp.copy()
        status_str = df_f["status"].fillna("Unknown").astype(str)
        df_f["Terminó"] = status_str.str.contains("Finished|Lap", case=False, regex=True)

        if "constructorName" in df_f.columns:
            fiab_eq = (
                df_f.groupby("constructorName", as_index=False)
                .agg(
                    Participaciones=("Terminó", "count"),
                    Terminadas=("Terminó", "sum"),
                )
            )
            fiab_eq["% Fiabilidad"] = (fiab_eq["Terminadas"] / fiab_eq["Participaciones"] * 100).round(1)
            fiab_eq = fiab_eq.sort_values("% Fiabilidad", ascending=False)
            fig_fiab = grafico_barras_editorial(
                fiab_eq,
                categoria_col="constructorName",
                valor_col="% Fiabilidad",
                titulo=f"Tasa de Fiabilidad por Constructor — {anio_cargado}",
                sufijo_texto="%",
                color_lider=MOTORSPORT_GREEN,
                formato_valor=".1f",
            )
            st.plotly_chart(fig_fiab, width="stretch")

        abandonos = df_f[~df_f["Terminó"]]
        if not abandonos.empty:
            causas = abandonos["status"].value_counts().head(12).reset_index()
            causas.columns = ["Causa de Abandono", "Cantidad"]
            fig_causas = grafico_barras_editorial(
                causas,
                categoria_col="Causa de Abandono",
                valor_col="Cantidad",
                titulo=f"Principales Causas de Abandono — {anio_cargado}",
                sufijo_texto=" DNF",
                color_lider=MCLAREN_RED,
                formato_valor=".0f",
            )
            st.plotly_chart(fig_causas, width="stretch")
        else:
            st.info("No se registraron abandonos en esta temporada.")


    with tab_adel:
        st.subheader(f"Índice de Movilidad en Carrera (Parrilla → Meta) — Temporada {anio_cargado}")
        st.caption(
            "Mide el cambio neto entre el cajón de salida y la posición final de carrera. "
            "Combina adelantamientos en pista, estrategia y abandonos de rivales."
        )
        df_ad = df_temp.dropna(subset=["grid", "position"]).copy()
        df_ad = df_ad[(df_ad["grid"] > 0) & (df_ad["position"] > 0)]
        if df_ad.empty:
            st.info("No hay datos válidos de parrilla y posición final para esta temporada.")
        else:
            df_ad["pos_ganadas"] = df_ad["grid"] - df_ad["position"]
            df_ad["cambio_abs"] = df_ad["pos_ganadas"].abs()

            por_piloto = (
                df_ad.groupby("Piloto", as_index=False)
                .agg(
                    Ganancia_Neta_Total=("pos_ganadas", "sum"),
                    Ganancia_Media=("pos_ganadas", "mean"),
                    Carreras=("pos_ganadas", "count"),
                )
                .sort_values("Ganancia_Neta_Total", ascending=False)
            )
            por_piloto["Ganancia_Media"] = por_piloto["Ganancia_Media"].round(2)

            fig_p = grafico_barras_editorial(
                por_piloto.head(15),
                categoria_col="Piloto",
                valor_col="Ganancia_Neta_Total",
                titulo=f"Mayores Remontadas en Carrera (Posiciones Ganadas Netas) — {anio_cargado}",
                sufijo_texto=" pos",
                color_lider=MOTORSPORT_GREEN,
                formato_valor="+.0f",
            )
            st.plotly_chart(fig_p, width="stretch")

            if "raceName" in df_ad.columns:
                por_gp = (
                    df_ad.groupby("raceName", as_index=False)
                    .agg(Indice_Movilidad=("cambio_abs", "mean"))
                    .sort_values("Indice_Movilidad", ascending=False)
                )
                por_gp["Indice_Movilidad"] = por_gp["Indice_Movilidad"].round(2)
                fig_gp = grafico_barras_editorial(
                    por_gp,
                    categoria_col="raceName",
                    valor_col="Indice_Movilidad",
                    titulo=f"Índice de Movilidad por Circuito (Cambio medio |Parrilla - Meta|) — {anio_cargado}",
                    sufijo_texto=" pos/piloto",
                    color_lider=MCLAREN_RED,
                    formato_valor=".2f",
                )
                st.plotly_chart(fig_gp, width="stretch")
