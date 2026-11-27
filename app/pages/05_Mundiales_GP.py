"""Página 05: Mundiales y Resultados Históricos por Gran Premio (Ergast 1950–actualidad)."""

from __future__ import annotations

import base64
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
    MCLAREN_RED,
    MOTORSPORT_GREEN,
    grafico_barras_editorial,
    inject_editorial_theme,
    render_crt_header,
)
from src.domain.championship_cars import obtener_fichas_monoplazas
from src.etl.extractor import (
    extraer_clasificacion_constructores_ergast,
    extraer_clasificacion_pilotos_ergast,
    extraer_resultados_ergast,
    listar_calendario_ergast,
)

ASSETS_CARS_DIR = ROOT_DIR / "app" / "assets" / "cars"

st.set_page_config(page_title="Archivo de Temporadas — Box Plots F1", layout="wide")
inject_editorial_theme()


def _nombre_piloto(df: pd.DataFrame) -> pd.Series:
    if "givenName" in df.columns and "familyName" in df.columns:
        return (
            df["givenName"].fillna("").astype(str).str.strip()
            + " "
            + df["familyName"].fillna("").astype(str).str.strip()
        ).str.strip()
    if "driverCode" in df.columns:
        return df["driverCode"].astype(str)
    if "driverId" in df.columns:
        return df["driverId"].astype(str)
    return pd.Series(["Desconocido"] * len(df), index=df.index)


def _estandarizar_clasificacion(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Piloto"] = _nombre_piloto(out)
    if "constructorNames" in out.columns:
        out["Escudería"] = out["constructorNames"].apply(
            lambda v: ", ".join(v) if isinstance(v, list) else str(v or "")
        )
    elif "constructorName" in out.columns:
        out["Escudería"] = out["constructorName"].astype(str)
    else:
        out["Escudería"] = ""

    renombre = {
        "position": "Posición",
        "driverCode": "Código",
        "points": "Puntos",
        "wins": "Victorias",
    }
    cols = ["Posición", "Piloto"]
    for orig, dest in renombre.items():
        if orig in out.columns:
            out[dest] = out[orig]
            if dest not in cols:
                cols.append(dest)
    if "Escudería" not in cols:
        cols.insert(2, "Escudería")

    if "Puntos" in out.columns:
        out["Puntos"] = pd.to_numeric(out["Puntos"], errors="coerce").fillna(0.0)
    return out[[c for c in cols if c in out.columns]]


def _estandarizar_constructores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    renombre = {
        "position": "Posición",
        "constructorName": "Constructor",
        "constructorNationality": "Nacionalidad",
        "points": "Puntos",
        "wins": "Victorias",
    }
    cols = []
    for orig, dest in renombre.items():
        if orig in out.columns:
            out[dest] = out[orig]
            cols.append(dest)
    if "Puntos" in out.columns:
        out["Puntos"] = pd.to_numeric(out["Puntos"], errors="coerce").fillna(0.0)
    return out[cols] if cols else out


def _estandarizar_resultados_gp(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Piloto"] = _nombre_piloto(out)
    renombre = {
        "round": "Ronda",
        "raceName": "Gran Premio",
        "position": "Posición",
        "driverCode": "Código",
        "constructorName": "Escudería",
        "grid": "Grilla",
        "laps": "Vueltas",
        "points": "Puntos",
        "status": "Estado",
    }
    cols = ["Ronda", "Gran Premio", "Posición", "Piloto"]
    for orig, dest in renombre.items():
        if orig in out.columns:
            out[dest] = out[orig]
            if dest not in cols:
                cols.append(dest)

    if "Puntos" in out.columns:
        out["Puntos"] = pd.to_numeric(out["Puntos"], errors="coerce").fillna(0.0)
    if "Vueltas" in out.columns:
        out["Vueltas"] = pd.to_numeric(out["Vueltas"], errors="coerce").fillna(0).astype(int)
    return out[[c for c in cols if c in out.columns]]


def _cargar_imagen_base64(clave_archivo: str) -> str | None:
    for ext, mime in (("png", "image/png"), ("jpg", "image/jpeg"), ("jpeg", "image/jpeg"), ("webp", "image/webp")):
        img_path = ASSETS_CARS_DIR / f"{clave_archivo}.{ext}"
        if img_path.exists():
            b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{b64}"
    return None


def _render_tarjeta_individual(container, anio: int, ficha: dict, dual: bool = False) -> None:
    clave_archivo = ficha.get("archivo", str(anio))
    img_uri = _cargar_imagen_base64(clave_archivo)
    title_size = "26px" if dual else "34px"

    if img_uri:
        max_h = "260px" if dual else "310px"
        bloque_img = (
            f'<div style="background:#F2EAD7; border:1px solid #D8D0BE; border-radius:6px; padding:10px 10px 8px 10px;">'
            f'<img src="{img_uri}" style="max-height:{max_h}; width:100%; object-fit:contain; display:block; margin:0 auto; border-radius:4px;" />'
            f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:10px; color:#6E685B; '
            f'letter-spacing:0.10em; text-transform:uppercase; text-align:right; margin-top:6px;">'
            f'FIG. {anio} · PERFIL LATERAL · {ficha["modelo"].upper()}'
            f"</div></div>"
        )
    else:
        bloque_img = (
            f'<div style="border:1px dashed #D6CEBC; border-radius:6px; padding:24px 12px; '
            f'text-align:center; font-size:12px; color:#7A7467; font-family:\'IBM Plex Mono\',monospace;">'
            f"Boceto pendiente ({clave_archivo}.jpg) — se mostrará automáticamente al generarlo."
            f"</div>"
        )

    min_h_txt = "min-height:215px;" if dual else ""
    bloque_texto = (
        f'<div style="display:flex; flex-direction:column; justify-content:space-between; gap:10px; {min_h_txt}">'
        '<div>'
        '<div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap;">'
        f'<span style="font-family:\'IBM Plex Mono\',monospace; font-size:18px; font-weight:600; letter-spacing:2px; color:#5A564E;">{anio}</span>'
        '<span style="font-family:\'IBM Plex Mono\',monospace; font-size:10px; font-weight:700; text-transform:uppercase; '
        f'background:#1C1C1C; color:#F7F4EC; padding:4px 10px; border-radius:4px; letter-spacing:0.06em;">{ficha["rol"]}</span>'
        '</div>'
        f'<div style="font-family:\'Plus Jakarta Sans\',sans-serif; font-size:{title_size}; font-weight:800; line-height:1.12; margin:10px 0 12px 0; color:#1C1C1C;">{ficha["modelo"]}</div>'
        f'<div style="font-size:13px; color:#4A4A4A; margin-bottom:6px; line-height:1.45;"><strong>Ingeniería:</strong> {ficha["creditos"]}</div>'
        f'<div style="font-size:13px; color:#2E2E2E; margin-bottom:8px;"><strong>Piloto(s):</strong> {ficha["piloto"]}</div>'
        '</div>'
        f'<div style="font-size:13px; color:#333333; line-height:1.55; border-top:1px solid #E3DCCB; padding-top:10px;">{ficha["resumen"]}</div>'
        '</div>'
    )

    if dual:
        contenido = f"{bloque_texto}<div style='margin-top:14px;'>{bloque_img}</div>"
    else:
        contenido = (
            f'<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); '
            f'gap:24px; align-items:center;">{bloque_texto}{bloque_img}</div>'
        )

    container.markdown(
        f"""
        <div style="background-color:#FFFFFF; color:#1C1C1C; padding:22px 26px;
                    border-radius:10px; border:1px solid #DDD6C5; margin-top:8px;">
            {contenido}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_ficha_monoplaza(anio: int) -> None:
    """Renderiza 1 ficha (título unificado) o 2 fichas lado a lado (título dividido)."""
    fichas = obtener_fichas_monoplazas(anio)
    if not fichas:
        st.info(f"Aún no hay ficha técnica editorial cargada para {anio}.")
        return

    if len(fichas) == 1:
        _render_tarjeta_individual(st, anio, fichas[0], dual=False)
    else:
        st.caption("Temporada con títulos divididos: se muestran ambos monoplazas campeones.")
        cols = st.columns(2)
        for col, ficha in zip(cols, fichas):
            _render_tarjeta_individual(col, anio, ficha, dual=True)


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _cargar_temporada(anio: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    calendario = listar_calendario_ergast(int(anio))
    clasif_raw = extraer_clasificacion_pilotos_ergast(int(anio))
    const_raw = extraer_clasificacion_constructores_ergast(int(anio))
    clasif = _estandarizar_clasificacion(clasif_raw) if not clasif_raw.empty else pd.DataFrame()
    const = _estandarizar_constructores(const_raw) if not const_raw.empty else pd.DataFrame()
    return calendario, clasif, const


@st.cache_data(ttl=24 * 3600, show_spinner=False, max_entries=60)
def _cargar_resultados_gp(anio: int, ronda: int) -> pd.DataFrame:
    raw = extraer_resultados_ergast(int(anio), ronda=int(ronda))
    return _estandarizar_resultados_gp(raw) if not raw.empty else pd.DataFrame()


def _render_kpis_temporada(anio: int, calendario: pd.DataFrame, clasif: pd.DataFrame, constructores: pd.DataFrame) -> None:
    """Renderiza 4 tarjetas KPI editoriales con espacio amplio y sin truncamiento."""
    champ_drv, champ_drv_sub = "—", "Sin datos"
    max_wins_val, max_wins_sub = "—", "—"
    if not clasif.empty:
        top = clasif.iloc[0]
        champ_drv = str(top.get("Piloto", "—"))
        pts = top.get("Puntos", 0)
        eq = top.get("Escudería", "")
        champ_drv_sub = f"{pts:.0f} pts · {eq}" if eq else f"{pts:.0f} pts"
        if "Victorias" in clasif.columns:
            idx_w = clasif["Victorias"].astype(float).idxmax()
            w_row = clasif.loc[idx_w]
            max_wins_val = f"{int(w_row['Victorias'])} Victorias"
            max_wins_sub = str(w_row.get("Piloto", "—"))

    if anio < 1958:
        champ_const, champ_const_sub = "No disputado", "Inaugurado en 1958"
    elif not constructores.empty:
        c_top = constructores.iloc[0]
        champ_const = str(c_top.get("Constructor", "—"))
        c_pts = float(c_top.get("Puntos", 0))
        if len(constructores) > 1:
            diff = c_pts - float(constructores.iloc[1].get("Puntos", 0))
            champ_const_sub = f"{c_pts:.0f} pts · +{diff:.0f} vs 2°"
        else:
            champ_const_sub = f"{c_pts:.0f} pts"
    else:
        champ_const, champ_const_sub = "—", "Sin datos"

    n_gps = len(calendario) if calendario is not None and not calendario.empty else 0
    ganadores_distintos = (
        int((clasif["Victorias"].astype(float) > 0).sum())
        if (not clasif.empty and "Victorias" in clasif.columns)
        else 0
    )

    tarjetas = [
        ("CAMPEÓN DE PILOTOS", champ_drv, champ_drv_sub),
        ("CAMPEÓN CONSTRUCTORES", champ_const, champ_const_sub),
        ("GRANDES PREMIOS", f"{n_gps} GPs", f"{ganadores_distintos} ganadores distintos" if ganadores_distintos else "Calendario oficial"),
        ("MÁXIMO GANADOR", max_wins_val, max_wins_sub),
    ]
    bloques = "".join(
        f"""
        <div style="background:rgba(255,255,255,0.68); border:1px solid rgba(28,28,28,0.14);
                    border-top:3px solid #E11D24; border-radius:6px; padding:14px 16px; min-width:0;">
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#5A564E;
                        letter-spacing:0.06em; text-transform:uppercase;">{lbl}</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:clamp(1.05rem,1.45vw,1.32rem);
                        font-weight:800; color:#1C1C1C; margin:6px 0 4px 0; line-height:1.2;
                        word-break:break-word;">{val}</div>
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.74rem; color:#277B47;
                        font-weight:600; line-height:1.3;">{sub}</div>
        </div>
        """
        for lbl, val, sub in tarjetas
    )
    st.markdown(
        f"""
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr));
                    gap:14px; margin:12px 0 20px 0;">
            {bloques}
        </div>
        """,
        unsafe_allow_html=True,
    )


col_sel, col_info = st.columns([1, 3])
anios_disp = list(range(2026, 1949, -1))
anio = col_sel.selectbox("Temporada", anios_disp, index=anios_disp.index(2024))

render_crt_header(
    canal=f"CH 02 · ARCHIVE {anio}",
    titulo=f"🏆 Archivo de Temporadas — {anio}",
    subtitulo="Campeones, monoplazas referentes, clasificación mundial y resultados carrera por carrera · Fuente: Ergast / Jolpica",
)

with st.spinner(f"Cargando temporada {anio}..."):
    try:
        calendario, clasif, constructores = _cargar_temporada(int(anio))
    except Exception as exc:
        st.error(f"Error consultando Ergast/Jolpica para {anio}: {exc}")
        calendario, clasif, constructores = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

col_info.markdown(
    f"<div style='padding-top:32px; font-family:\"IBM Plex Mono\",monospace; font-size:0.78rem; color:#5A564E;'>"
    f"Temporada {anio} · {len(calendario)} Grandes Premios registrados"
    f"</div>",
    unsafe_allow_html=True,
)

_render_kpis_temporada(int(anio), calendario, clasif, constructores)

tab_cars, tab_clasif, tab_gps = st.tabs(
    ["🏎️ Portada & Monoplazas", "📊 Clasificación Mundial", "🏁 Carrera por Carrera"]
)

with tab_cars:
    _render_ficha_monoplaza(int(anio))

with tab_clasif:
    st.subheader(f"Campeonato de Pilotos — {anio}")
    if clasif.empty:
        st.warning("No se encontró clasificación oficial de pilotos para esta temporada.")
    else:
        c_g, c_t = st.columns([1.15, 1])
        with c_g:
            if "Puntos" in clasif.columns and "Piloto" in clasif.columns:
                fig = grafico_barras_editorial(
                    clasif.head(12),
                    categoria_col="Piloto",
                    valor_col="Puntos",
                    titulo=f"Top 12 Pilotos por Puntos — {anio}",
                    sufijo_texto=" pts",
                    color_lider=MCLAREN_RED,
                    formato_valor=".0f",
                )
                st.plotly_chart(fig, width="stretch")
        with c_t:
            st.dataframe(clasif, width="stretch", hide_index=True, height=440)

    st.divider()
    st.subheader(f"Campeonato de Constructores — {anio}")
    if int(anio) < 1958:
        st.info(
            "Nota histórica FIA: Entre **1950 y 1957** no existía el Campeonato Mundial de Constructores "
            "(se inauguró en **1958**)."
        )
    elif constructores.empty:
        st.warning("No se encontraron datos oficiales de constructores para esta temporada.")
    else:
        c_cg, c_ct = st.columns([1.15, 1])
        with c_cg:
            if "Puntos" in constructores.columns and "Constructor" in constructores.columns:
                fig_c = grafico_barras_editorial(
                    constructores.head(12),
                    categoria_col="Constructor",
                    valor_col="Puntos",
                    titulo=f"Constructores por Puntos — {anio}",
                    sufijo_texto=" pts",
                    color_lider=MOTORSPORT_GREEN,
                    formato_valor=".0f",
                )
                st.plotly_chart(fig_c, width="stretch")
        with c_ct:
            st.dataframe(constructores, width="stretch", hide_index=True, height=400)

with tab_gps:
    mapa_gp: dict[str, int] = {}
    if calendario is not None and not calendario.empty and "round" in calendario.columns:
        for _, row in calendario.sort_values("round").iterrows():
            r_num = int(row["round"])
            nombre = str(row.get("raceName", f"Ronda {r_num}"))
            mapa_gp[f"R{r_num} — {nombre}"] = r_num

    if not mapa_gp:
        st.info(f"No hay calendario de carreras disponible para {anio}.")
    else:
        gp_sel = st.selectbox(f"Selecciona el Gran Premio ({len(mapa_gp)} carreras)", list(mapa_gp.keys()))
        ronda_sel = mapa_gp[gp_sel]
        with st.spinner(f"Cargando resultados de {gp_sel}..."):
            try:
                df_gp = _cargar_resultados_gp(int(anio), int(ronda_sel))
            except Exception as exc:
                st.error(f"Error cargando {gp_sel}: {exc}")
                df_gp = pd.DataFrame()

        if df_gp.empty:
            st.info("No se encontraron resultados oficiales para este Gran Premio (posiblemente aún no disputado).")
        else:
            top3 = df_gp.head(3)
            medallas = ["🥇 1° LUGAR", "🥈 2° LUGAR", "🥉 3° LUGAR"]
            pod_cols = st.columns(3)
            for idx_p, (_, r_p) in enumerate(top3.iterrows()):
                borde = "#E11D24" if idx_p == 0 else "#2A2A2A"
                pts_txt = f"{r_p.get('Puntos', 0):.0f} pts" if "Puntos" in r_p else ""
                grilla_txt = f"Grilla P{int(r_p['Grilla'])}" if "Grilla" in r_p and pd.notna(r_p["Grilla"]) else ""
                pod_cols[idx_p].markdown(
                    f"""
                    <div style="background:#FFFFFF; border:1px solid rgba(28,28,28,0.14);
                                border-top:4px solid {borde}; border-radius:8px; padding:14px 16px;
                                margin:8px 0 14px 0;">
                        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:#5A564E;">
                            {medallas[idx_p]} · {pts_txt}
                        </div>
                        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-weight:800;
                                    font-size:1.12rem; color:#1C1C1C; margin:4px 0;">
                            {r_p.get('Piloto', '—')}
                        </div>
                        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.74rem; color:#5A564E;">
                            {r_p.get('Escudería', '—')} · {grilla_txt}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.dataframe(df_gp, width="stretch", hide_index=True)
