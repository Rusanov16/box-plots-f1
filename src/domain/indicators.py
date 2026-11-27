"""Indicadores derivados y detección estadística de anomalías (F3 / F4 — SIE-F1).

Calcula de forma no destructiva:
- Vuelta rápida por sesión y por piloto.
- Detección de stints y degradación de neumáticos (pendiente lineal s/vuelta).
- Efectividad de pit stops.
- Etiquetado de anomalías de ritmo (IQR y Z-score) sin eliminar registros.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


def _laptime_a_segundos(serie: pd.Series) -> pd.Series:
    """Convierte una serie de `LapTime` (Timedelta o numérico) a segundos float."""
    if pd.api.types.is_timedelta64_dtype(serie):
        return serie.dt.total_seconds()
    return pd.to_numeric(serie, errors="coerce")


def detectar_vuelta_rapida(laps_df: pd.DataFrame) -> pd.Series:
    """Retorna una serie booleana marcando la vuelta más rápida válida (`> 0`)."""
    flags = pd.Series(False, index=laps_df.index, dtype=bool)
    if laps_df is None or laps_df.empty or "LapTime" not in laps_df.columns:
        return flags

    segundos = _laptime_a_segundos(laps_df["LapTime"])
    validas = segundos[segundos.notna() & (segundos > 0)]
    if validas.empty:
        return flags

    idx_min = validas.idxmin()
    flags.loc[idx_min] = True
    return flags


def etiquetar_anomalias_ritmo(
    laps_df: pd.DataFrame,
    z_umbral: float = 3.0,
    iqr_factor: float = 1.5,
) -> pd.DataFrame:
    """Etiqueta vueltas con anomalías de ritmo (IQR / Z-score) SIN eliminar filas.

    Agrega o actualiza `es_anomalia` (bool) y `motivo_anomalia` (str | None).
    """
    df = laps_df.copy()
    if "es_anomalia" not in df.columns:
        df["es_anomalia"] = False
    if "motivo_anomalia" not in df.columns:
        df["motivo_anomalia"] = None

    if df.empty or "LapTime" not in df.columns:
        return df

    segundos = _laptime_a_segundos(df["LapTime"])

    # 1. Tiempos nulos o no positivos
    mask_invalido = segundos.isna() | (segundos <= 0)
    df.loc[mask_invalido, "es_anomalia"] = True
    df.loc[mask_invalido & df["motivo_anomalia"].isna(), "motivo_anomalia"] = "tiempo_nulo_o_no_positivo"

    # 2. Pit in / Pit out si existen columnas
    if "PitInTime" in df.columns:
        mask_pit_in = df["PitInTime"].notna()
        df.loc[mask_pit_in, "es_anomalia"] = True
        df.loc[mask_pit_in & df["motivo_anomalia"].isna(), "motivo_anomalia"] = "pit_in_lap"
    if "PitOutTime" in df.columns:
        mask_pit_out = df["PitOutTime"].notna()
        df.loc[mask_pit_out, "es_anomalia"] = True
        df.loc[mask_pit_out & df["motivo_anomalia"].isna(), "motivo_anomalia"] = "pit_out_lap"

    # 3. Outliers estadísticos (IQR + Z-score) sobre tiempos válidos
    validos = segundos[segundos.notna() & (segundos > 0)]
    if len(validos) >= 4:
        q1 = validos.quantile(0.25)
        q3 = validos.quantile(0.75)
        iqr = q3 - q1
        limite_sup_iqr = q3 + iqr_factor * iqr

        media = validos.mean()
        std = validos.std(ddof=0)

        mask_iqr = segundos.notna() & (segundos > limite_sup_iqr)
        if std and std > 0:
            z_scores = (segundos - media).abs() / std
            mask_z = segundos.notna() & (z_scores > z_umbral)
        else:
            mask_z = pd.Series(False, index=df.index)

        mask_outlier = mask_iqr | mask_z
        df.loc[mask_outlier, "es_anomalia"] = True
        df.loc[mask_outlier & df["motivo_anomalia"].isna(), "motivo_anomalia"] = "ritmo_anomalo_iqr_zscore"

    return df


def calcular_degradacion_stints(
    laps_df: pd.DataFrame, excluir_anomalias: bool = True
) -> List[Dict[str, Any]]:
    """Calcula la degradación (pendiente lineal en s/vuelta) por piloto y stint."""
    if laps_df is None or laps_df.empty or "LapTime" not in laps_df.columns:
        return []

    df = laps_df.copy()
    df["_sec"] = _laptime_a_segundos(df["LapTime"])
    df = df[df["_sec"].notna() & (df["_sec"] > 0)]

    if excluir_anomalias and "es_anomalia" in df.columns:
        df = df[~df["es_anomalia"].astype(bool)]

    if df.empty:
        return []

    driver_col = "Driver" if "Driver" in df.columns else "id_piloto"
    stint_col = "Stint" if "Stint" in df.columns else "stint"
    comp_col = "Compound" if "Compound" in df.columns else "compuesto"
    life_col = "TyreLife" if "TyreLife" in df.columns else "vida_neumatico"

    if driver_col not in df.columns:
        df[driver_col] = "UNK"
    if stint_col not in df.columns:
        df[stint_col] = 1

    resultados: List[Dict[str, Any]] = []
    for (piloto, stint), grupo in df.groupby([driver_col, stint_col]):
        if len(grupo) < 2:
            continue
        if life_col in grupo.columns and grupo[life_col].notna().all():
            x = pd.to_numeric(grupo[life_col], errors="coerce").to_numpy(dtype=float)
        else:
            x = np.arange(1, len(grupo) + 1, dtype=float)
        y = grupo["_sec"].to_numpy(dtype=float)

        if np.std(x) == 0:
            pendiente = 0.0
        else:
            pendiente = float(np.polyfit(x, y, 1)[0])

        compuesto = (
            str(grupo[comp_col].iloc[0]) if comp_col in grupo.columns and not grupo[comp_col].isna().all() else None
        )
        resultados.append(
            {
                "id_piloto": str(piloto),
                "stint": int(stint),
                "compuesto": compuesto,
                "vueltas_analizadas": int(len(grupo)),
                "degradacion_s_por_vuelta": round(pendiente, 4),
                "ritmo_medio_s": round(float(np.mean(y)), 3),
            }
        )
    return resultados


def calcular_efectividad_pit_stops(pit_stops_df: pd.DataFrame) -> Dict[str, Optional[float]]:
    """Calcula métricas resumen de duración de pit stops (media, mediana, mínimo)."""
    if pit_stops_df is None or pit_stops_df.empty or "duracion_parada" not in pit_stops_df.columns:
        return {"total_paradas": 0, "media_s": None, "mediana_s": None, "min_s": None}

    validos = pd.to_numeric(pit_stops_df["duracion_parada"], errors="coerce").dropna()
    validos = validos[validos > 0]
    if validos.empty:
        return {"total_paradas": 0, "media_s": None, "mediana_s": None, "min_s": None}

    return {
        "total_paradas": int(len(validos)),
        "media_s": round(float(validos.mean()), 3),
        "mediana_s": round(float(validos.median()), 3),
        "min_s": round(float(validos.min()), 3),
    }


def estimar_ventana_undercut(
    degradacion: List[Dict[str, Any]],
    tiempo_pit_lane_s: float = 22.0,
) -> List[Dict[str, Any]]:
    """Estima cuántas vueltas tarda un neumático nuevo en compensar el pit stop por compuesto."""
    if not degradacion:
        return []
    df = pd.DataFrame(degradacion)
    if "compuesto" not in df.columns or "degradacion_s_por_vuelta" not in df.columns:
        return []

    resumen = []
    for comp, grupo in df.dropna(subset=["compuesto"]).groupby("compuesto"):
        deg_media = float(grupo["degradacion_s_por_vuelta"].mean())
        # Si la degradación es positiva (neumático pierde tiempo cada vuelta),
        # el undercut compensa el pit cuando deg * N * (N+1) / 2 >= tiempo_pit_lane_s
        if deg_media > 0.01:
            vueltas_comp = int(np.ceil((-1.0 + np.sqrt(1.0 + 8.0 * tiempo_pit_lane_s / deg_media)) / 2.0))
        else:
            vueltas_comp = None
        resumen.append(
            {
                "Compuesto": str(comp),
                "Degradación Media (s/vuelta)": round(deg_media, 4),
                "Ritmo Medio (s)": round(float(grupo["ritmo_medio_s"].mean()), 3),
                "Vueltas para compensar Pit (~22s)": vueltas_comp if vueltas_comp is not None else "Sin caída positiva",
            }
        )
    return resumen
