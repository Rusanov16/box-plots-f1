"""Extractores seguros para FastF1 (2018+) y Ergast/Jolpica (1950+) — Función F1/F3.

Reglas clave:
- Siempre habilita `fastf1.Cache.enable_cache(CACHE_DIR)`.
- Siempre usa `session.laps.pick_drivers([...])` (nunca `pick_driver()`).
- Valida respuestas vacías de FastF1 y Ergast antes de indexar.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import fastf1
from fastf1.ergast import Ergast
import pandas as pd

from src.config import CACHE_DIR, ensure_runtime_dirs
from src.domain.catalogos import normalizar_codigo_piloto


def habilitar_cache_fastf1() -> str:
    """Crea y habilita el directorio local de caché de FastF1."""
    ensure_runtime_dirs()
    ruta = str(CACHE_DIR)
    fastf1.Cache.enable_cache(ruta)
    return ruta


def extraer_sesion_fastf1(
    anio: int,
    gp: Any,
    cod_sesion: str,
    cargar_telemetria: bool = True,
    pilotos: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Extrae metadatos, vueltas, resultados y telemetría de una sesión FastF1 (anio >= 2018)."""
    if anio < 2018:
        raise ValueError(
            f"FastF1 detallado solo cubre temporadas >= 2018 (recibido: {anio}). "
            "Use `extraer_resultados_ergast` para temporadas históricas."
        )

    habilitar_cache_fastf1()
    session = fastf1.get_session(anio, gp, cod_sesion)
    session.load(laps=True, telemetry=cargar_telemetria, weather=False, messages=False)

    try:
        laps = session.laps
    except Exception:
        laps = None

    if laps is None or laps.empty:
        laps_df = pd.DataFrame()
    else:
        if pilotos:
            codigos = [normalizar_codigo_piloto(p) for p in pilotos]
            laps_df = laps.pick_drivers(codigos).copy()
        else:
            laps_df = laps.copy()

    telemetria_por_vuelta: List[Dict[str, Any]] = []
    if cargar_telemetria and not laps_df.empty:
        for _, lap in laps_df.iterrows():
            try:
                tel = lap.get_car_data()
                if tel is not None and not tel.empty:
                    telemetria_por_vuelta.append(
                        {
                            "id_piloto": normalizar_codigo_piloto(lap["Driver"]),
                            "numero_vuelta": int(lap["LapNumber"]),
                            "telemetry": tel.copy(),
                        }
                    )
            except Exception:
                continue

    evento_raw = getattr(session, "event", None)
    evento = evento_raw if evento_raw is not None else {}
    try:
        fecha_sesion = session.date
    except Exception:
        fecha_sesion = evento.get("EventDate", None)

    try:
        res_raw = session.results
        results_df = res_raw.copy() if res_raw is not None else pd.DataFrame()
    except Exception:
        results_df = pd.DataFrame()

    metadata = {
        "anio": int(anio),
        "ronda": int(evento.get("RoundNumber", 0) or 0),
        "nombre_evento": str(evento.get("EventName", gp)),
        "ubicacion": str(evento.get("Location", "")) or None,
        "pais": str(evento.get("Country", "")) or None,
        "cod_sesion": cod_sesion.strip().upper()[:3],
        "fecha_sesion": fecha_sesion,
    }

    return {
        "metadata": metadata,
        "laps": laps_df,
        "results": results_df,
        "telemetry": telemetria_por_vuelta,
    }


def listar_calendario_ergast(anio: int) -> pd.DataFrame:
    """Obtiene el calendario completo de Grandes Premios de una temporada (1950–actualidad)."""
    ergast = Ergast()
    df = ergast.get_race_schedule(season=int(anio), limit=100)
    if df is None or df.empty:
        return pd.DataFrame()
    return df.copy()


def extraer_clasificacion_pilotos_ergast(anio: int) -> pd.DataFrame:
    """Obtiene la clasificación oficial del campeonato de pilotos de una temporada."""
    ergast = Ergast()
    resp = ergast.get_driver_standings(season=int(anio), limit=100)
    if resp is None or not getattr(resp, "content", None):
        return pd.DataFrame()
    frames = [df for df in resp.content if df is not None and not df.empty]
    if not frames:
        return pd.DataFrame()
    return frames[-1].copy()


def extraer_clasificacion_constructores_ergast(anio: int) -> pd.DataFrame:
    """Obtiene la clasificación oficial del campeonato de constructores (1958–actualidad)."""
    if int(anio) < 1958:
        return pd.DataFrame()
    ergast = Ergast()
    resp = ergast.get_constructor_standings(season=int(anio), limit=100)
    if resp is None or not getattr(resp, "content", None):
        return pd.DataFrame()
    frames = [df for df in resp.content if df is not None and not df.empty]
    if not frames:
        return pd.DataFrame()
    return frames[-1].copy()


def extraer_temporada_completa_ergast(anio: int) -> pd.DataFrame:
    """Descarga todos los resultados de carrera de una temporada paginando Ergast."""
    ergast = Ergast()
    frames: List[pd.DataFrame] = []
    offset = 0
    limit = 100
    while True:
        resp = ergast.get_race_results(season=int(anio), limit=limit, offset=offset)
        if resp is None or not getattr(resp, "content", None):
            break
        desc = getattr(resp, "description", None)
        filas_lote = 0
        for idx, df in enumerate(resp.content):
            if df is None or df.empty:
                continue
            copia = df.copy()
            filas_lote += len(copia)
            if desc is not None and idx < len(desc):
                if "round" in desc.columns:
                    copia["round"] = desc.iloc[idx]["round"]
                if "raceName" in desc.columns:
                    copia["raceName"] = desc.iloc[idx]["raceName"]
            frames.append(copia)
        if filas_lote < limit:
            break
        offset += limit
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def extraer_vueltas_ergast(anio: int, ronda: int) -> pd.DataFrame:
    """Descarga tiempos vuelta a vuelta desde Ergast (disponible desde 1996)."""
    if int(anio) < 1996:
        return pd.DataFrame()
    ergast = Ergast()
    frames: List[pd.DataFrame] = []
    offset = 0
    limit = 100
    while True:
        resp = ergast.get_lap_times(season=int(anio), round=int(ronda), limit=limit, offset=offset)
        if resp is None or not getattr(resp, "content", None):
            break
        filas_lote = 0
        for df in resp.content:
            if df is not None and not df.empty:
                frames.append(df.copy())
                filas_lote += len(df)
        if filas_lote < limit:
            break
        offset += limit
        if offset >= 2000:
            break
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def extraer_resultados_ergast(anio: int, ronda: Optional[int] = None) -> pd.DataFrame:
    """Extrae resultados históricos de carrera desde `fastf1.ergast.Ergast` (1950–actualidad)."""
    ergast = Ergast()
    kwargs: Dict[str, Any] = {"season": int(anio), "limit": 100}
    if ronda is not None:
        kwargs["round"] = int(ronda)

    resp = ergast.get_race_results(**kwargs)
    if resp is None or not getattr(resp, "content", None):
        return pd.DataFrame()

    desc = getattr(resp, "description", None)
    frames = []
    for idx, df in enumerate(resp.content):
        if df is None or df.empty:
            continue
        copia = df.copy()
        if desc is not None and idx < len(desc):
            if "round" in desc.columns:
                copia["round"] = desc.iloc[idx]["round"]
            if "raceName" in desc.columns:
                copia["raceName"] = desc.iloc[idx]["raceName"]
        frames.append(copia)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def comparar_consistencia_fastf1_ergast(
    resultados_fastf1: pd.DataFrame,
    resultados_ergast: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """Compara posiciones finales entre FastF1 y Ergast (Control F3) sin detener el ETL."""
    discrepancias: List[Dict[str, Any]] = []
    if (
        resultados_fastf1 is None
        or resultados_fastf1.empty
        or resultados_ergast is None
        or resultados_ergast.empty
    ):
        return discrepancias

    col_f1_drv = "Abbreviation" if "Abbreviation" in resultados_fastf1.columns else "Driver"
    col_erg_drv = "driverCode" if "driverCode" in resultados_ergast.columns else "Driver"
    if col_f1_drv not in resultados_fastf1.columns or col_erg_drv not in resultados_ergast.columns:
        return discrepancias

    pos_f1 = {
        normalizar_codigo_piloto(row[col_f1_drv]): row.get("Position")
        for _, row in resultados_fastf1.iterrows()
        if pd.notna(row.get(col_f1_drv))
    }
    pos_erg = {
        normalizar_codigo_piloto(row[col_erg_drv]): row.get("position")
        for _, row in resultados_ergast.iterrows()
        if pd.notna(row.get(col_erg_drv))
    }

    for piloto, p_f1 in pos_f1.items():
        if piloto in pos_erg and pd.notna(p_f1) and pd.notna(pos_erg[piloto]):
            if int(float(p_f1)) != int(float(pos_erg[piloto])):
                discrepancias.append(
                    {
                        "id_piloto": piloto,
                        "posicion_fastf1": int(float(p_f1)),
                        "posicion_ergast": int(float(pos_erg[piloto])),
                    }
                )
    return discrepancias
