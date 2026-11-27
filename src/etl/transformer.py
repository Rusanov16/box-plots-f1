"""Transformación y normalización no destructiva de datos FastF1 (F1 / F2 / F3).

Reglas clave:
- Convierte `pd.Timedelta` a `datetime.timedelta` y `pd.NaT` a `None`.
- Nunca elimina vueltas lentas (Safety Car, lluvia, pit stops); las etiqueta.
- Garantiza `TIMESTAMP` válido en `telemetria.tiempo_registro` (nunca `Timedelta`).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from src.domain.catalogos import (
    normalizar_codigo_piloto,
    normalizar_compuesto,
    normalizar_escuderia,
)
from src.domain.indicators import detectar_vuelta_rapida, etiquetar_anomalias_ritmo
from src.domain.validators import (
    COMPUESTOS_ESTANDAR,
    validar_compuestos,
    validar_telemetria,
    validar_tiempo_vuelta,
    validar_vida_neumatico,
)


def timedelta_a_interval(valor: Any) -> Optional[timedelta]:
    """Convierte `pd.Timedelta` / `timedelta` a `datetime.timedelta` nativo, o `None` si `NaT`."""
    if valor is None or pd.isna(valor):
        return None
    if isinstance(valor, pd.Timedelta):
        td = valor.to_pytimedelta()
    elif isinstance(valor, timedelta):
        td = valor
    else:
        return None
    return td if td.total_seconds() > 0 else None


def transformar_vueltas(laps_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """Normaliza vueltas de FastF1 preservando todos los registros y generando alertas F3."""
    alertas: List[Dict[str, Any]] = []
    if laps_df is None or laps_df.empty:
        return pd.DataFrame(), alertas

    df = laps_df.copy()

    # Validaciones F3 no destructivas
    mal_tiempo = validar_tiempo_vuelta(df)
    if not mal_tiempo.empty:
        alertas.append({"regla": "tiempo_vuelta_no_positivo", "cantidad": int(len(mal_tiempo))})

    mal_compuesto = validar_compuestos(df)
    if not mal_compuesto.empty:
        alertas.append({"regla": "compuesto_no_estandar", "cantidad": int(len(mal_compuesto))})

    mal_vida = validar_vida_neumatico(df)
    if not mal_vida.empty:
        alertas.append({"regla": "vida_neumatico_fuera_rango", "cantidad": int(len(mal_vida))})

    # Etiquetado de anomalías de ritmo (IQR / Z-score) y vuelta rápida
    df = etiquetar_anomalias_ritmo(df)
    df["vuelta_rapida"] = detectar_vuelta_rapida(df)

    # Normalización de campos
    df["id_piloto"] = df["Driver"].apply(normalizar_codigo_piloto)
    df["nombre_equipo"] = (
        df["Team"].apply(normalizar_escuderia) if "Team" in df.columns else "Desconocido"
    )
    df["numero_vuelta"] = pd.to_numeric(df["LapNumber"], errors="coerce").fillna(0).astype(int)

    for col_orig, col_dest in (
        ("LapTime", "tiempo_lap"),
        ("Sector1Time", "sector_1"),
        ("Sector2Time", "sector_2"),
        ("Sector3Time", "sector_3"),
    ):
        if col_orig in df.columns:
            df[col_dest] = pd.Series(
                [timedelta_a_interval(v) for v in df[col_orig]],
                index=df.index,
                dtype=object,
            )
        else:
            df[col_dest] = None

    if "Compound" in df.columns:
        df["compuesto"] = df["Compound"].apply(
            lambda c: normalizar_compuesto(c) if pd.notna(c) and normalizar_compuesto(c) in COMPUESTOS_ESTANDAR else None
        )
    else:
        df["compuesto"] = None

    if "FreshTyre" in df.columns:
        df["neumaticos_nuevos"] = df["FreshTyre"].fillna(True).astype(bool)
    else:
        df["neumaticos_nuevos"] = True

    if "TyreLife" in df.columns:
        vida = pd.to_numeric(df["TyreLife"], errors="coerce")
        df["vida_neumatico"] = vida.apply(lambda v: int(v) if pd.notna(v) and v >= 0 else None)
    else:
        df["vida_neumatico"] = None

    return df, alertas


def extraer_pit_stops(laps_df: pd.DataFrame) -> pd.DataFrame:
    """Extrae registros de paradas en boxes (`pit_stops`) a partir de `PitInTime`/`PitOutTime`."""
    if laps_df is None or laps_df.empty or "PitInTime" not in laps_df.columns:
        return pd.DataFrame()

    registros: List[Dict[str, Any]] = []
    df = laps_df.sort_values(["Driver", "LapNumber"]).reset_index(drop=True)

    for piloto, grupo in df.groupby("Driver"):
        grupo = grupo.reset_index(drop=True)
        for idx, row in grupo.iterrows():
            if pd.isna(row.get("PitInTime")):
                continue
            duracion: Optional[float] = None
            comp_entrante = None
            nuevo_entrante = True

            if idx + 1 < len(grupo):
                siguiente = grupo.iloc[idx + 1]
                if pd.notna(siguiente.get("PitOutTime")) and pd.notna(row.get("PitInTime")):
                    delta = siguiente["PitOutTime"] - row["PitInTime"]
                    if isinstance(delta, (pd.Timedelta, timedelta)):
                        secs = delta.total_seconds()
                        if secs > 0:
                            duracion = round(float(secs), 3)
                if pd.notna(siguiente.get("Compound")):
                    comp = normalizar_compuesto(siguiente["Compound"])
                    if comp in COMPUESTOS_ESTANDAR:
                        comp_entrante = comp
                if "FreshTyre" in siguiente and pd.notna(siguiente.get("FreshTyre")):
                    nuevo_entrante = bool(siguiente["FreshTyre"])

            comp_saliente = None
            if pd.notna(row.get("Compound")):
                comp = normalizar_compuesto(row["Compound"])
                if comp in COMPUESTOS_ESTANDAR:
                    comp_saliente = comp

            vida_saliente = None
            if pd.notna(row.get("TyreLife")):
                val = int(float(row["TyreLife"]))
                if val >= 0:
                    vida_saliente = val

            registros.append(
                {
                    "id_piloto": normalizar_codigo_piloto(piloto),
                    "nombre_equipo": normalizar_escuderia(row["Team"]) if "Team" in row else "Desconocido",
                    "numero_vuelta": int(row["LapNumber"]),
                    "stint": int(row["Stint"]) if "Stint" in row and pd.notna(row.get("Stint")) else None,
                    "duracion_parada": duracion,
                    "compuesto_saliente": comp_saliente,
                    "nuevo_saliente": bool(row.get("FreshTyre", True)) if pd.notna(row.get("FreshTyre", True)) else True,
                    "compuesto_entrante": comp_entrante,
                    "nuevo_entrante": nuevo_entrante,
                    "vida_neumatico_saliente": vida_saliente,
                }
            )
    return pd.DataFrame(registros)


def transformar_telemetria(
    telemetry_df: pd.DataFrame,
    fecha_sesion: Optional[datetime] = None,
) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """Normaliza telemetría asegurando `tiempo_registro` como `TIMESTAMP` válido."""
    alertas: List[Dict[str, Any]] = []
    if telemetry_df is None or telemetry_df.empty:
        return pd.DataFrame(), alertas

    df = telemetry_df.copy()

    # Validación física F3
    anomalias_tel = validar_telemetria(df)
    for col, anom_df in anomalias_tel.items():
        alertas.append({"regla": f"telemetria_fuera_rango_{col}", "cantidad": int(len(anom_df))})

    # Construcción de TIMESTAMP real (nunca Timedelta crudo)
    if "Date" in df.columns and df["Date"].notna().any():
        tiempos = pd.to_datetime(df["Date"], errors="coerce")
    elif "Time" in df.columns and fecha_sesion is not None:
        base_ts = pd.Timestamp(fecha_sesion)
        tiempos = base_ts + pd.to_timedelta(df["Time"], errors="coerce")
    else:
        raise ValueError(
            "La telemetría requiere columna `Date` o (`Time` + `fecha_sesion`) "
            "para generar un TIMESTAMP válido."
        )

    df["tiempo_registro"] = tiempos
    df = df[df["tiempo_registro"].notna()].copy()

    def _int_en_rango(serie: pd.Series, lo: int, hi: int) -> pd.Series:
        num = pd.to_numeric(serie, errors="coerce")
        return num.apply(lambda v: int(round(v)) if pd.notna(v) and lo <= v <= hi else None)

    df["velocidad"] = _int_en_rango(df["Speed"], 0, 400) if "Speed" in df.columns else None
    df["rpm"] = _int_en_rango(df["RPM"], 0, 20000) if "RPM" in df.columns else None
    df["marcha"] = _int_en_rango(df["nGear"], 0, 8) if "nGear" in df.columns else None
    df["throttle"] = _int_en_rango(df["Throttle"], 0, 100) if "Throttle" in df.columns else None
    df["brake"] = df["Brake"].astype(bool) if "Brake" in df.columns else None
    df["drs_abierto"] = (
        (pd.to_numeric(df["DRS"], errors="coerce").fillna(0) >= 10)
        if "DRS" in df.columns
        else None
    )

    return df[["tiempo_registro", "velocidad", "rpm", "marcha", "throttle", "brake", "drs_abierto"]], alertas
