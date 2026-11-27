"""Página 10: Raceboxd — Diario y Reseñas de Grandes Premios estilo Letterboxd."""

from __future__ import annotations

import html
import json
import sys
import uuid
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = APP_DIR.parent
for _p in (str(ROOT_DIR), str(APP_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.sticker_generator import generar_sticker_ticket_png
from components.theme import (
    BAR_CHARCOAL,
    INK_CHARCOAL,
    MOTORSPORT_GREEN,
    estilizar_plotly_editorial,
    inject_editorial_theme,
    render_crt_header,
)
from src.etl.extractor import (
    extraer_clasificacion_pilotos_ergast,
    extraer_resultados_ergast,
    listar_calendario_ergast,
)

DATA_FILE = ROOT_DIR / "data" / "raceboxd.json"

ETIQUETAS_CARRERA = [
    # Épica y manejo
    "CÁTEDRA",
    "EN MOJADO",
    "PODIO LOCO",
    "INFARTO",
    # Caos y mecánica
    "CAOS MECÁNICO",
    "BANDERA ROJA",
    "RULETA RUSA",
    "DRAMA RADIO",
    # Muro y ritmo
    "SUICIDIO BOX",
    "UNDERCUT",
    "TREN DRS",
    "SIESTA",
]

_SEMILLA_INICIAL: List[Dict[str, Any]] = []

_MESES_ES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE",
}


def _cargar_diario() -> List[Dict[str, Any]]:
    """Diario privado por sesión de usuario (listo para migrar a BD con cuentas en v2)."""
    if "raceboxd_diario" not in st.session_state:
        st.session_state["raceboxd_diario"] = list(_SEMILLA_INICIAL)
    return list(st.session_state["raceboxd_diario"])


def _guardar_diario(entradas: List[Dict[str, Any]]) -> None:
    st.session_state["raceboxd_diario"] = list(entradas)


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def _calendario_anio(anio: int) -> List[Dict[str, Any]]:
    cal = listar_calendario_ergast(int(anio))
    if cal is None or cal.empty or "round" not in cal.columns:
        return []
    filas = []
    for _, row in cal.sort_values("round").iterrows():
        nombre = str(row.get("raceName", f"Ronda {int(row['round'])}"))
        pais = str(row.get("country", nombre))
        codigo = "".join(ch for ch in pais.upper() if ch.isalpha())[:3] or "GP"
        filas.append({"ronda": int(row["round"]), "gp": nombre, "codigo": codigo})
    return filas


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def _pilotos_anio(anio: int) -> List[str]:
    df = extraer_clasificacion_pilotos_ergast(int(anio))
    if df is None or df.empty:
        return []
    if "givenName" in df.columns and "familyName" in df.columns:
        nombres = (df["givenName"].fillna("") + " " + df["familyName"].fillna("")).str.strip().tolist()
        return [n for n in nombres if n]
    return []


@st.cache_data(ttl=24 * 3600, show_spinner=False, max_entries=60)
def _podio_gp(anio: int, ronda: int) -> str:
    """Devuelve el podio oficial compacto: 'P1 VER · P2 NOR · P3 LEC'."""
    df = extraer_resultados_ergast(int(anio), ronda=int(ronda))
    if df is None or df.empty:
        return ""
    partes = []
    for idx_p, (_, row) in enumerate(df.head(3).iterrows(), start=1):
        cod = str(row.get("driverCode") or "").strip().upper()
        if not cod:
            ape = str(row.get("familyName") or row.get("driverId") or "").strip().upper()
            cod = ape[:3]
        if cod:
            partes.append(f"P{idx_p} {cod}")
    return " · ".join(partes)


def _esc(val: Any) -> str:
    return html.escape(str(val or ""), quote=True)


def _fmt_estrellas(val: float) -> str:
    enteras = int(val)
    media = "½" if (val - enteras) >= 0.5 else ""
    return ("★" * enteras) + media


st.set_page_config(page_title="Raceboxd — Box Plots F1", layout="wide")
inject_editorial_theme()
render_crt_header(
    canal="CH 06 · RACEBOXD",
    titulo="Raceboxd — Diario y Reseñas de Grandes Premios",
    subtitulo="Puntúa carreras históricas y actuales (0.5★ – 5★), guarda tus favoritas y escribe tu crónica de pista.",
)

entradas = _cargar_diario()
entradas_ord = sorted(entradas, key=lambda x: str(x.get("fecha_vista", "")), reverse=True)

tab_diary, tab_reviews, tab_stats, tab_log = st.tabs(
    ["Diary", "Reviews", "Top & Stats", "✚ Log Race"]
)

with tab_diary:
    if not entradas_ord:
        st.info("Tu diario está vacío. Usa la pestaña **+ Log Race** para registrar tu primer Gran Premio.")
    else:
        grupos_mes: Dict[str, List[Dict[str, Any]]] = {}
        for item in entradas_ord:
            try:
                dt = date.fromisoformat(str(item.get("fecha_vista", "2024-01-01")))
                clave_mes = f"{_MESES_ES[dt.month]} {dt.year}"
                dia_txt = f"{dt.day:02d}"
            except Exception:
                clave_mes = str(item.get("anio", "HISTÓRICO"))
                dia_txt = "--"
            grupos_mes.setdefault(clave_mes, []).append({**item, "_dia": dia_txt})

        for mes, filas in grupos_mes.items():
            st.markdown(
                f'<div style="background:#EDE8DC; border:1px solid rgba(28,28,28,0.12); border-radius:6px; '
                f'padding:6px 14px; font-family:\'IBM Plex Mono\',monospace; font-size:0.72rem; '
                f'font-weight:700; letter-spacing:0.1em; color:#5A564E; margin:14px 0 8px 0;">{mes}</div>',
                unsafe_allow_html=True,
            )
            for r in filas:
                est = _fmt_estrellas(float(r.get("estrellas", 0)))
                corazon = '<span style="margin-left:6px; font-size:0.95rem;">🏎️</span>' if r.get("favorita") else ""
                ico_rev = '<span style="color:#5A564E; margin-left:8px; font-family:\'IBM Plex Mono\',monospace;">≡</span>' if r.get("resena") else ""
                dotd_html = (
                    f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.72rem; color:#5A564E; '
                    f'background:#F7F4EC; border:1px solid rgba(28,28,28,0.12); padding:4px 10px; border-radius:4px;">'
                    f'DOTD: {_esc(r["dotd"])}</div>'
                    if r.get("dotd")
                    else ""
                )
                bg_poster = (
                    "linear-gradient(155deg, #16241B 0%, #277B47 100%)"
                    if float(r.get("estrellas", 0)) >= 5.0
                    else "linear-gradient(155deg, #1C1C1C 0%, #2E2B26 65%, #E11D24 100%)"
                )
                tags_html = "".join(
                    f'<span style="font-family:\'IBM Plex Mono\',monospace; font-size:0.66rem; background:#EDE8DC; '
                    f'border:1px solid rgba(28,28,28,0.14); padding:2px 6px; border-radius:4px; margin-right:4px;">{_esc(t)}</span>'
                    for t in r.get("etiquetas", [])
                )
                st.markdown(
                    f'<div style="background:#FFFFFF; border:1px solid rgba(28,28,28,0.12); border-radius:8px; '
                    f'padding:12px 16px; margin-bottom:8px; display:grid; grid-template-columns:54px 52px 1fr auto; '
                    f'align-items:center; gap:14px;">'
                    f'<div style="width:48px; height:48px; border:1px solid rgba(28,28,28,0.2); border-radius:6px; '
                    f'background:#F7F4EC; display:flex; flex-direction:column; align-items:center; justify-content:center; font-family:\'IBM Plex Mono\',monospace;">'
                    f'<span style="font-size:1.02rem; font-weight:700; line-height:1;">{_esc(r["_dia"])}</span>'
                    f'<span style="font-size:0.58rem; color:#5A564E;">R{_esc(r.get("ronda", "?"))}</span></div>'
                    f'<div style="width:46px; height:64px; border-radius:4px; border:1px solid #1C1C1C; background:{bg_poster}; '
                    f'color:#F7F4EC; display:flex; flex-direction:column; justify-content:space-between; padding:5px 4px; '
                    f'font-family:\'IBM Plex Mono\',monospace; text-align:center;">'
                    f'<span style="font-size:0.58rem; opacity:0.85;">{_esc(r.get("anio", ""))}</span>'
                    f'<span style="font-size:0.75rem; font-weight:700;">{_esc(r.get("codigo", "GP"))}</span>'
                    f'<span style="font-size:0.56rem; opacity:0.85;">GP</span></div>'
                    f'<div><div style="font-family:\'Plus Jakarta Sans\',sans-serif; font-weight:800; font-size:1.04rem; color:#1C1C1C;">'
                    f'{_esc(r.get("gp", "Gran Premio"))} <span style="font-family:\'IBM Plex Mono\',monospace; font-weight:500; font-size:0.82rem; color:#5A564E;">{_esc(r.get("anio", ""))}</span></div>'
                    f'<div style="color:#277B47; font-size:0.95rem; letter-spacing:1px; margin-top:3px;">{est}{corazon}{ico_rev}</div>'
                    f'<div style="margin-top:5px;">{tags_html}</div></div>'
                    f'{dotd_html}</div>',
                    unsafe_allow_html=True,
                )

with tab_reviews:
    if not entradas_ord:
        st.info("Aún no hay carreras registradas. Usa **+ Log Race** para puntuar un Gran Premio y descargar tu ticket.")
    else:
        for r in entradas_ord:
            est = _fmt_estrellas(float(r.get("estrellas", 0)))
            corazon = ' <span style="font-size:1.0rem;">🏎️</span>' if r.get("favorita") else ""
            texto_resena = str(r.get("resena", "")).strip()
            bloque_resena = (
                f'<p style="font-size:0.92rem; line-height:1.5; color:#2A2A2A; margin:0;">{_esc(texto_resena)}</p>'
                if texto_resena
                else ""
            )
            bg_poster = (
                "linear-gradient(155deg, #16241B 0%, #277B47 100%)"
                if float(r.get("estrellas", 0)) >= 5.0
                else "linear-gradient(155deg, #1C1C1C 0%, #2E2B26 65%, #E11D24 100%)"
            )
            st.markdown(
                f'<div style="background:#FFFFFF; border:1px solid rgba(28,28,28,0.14); border-left:4px solid #E11D24; '
                f'border-radius:10px; padding:20px 24px; margin-bottom:14px; display:grid; grid-template-columns:1fr 92px; gap:20px; align-items:start;">'
                f'<div>'
                f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.76rem; color:#5A564E; margin-bottom:6px;">'
                f'@{_esc(r.get("usuario", "fan"))} · Piloto del Día: {_esc(r.get("dotd") or "—")}</div>'
                f'<div style="font-family:\'Plus Jakarta Sans\',sans-serif; font-size:1.28rem; font-weight:800; color:#1C1C1C;">'
                f'{_esc(r.get("gp", ""))} <span style="font-family:\'IBM Plex Mono\',monospace; font-weight:500; font-size:0.86rem; color:#5A564E;">{_esc(r.get("anio", ""))}</span></div>'
                f'<div style="color:#277B47; font-size:1.02rem; margin:4px 0;">{est}{corazon}</div>'
                f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.72rem; color:#5A564E; margin-bottom:10px;">'
                f'Vista el {_esc(r.get("fecha_vista", "—"))} · Ronda {_esc(r.get("ronda", "?"))}</div>'
                f'{bloque_resena}'
                f'</div>'
                f'<div style="width:86px; height:120px; border-radius:6px; border:1px solid #1C1C1C; background:{bg_poster}; '
                f'color:#F7F4EC; display:flex; flex-direction:column; justify-content:space-between; padding:10px 6px; '
                f'font-family:\'IBM Plex Mono\',monospace; text-align:center;">'
                f'<span style="font-size:0.62rem; opacity:0.85;">R{_esc(r.get("ronda", "?"))} · {_esc(r.get("anio", ""))}</span>'
                f'<span style="font-size:1.15rem; font-weight:700;">{_esc(r.get("codigo", "GP"))}</span>'
                f'<span style="font-size:0.58rem; opacity:0.85;">RACEBOXD</span></div></div>',
                unsafe_allow_html=True,
            )
            r_con_podio = dict(r)
            if not r_con_podio.get("podio"):
                try:
                    r_con_podio["podio"] = _podio_gp(int(r.get("anio", 2024)), int(r.get("ronda", 1)))
                except Exception:
                    r_con_podio["podio"] = ""
            c_ig, c_x, c_ed, _ = st.columns([1.2, 1.3, 0.7, 1.3])
            c_ig.download_button(
                "Descargar Ticket Vertical (9:16)",
                data=generar_sticker_ticket_png(r_con_podio, formato="ig"),
                file_name=f"raceboxd_{r.get('codigo', 'gp').lower()}_{r.get('anio', '')}_vertical.png",
                mime="image/png",
                key=f"dl_ig_{r.get('id')}",
            )
            c_x.download_button(
                "Descargar Ticket Panorámico (16:9)",
                data=generar_sticker_ticket_png(r_con_podio, formato="x"),
                file_name=f"raceboxd_{r.get('codigo', 'gp').lower()}_{r.get('anio', '')}_panoramico.png",
                mime="image/png",
                key=f"dl_x_{r.get('id')}",
            )
            rid = r.get("id")
            with c_ed.popover("Editar"):
                with st.form(f"edit_form_{rid}"):
                    e1, e2 = st.columns([2, 1])
                    n_est = e1.select_slider(
                        "Calificación (★)",
                        options=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                        value=float(r.get("estrellas", 4.5)),
                    )
                    n_fav = e2.checkbox("Favorita 🏎️", value=bool(r.get("favorita", False)))
                    tags_prev = [t for t in (r.get("etiquetas") or []) if t in ETIQUETAS_CARRERA][:2]
                    n_tags = st.multiselect(
                        "Etiquetas rápidas (máx. 2)",
                        options=ETIQUETAS_CARRERA,
                        default=tags_prev,
                        max_selections=2,
                    )
                    n_resena = st.text_area(
                        "Reseña / Crónica corta",
                        value=str(r.get("resena", "")),
                        max_chars=500,
                    )
                    if st.form_submit_button("Guardar cambios", type="primary"):
                        actualizadas = []
                        for item in entradas:
                            if item.get("id") == rid:
                                item = dict(item)
                                item["estrellas"] = float(n_est)
                                item["favorita"] = bool(n_fav)
                                item["etiquetas"] = list(n_tags)[:2]
                                item["resena"] = n_resena.strip()
                            actualizadas.append(item)
                        _guardar_diario(actualizadas)
                        st.rerun()

with tab_stats:
    if not entradas:
        st.info("Registra carreras para ver tus estadísticas personales.")
    else:
        df_s = pd.DataFrame(entradas)
        prom = float(df_s["estrellas"].mean())
        favs = int(df_s["favorita"].sum())
        mejor = df_s.sort_values(["estrellas", "anio"], ascending=[False, False]).iloc[0]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Carreras Registradas", len(df_s))
        k2.metric("Promedio", f"{prom:.2f} ★")
        k3.metric("Favoritas", f"{favs} 🏎️")
        k4.metric("Mejor Valorada", f"{mejor['codigo']} {mejor['anio']}")

        # Histograma de estrellas estilo Letterboxd (0.5★ a 5.0★)
        escala = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        conteos = [int((df_s["estrellas"] == s).sum()) for s in escala]
        max_c = max(conteos) if conteos else 0
        colores_h = [MOTORSPORT_GREEN if (c == max_c and c > 0) else BAR_CHARCOAL for c in conteos]
        fig_hist = go.Figure(
            go.Bar(
                x=[f"{s:.1f}★" for s in escala],
                y=conteos,
                marker=dict(color=colores_h),
                text=[str(c) if c > 0 else "" for c in conteos],
                textposition="outside",
                cliponaxis=False,
                textfont=dict(family="IBM Plex Mono, monospace", size=11, color=INK_CHARCOAL),
            )
        )
        estilizar_plotly_editorial(fig_hist, titulo="Distribución de Calificaciones (0.5★ – 5.0★)", altura=270)
        fig_hist.update_yaxes(showticklabels=False, range=[0, max(1, max_c) * 1.28])
        st.plotly_chart(fig_hist, width="stretch")

        st.divider()
        st.subheader("Gestionar entradas")
        opciones_del = {f"{e['anio']} R{e['ronda']} — {e['gp']} ({e['estrellas']}★)": e["id"] for e in entradas_ord}
        c_del, c_btn = st.columns([2, 1], vertical_alignment="bottom")
        sel_del = c_del.selectbox("Eliminar una entrada", ["(Seleccionar)"] + list(opciones_del.keys()))
        if sel_del != "(Seleccionar)" and c_btn.button("Eliminar entrada"):
            nuevas = [e for e in entradas if e["id"] != opciones_del[sel_del]]
            _guardar_diario(nuevas)
            st.success("Entrada eliminada.")
            st.rerun()

with tab_log:
    st.subheader("Registrar un Gran Premio en tu Diario")
    c_a, c_gp = st.columns([1, 2])
    anios_rb = list(range(2026, 1949, -1))
    anio_sel = c_a.selectbox("Temporada", anios_rb, index=anios_rb.index(2024), key="rb_anio")

    try:
        cal_anio = _calendario_anio(int(anio_sel))
    except Exception:
        cal_anio = []

    if cal_anio:
        mapa_cal = {f"R{c['ronda']} — {c['gp']}": c for c in cal_anio}
        gp_etiqueta = c_gp.selectbox("Gran Premio", list(mapa_cal.keys()), key="rb_gp")
        gp_info = mapa_cal[gp_etiqueta]
    else:
        gp_txt = c_gp.text_input("Nombre del Gran Premio", value="Monaco Grand Prix")
        gp_info = {"ronda": 1, "gp": gp_txt, "codigo": gp_txt[:3].upper() or "GP"}

    try:
        pilotos_anio = _pilotos_anio(int(anio_sel))
    except Exception:
        pilotos_anio = []

    with st.form("form_raceboxd", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        estrellas = f1.select_slider(
            "Calificación (★)",
            options=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
            value=4.5,
        )
        usuario = f2.text_input("Tu alias", value="", placeholder="Ej. tu_usuario", max_chars=24)
        fecha_v = f3.date_input("Fecha vista", value=date.today())

        f4, f5 = st.columns([2, 1])
        opciones_dotd = ["(Sin especificar)"] + pilotos_anio
        dotd_sel = f4.selectbox("Piloto del Día (parrilla oficial)", opciones_dotd)
        favorita = f5.checkbox("Marcar como favorita 🏎️", value=False)

        etiquetas = st.multiselect(
            "Etiquetas rápidas de la carrera (opcional, máx. 2)",
            ETIQUETAS_CARRERA,
            max_selections=2,
        )
        resena = st.text_area("Reseña / Crónica corta (opcional)", max_chars=500, placeholder="¿Qué hizo inolvidable esta carrera?")

        if st.form_submit_button("Guardar en Raceboxd", type="primary"):
            n_sesion = int(st.session_state.get("rb_count_sesion", 0))
            if n_sesion >= 10:
                st.warning("Has alcanzado el límite de 10 registros por sesión.")
            else:
                try:
                    podio_txt = _podio_gp(int(anio_sel), int(gp_info["ronda"]))
                except Exception:
                    podio_txt = ""
                nueva = {
                    "id": str(uuid.uuid4())[:8],
                    "usuario": usuario.strip() or "anónimo",
                    "anio": int(anio_sel),
                    "ronda": int(gp_info["ronda"]),
                    "gp": gp_info["gp"],
                    "codigo": gp_info["codigo"],
                    "fecha_vista": fecha_v.isoformat(),
                    "estrellas": float(estrellas),
                    "favorita": bool(favorita),
                    "dotd": "" if dotd_sel == "(Sin especificar)" else dotd_sel,
                    "podio": podio_txt,
                    "etiquetas": etiquetas,
                    "resena": resena.strip(),
                }
                entradas.append(nueva)
                _guardar_diario(entradas)
                st.session_state["rb_count_sesion"] = n_sesion + 1
                st.success(f"Guardado: {gp_info['gp']} {anio_sel} ({_fmt_estrellas(float(estrellas))})")
                st.rerun()
