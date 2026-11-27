"""Validadores de integridad y rangos físicos para vueltas y telemetría (Función F3).

Preserva siempre los datos originales: las funciones retornan únicamente las
filas con anomalías detectadas sin eliminar registros del DataFrame de entrada.
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

COMPUESTOS_ESTANDAR = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]

RANGOS_TELEMETRIA = {
    "Speed": (0.0, 400.0),
    "RPM": (0.0, 20000.0),
    "nGear": (0, 8),
    "Throttle": (0.0, 100.0),
}


def validar_tiempo_vuelta(laps_df: pd.DataFrame) -> pd.DataFrame:
    """Retorna filas con `LapTime` <= 0 (ignorando `NaT`/`NaN`)."""
    if laps_df is None or laps_df.empty or "LapTime" not in laps_df.columns:
        return pd.DataFrame()

    serie = laps_df["LapTime"]
    if pd.api.types.is_timedelta64_dtype(serie):
        segundos = serie.dt.total_seconds()
        mask = segundos.notna() & (segundos <= 0)
    else:
        numerico = pd.to_numeric(serie, errors="coerce")
        mask = numerico.notna() & (numerico <= 0)
    return laps_df.loc[mask]


def validar_compuestos(laps_df: pd.DataFrame) -> pd.DataFrame:
    """Retorna filas con compuestos no nulos fuera del estándar FIA."""
    if laps_df is None or laps_df.empty or "Compound" not in laps_df.columns:
        return pd.DataFrame()

    serie = laps_df["Compound"]
    no_nulos = serie.notna()
    normalizados = serie.astype(str).str.strip().str.upper()
    mask = no_nulos & (~normalizados.isin(COMPUESTOS_ESTANDAR))
    return laps_df.loc[mask]


def validar_vida_neumatico(
    laps_df: pd.DataFrame, min_val: float = 0, max_val: float = 100
) -> pd.DataFrame:
    """Retorna filas con `TyreLife` fuera del rango `[min_val, max_val]`."""
    if laps_df is None or laps_df.empty or "TyreLife" not in laps_df.columns:
        return pd.DataFrame()

    numerico = pd.to_numeric(laps_df["TyreLife"], errors="coerce")
    mask = numerico.notna() & ((numerico < min_val) | (numerico > max_val))
    return laps_df.loc[mask]


def validar_telemetria(telemetry_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Valida rangos físicos en columnas de telemetría (`Speed`, `RPM`, `nGear`, `Throttle`).

    Retorna un diccionario `{columna: DataFrame_anomalias}` con las filas fuera de rango.
    """
    resultado: Dict[str, pd.DataFrame] = {}
    if telemetry_df is None or telemetry_df.empty:
        return resultado

    for columna, (min_val, max_val) in RANGOS_TELEMETRIA.items():
        if columna not in telemetry_df.columns:
            continue
        numerico = pd.to_numeric(telemetry_df[columna], errors="coerce")
        mask = numerico.notna() & ((numerico < min_val) | (numerico > max_val))
        anomalias = telemetry_df.loc[mask]
        if not anomalias.empty:
            resultado[columna] = anomalias
    return resultado
