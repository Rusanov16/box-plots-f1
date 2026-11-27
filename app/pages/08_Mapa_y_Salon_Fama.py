"""Página 08: Mapa Mundial de Circuitos (1950–2026) y Salón de la Fama de Pilotos."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = APP_DIR.parent
for _p in (str(ROOT_DIR), str(APP_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastf1.ergast import Ergast
import pandas as pd
import plotly.express as px
import streamlit as st

from components.theme import (
    MCLAREN_RED,
    estilizar_plotly_editorial,
    inject_editorial_theme,
    render_crt_header,
)

ASSETS_DRIVERS_DIR = ROOT_DIR / "app" / "assets" / "drivers"

LEYENDAS = {
    "Juan Manuel Fangio": "fangio",
    "Ayrton Senna": "senna",
    "Alain Prost": "prost",
    "Michael Schumacher": "michael_schumacher",
    "Lewis Hamilton": "hamilton",
    "Fernando Alonso": "alonso",
    "Sebastian Vettel": "vettel",
    "Max Verstappen": "max_verstappen",
    "Niki Lauda": "lauda",
    "Jim Clark": "clark",
}

st.set_page_config(page_title="Mapa Mundial y Salón de la Fama — Box Plots F1", layout="wide")
inject_editorial_theme()
render_crt_header(
    canal="CH 08 · HALL OF FAME & CIRCUITS",
    titulo="🌍 Mapa Mundial de Circuitos y 🏛️ Salón de la Fama",
    subtitulo="Cobertura geográfica histórica (1950–2026) y expedientes de leyendas FIA.",
)

tab_mapa, tab_fama = st.tabs(["🌍 Mapa Mundial de Circuitos (1950–2026)", "🏛️ Salón de la Fama / Perfil de Piloto"])

@st.cache_data(ttl=24 * 3600, show_spinner=False)
def _cargar_circuitos_mundo() -> pd.DataFrame:
    ergast = Ergast()
    df_c = ergast.get_circuits(limit=100)
    return df_c if df_c is not None else pd.DataFrame()


@st.cache_data(ttl=24 * 3600, show_spinner=False, max_entries=20)
def _cargar_perfil_piloto(driver_id: str) -> pd.DataFrame:
    ergast = Ergast()
    carreras_raw = []
    offset = 0
    limit = 100
    while True:
        resp = ergast.get_race_results(driver=driver_id, limit=limit, offset=offset)
        if resp is None or not getattr(resp, "content", None):
            break
        desc = getattr(resp, "description", None)
        n_lote = 0
        for idx, df_s in enumerate(resp.content):
            if df_s is None or df_s.empty:
                continue
            n_lote += len(df_s)
            r = df_s.iloc[0]
            season = int(desc.iloc[idx]["season"]) if desc is not None and idx < len(desc) else 0
            carreras_raw.append(
                {
                    "Temporada": season,
                    "position": pd.to_numeric(r.get("position"), errors="coerce"),
                    "grid": pd.to_numeric(r.get("grid"), errors="coerce"),
                    "points": pd.to_numeric(r.get("points"), errors="coerce") or 0.0,
                    "Escudería": str(r.get("constructorName", "")),
                    "Nombre": f"{r.get('givenName', '')} {r.get('familyName', '')}".strip(),
                    "Nacionalidad": {
                        "Argentine": "Argentina",
                        "British": "Británica",
                        "German": "Alemana",
                        "Brazilian": "Brasileña",
                        "French": "Francesa",
                        "Austrian": "Austríaca",
                        "Spanish": "Española",
                        "Dutch": "Neerlandesa",
                        "Italian": "Italiana",
                        "Finnish": "Finlandesa",
                        "Australian": "Australiana",
                        "Monegasque": "Monegasca",
                        "Mexican": "Mexicana",
                    }.get(str(r.get("driverNationality", "")), str(r.get("driverNationality", ""))),
                }
            )
        if n_lote < limit or offset >= 600:
            break
        offset += limit

    if not carreras_raw:
        return pd.DataFrame()
    df_all = pd.DataFrame(carreras_raw)
    return (
        df_all.groupby("Temporada", as_index=False)
        .agg(
            Escudería=("Escudería", lambda s: ", ".join(dict.fromkeys(s))),
            Carreras=("position", "count"),
            Victorias=("position", lambda s: int((s == 1).sum())),
            Podios=("position", lambda s: int((s <= 3).sum())),
            Poles=("grid", lambda s: int((s == 1).sum())),
            Puntos=("points", "sum"),
            Nombre=("Nombre", "first"),
            Nacionalidad=("Nacionalidad", "first"),
        )
        .sort_values("Temporada")
    )


# Correcciones FIA oficiales donde Ergast omite datos de parrilla en los años 50
_POLES_OFICIALES_FIA = {
    "fangio": 29,
}

with tab_mapa:
    st.subheader("Circuitos de la Fórmula 1")
    with st.spinner("Cargando catálogo mundial de circuitos..."):
        try:
            df_c = _cargar_circuitos_mundo()
        except Exception as exc:
            st.error(f"Error consultando circuitos: {exc}")
            df_c = pd.DataFrame()
    if not df_c.empty and "lat" in df_c.columns and "long" in df_c.columns:
        df_plot = df_c.copy()
        df_plot["lat"] = pd.to_numeric(df_plot["lat"], errors="coerce")
        df_plot["long"] = pd.to_numeric(df_plot["long"], errors="coerce")
        df_plot = df_plot.dropna(subset=["lat", "long"])

        col_f1, col_f2 = st.columns(2)
        paises = ["Todos"] + sorted(df_plot["country"].dropna().unique().tolist())
        pais_sel = col_f1.selectbox("Filtrar por país", paises)
        if pais_sel != "Todos":
            df_plot = df_plot[df_plot["country"] == pais_sel]

        circuitos_lista = ["(Ninguno — Vista global)"] + sorted(df_plot["circuitName"].dropna().unique().tolist())
        circ_sel = col_f2.selectbox("Seleccionar circuito para ver ficha y trazado", circuitos_lista)

        rot_lon, rot_lat = 10.0, 25.0
        fila_circ = None
        if circ_sel != "(Ninguno — Vista global)":
            fila_circ = df_plot[df_plot["circuitName"] == circ_sel].iloc[0]
            rot_lon = float(fila_circ["long"])
            rot_lat = float(fila_circ["lat"])

        fig_geo = px.scatter_geo(
            df_plot,
            lat="lat",
            lon="long",
            hover_name="circuitName",
            hover_data={"locality": True, "country": True, "lat": False, "long": False},
            projection="orthographic",
            title=f"🌐 Globo 3D Interactivo de Circuitos F1 ({len(df_plot)} circuitos)",
        )
        fig_geo.update_traces(
            marker=dict(size=8, color="#E10600", line=dict(width=1, color="#FFFFFF"), opacity=0.92)
        )
        fig_geo.update_geos(
            showocean=True,
            oceancolor="#0B1220",
            showland=True,
            landcolor="#232834",
            showcountries=True,
            countrycolor="#3D4659",
            showcoastlines=True,
            coastlinecolor="#4B5568",
            bgcolor="rgba(0,0,0,0)",
            projection_rotation=dict(lon=rot_lon, lat=rot_lat),
        )
        fig_geo.update_layout(
            height=540,
            margin=dict(l=0, r=0, t=45, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            geo_bgcolor="rgba(0,0,0,0)",
        )
        evento_mapa = st.plotly_chart(
            fig_geo,
            width="stretch",
            on_select="rerun",
            selection_mode="points",
            key="globo_circuitos_f1",
        )

        # Si el usuario pincha un punto directamente en el globo 3D, seleccionarlo
        if evento_mapa and getattr(evento_mapa, "selection", None):
            puntos = evento_mapa.selection.get("points", [])
            if puntos:
                nombre_click = puntos[0].get("hovertext")
                match = df_plot[df_plot["circuitName"] == nombre_click]
                if not match.empty:
                    fila_circ = match.iloc[0]
                    rot_lon = float(fila_circ["long"])
                    rot_lat = float(fila_circ["lat"])

        if fila_circ is not None:
            st.divider()
            st.subheader(f"🏁 {fila_circ['circuitName']} — {fila_circ['locality']}, {fila_circ['country']}")
            c_info, c_map = st.columns([1, 2])
            with c_info:
                st.write(f"**Ubicación:** {fila_circ['locality']}, {fila_circ['country']}")
                st.write(f"**Coordenadas:** `{fila_circ['lat']:.4f}, {fila_circ['long']:.4f}`")
                if pd.notna(fila_circ.get("circuitUrl")):
                    st.markdown(f"[📖 Ver ficha en Wikipedia]({fila_circ['circuitUrl']})")

                cid = str(fila_circ.get("circuitId", ""))
                if cid and st.button("Consultar récords históricos de este circuito"):
                    with st.spinner("Consultando ganadores históricos en Ergast..."):
                        try:
                            erg = Ergast()
                            resp_c = erg.get_race_results(circuit=cid, results_position=1, limit=100)
                            ganadores = []
                            if resp_c is not None and getattr(resp_c, "content", None):
                                desc_c = getattr(resp_c, "description", None)
                                for idx_c, df_g in enumerate(resp_c.content):
                                    if df_g is None or df_g.empty:
                                        continue
                                    g = df_g.iloc[0]
                                    yr = int(desc_c.iloc[idx_c]["season"]) if desc_c is not None and idx_c < len(desc_c) else 0
                                    ganadores.append(
                                        {
                                            "Año": yr,
                                            "Ganador": f"{g.get('givenName', '')} {g.get('familyName', '')}".strip(),
                                            "Escudería": str(g.get("constructorName", "")),
                                        }
                                    )
                            if ganadores:
                                df_gan = pd.DataFrame(ganadores)
                                top_p = df_gan["Ganador"].value_counts().index[0]
                                top_p_n = int(df_gan["Ganador"].value_counts().iloc[0])
                                top_e = df_gan["Escudería"].value_counts().index[0]
                                top_e_n = int(df_gan["Escudería"].value_counts().iloc[0])
                                st.metric("Ediciones F1 registradas", len(df_gan))
                                st.write(f"**Máximo ganador:** {top_p} ({top_p_n} victorias)")
                                st.write(f"**Escudería líder:** {top_e} ({top_e_n} victorias)")
                                st.write(f"**Periodo:** {df_gan['Año'].min()} – {df_gan['Año'].max()}")
                            else:
                                st.info("Sin historial de ganadores disponible.")
                        except Exception as exc:
                            st.error(f"Error consultando récords: {exc}")

            with c_map:
                df_zoom = pd.DataFrame([{"lat": rot_lat, "lon": rot_lon, "Circuito": fila_circ["circuitName"]}])
                fig_trazado = px.scatter_map(
                    df_zoom,
                    lat="lat",
                    lon="lon",
                    hover_name="Circuito",
                    center={"lat": float(rot_lat), "lon": float(rot_lon)},
                    zoom=13.5,
                    map_style="carto-positron",
                    title="Vista de Trazado / Ubicación Exacta de la Pista",
                )
                fig_trazado.update_traces(marker=dict(size=12, color="#E10600"))
                fig_trazado.update_layout(height=360, margin=dict(l=0, r=0, t=35, b=0))
                st.plotly_chart(fig_trazado, width="stretch")
        with st.expander("📋 Directorio de circuitos"):
            df_tabla_c = df_plot[["circuitName", "locality", "country"]].rename(
                columns={
                    "circuitName": "Circuito",
                    "locality": "Ciudad",
                    "country": "País",
                }
            )
            st.dataframe(df_tabla_c, width="stretch", hide_index=True)
    else:
        st.info("No se pudieron cargar los circuitos en este momento.")

with tab_fama:
    st.subheader("Salón de la Fama — Leyendas de la Fórmula 1")
    leyenda_sel = st.selectbox("Selecciona una leyenda", list(LEYENDAS.keys()))
    driver_id = LEYENDAS[leyenda_sel]

    with st.spinner(f"Cargando expediente histórico de {leyenda_sel}..."):
        try:
            df_p = _cargar_perfil_piloto(driver_id)
        except Exception as exc:
            st.error(f"Error consultando perfil de {leyenda_sel}: {exc}")
            df_p = pd.DataFrame()

    pid = driver_id
    if not df_p.empty:
        nombre = df_p["Nombre"].iloc[0]
        nac = df_p["Nacionalidad"].iloc[0]
        carreras_tot = int(df_p["Carreras"].sum())
        victorias = int(df_p["Victorias"].sum())
        podios = int(df_p["Podios"].sum())
        poles = _POLES_OFICIALES_FIA.get(pid, int(df_p["Poles"].sum()))
        puntos_tot = float(df_p["Puntos"].sum())

        img_uri = None
        for ext, mime in (("png", "image/png"), ("jpg", "image/jpeg"), ("jpeg", "image/jpeg"), ("webp", "image/webp")):
            ruta = ASSETS_DRIVERS_DIR / f"{pid}.{ext}"
            if ruta.exists():
                b64 = base64.b64encode(ruta.read_bytes()).decode("ascii")
                img_uri = f"data:{mime};base64,{b64}"
                break

        iniciales = "".join(p[0] for p in nombre.split()[:2]).upper()
        bloque_retrato = (
            f'<img src="{img_uri}" style="width:165px; height:165px; object-fit:cover; '
            f'border-radius:8px; border:1px solid #D6CEBC; flex-shrink:0;" />'
            if img_uri
            else f'<div style="width:165px; height:165px; background:#EAE4D7; border-radius:8px; '
            f'border:1px solid #D6CEBC; display:flex; align-items:center; justify-content:center; '
            f'font-size:46px; font-weight:800; color:#262626; flex-shrink:0;">{iniciales}</div>'
        )
        tasa_win = (victorias / carreras_tot * 100.0) if carreras_tot else 0.0
        tasa_podio = (podios / carreras_tot * 100.0) if carreras_tot else 0.0
        periodo_p = f"{int(df_p['Temporada'].min())} – {int(df_p['Temporada'].max())}"

        st.markdown(
            f"""
            <div style="background:#F7F4EC; color:#1E1E1E; border:1px solid #DDD6C5; border-radius:10px;
                        padding:24px 28px; display:flex; gap:24px; align-items:center; flex-wrap:wrap; margin-bottom:16px;">
                {bloque_retrato}
                <div style="flex:1; min-width:260px;">
                    <div style="font-size:12px; text-transform:uppercase; letter-spacing:1.5px; color:#666;">
                        Salón de la Fama · Box Plots F1 · {nac} · {periodo_p}
                    </div>
                    <div style="font-size:36px; font-weight:800; line-height:1.1; margin:4px 0 14px 0;">
                        {nombre}
                    </div>
                    <div style="display:flex; gap:14px; flex-wrap:wrap;">
                        <div style="background:#FFFFFF; border:1px solid #E3DCCB; border-radius:8px; padding:10px 14px; min-width:105px;">
                            <div style="font-size:11px; color:#666; text-transform:uppercase;">Carreras</div>
                            <div style="font-size:22px; font-weight:800;">{carreras_tot}</div>
                        </div>
                        <div style="background:#FFFFFF; border:1px solid #E3DCCB; border-radius:8px; padding:10px 14px; min-width:105px;">
                            <div style="font-size:11px; color:#666; text-transform:uppercase;">Victorias</div>
                            <div style="font-size:22px; font-weight:800;">{victorias} <span style="font-size:12px; color:#666;">({tasa_win:.1f}%)</span></div>
                        </div>
                        <div style="background:#FFFFFF; border:1px solid #E3DCCB; border-radius:8px; padding:10px 14px; min-width:105px;">
                            <div style="font-size:11px; color:#666; text-transform:uppercase;">Podios</div>
                            <div style="font-size:22px; font-weight:800;">{podios} <span style="font-size:12px; color:#666;">({tasa_podio:.1f}%)</span></div>
                        </div>
                        <div style="background:#FFFFFF; border:1px solid #E3DCCB; border-radius:8px; padding:10px 14px; min-width:105px;">
                            <div style="font-size:11px; color:#666; text-transform:uppercase;">Poles</div>
                            <div style="font-size:22px; font-weight:800;">{poles}</div>
                        </div>
                        <div style="background:#FFFFFF; border:1px solid #E3DCCB; border-radius:8px; padding:10px 14px; min-width:115px;">
                            <div style="font-size:11px; color:#666; text-transform:uppercase;">Puntos</div>
                            <div style="font-size:22px; font-weight:800;">{puntos_tot:.1f}</div>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        fig_hist = px.line(
            df_p.sort_values("Temporada"),
            x="Temporada",
            y="Puntos",
            markers=True,
            color_discrete_sequence=[MCLAREN_RED],
            hover_data=["Victorias", "Podios", "Poles", "Escudería"],
            title=f"Evolución de Puntos por Temporada — {nombre}",
        )
        estilizar_plotly_editorial(fig_hist)
        st.plotly_chart(fig_hist, width="stretch")
        st.dataframe(
            df_p[["Temporada", "Escudería", "Carreras", "Victorias", "Podios", "Poles", "Puntos"]].sort_values("Temporada", ascending=False),
            width="stretch",
            hide_index=True,
        )
