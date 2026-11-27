"""Extractor público de sesiones, vueltas y stints desde OpenF1 API (2023–actualidad).

No requiere inicio de sesión ni credenciales y produce exactamente el mismo
formato de salida que `extraer_sesion_fastf1` para integrarse sin fricción con
`transformar_vueltas` y `cargar_sesion_en_bd`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

OPENF1_BASE_URL = "https://api.openf1.org/v1"

_MAPA_COD_SESION = {
    "Practice 1": "FP1",
    "Practice 2": "FP2",
    "Practice 3": "FP3",
    "Qualifying": "Q",
    "Sprint": "S",
    "Sprint Qualifying": "SQ",
    "Sprint Shootout": "SS",
    "Race": "R",
}


def _crear_sesion_http() -> requests.Session:
    """Sesión HTTP reutilizable (keep-alive) con reintentos ante 429/5xx."""
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    sesion = requests.Session()
    reintentos = Retry(
        total=3,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adaptador = HTTPAdapter(max_retries=reintentos, pool_connections=8, pool_maxsize=8)
    sesion.mount("https://", adaptador)
    sesion.headers.update({"User-Agent": "BoxPlotsF1/1.0", "Accept": "application/json"})
    return sesion


_HTTP = _crear_sesion_http()


def _get_json(endpoint: str, params: Dict[str, Any], timeout: int = 20) -> List[Dict[str, Any]]:
    resp = _HTTP.get(f"{OPENF1_BASE_URL}/{endpoint}", params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else []


def listar_sesiones_openf1(anio: int) -> List[Dict[str, Any]]:
    """Lista las sesiones disponibles en OpenF1 para una temporada (2023+)."""
    if anio < 2023:
        return []
    sesiones = _get_json("sessions", {"year": int(anio)})
    return sorted(sesiones, key=lambda s: str(s.get("date_start", "")))


def _segundos_a_timedelta(val: Any) -> Any:
    if val is None or pd.isna(val):
        return pd.NaT
    try:
        secs = float(val)
        return pd.Timedelta(seconds=secs) if secs > 0 else pd.NaT
    except Exception:
        return pd.NaT


def _buscar_stint(
    stints_piloto: List[Dict[str, Any]], lap_number: int
) -> Dict[str, Any]:
    for s in stints_piloto:
        ini = s.get("lap_start")
        fin = s.get("lap_end")
        if ini is not None and fin is not None and ini <= lap_number <= fin:
            return s
    return {}


def extraer_sesion_openf1(session_key: int) -> Dict[str, Any]:
    """Extrae metadatos, vueltas y stints de una sesión OpenF1 en formato estándar SIE-F1."""
    sesiones = _get_json("sessions", {"session_key": int(session_key)})
    if not sesiones:
        raise ValueError(f"No se encontró la sesión OpenF1 con session_key={session_key}")
    s_info = sesiones[0]

    # Descarga en paralelo de pilotos, vueltas y stints (reduce latencia ~3x).
    from concurrent.futures import ThreadPoolExecutor

    params = {"session_key": int(session_key)}
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_drivers = pool.submit(_get_json, "drivers", params)
        f_laps = pool.submit(_get_json, "laps", params)
        f_stints = pool.submit(_get_json, "stints", params)
        drivers, laps_raw, stints_raw = f_drivers.result(), f_laps.result(), f_stints.result()

    mapa_pilotos: Dict[int, Dict[str, str]] = {}
    for d in drivers:
        num = d.get("driver_number")
        if num is None:
            continue
        mapa_pilotos[int(num)] = {
            "Driver": str(d.get("name_acronym") or num).upper(),
            "Team": str(d.get("team_name") or "Desconocido"),
        }

    stints_por_piloto: Dict[int, List[Dict[str, Any]]] = {}
    for st in stints_raw:
        num = st.get("driver_number")
        if num is not None:
            stints_por_piloto.setdefault(int(num), []).append(st)

    filas: List[Dict[str, Any]] = []
    for lap in laps_raw:
        num = lap.get("driver_number")
        lap_num = lap.get("lap_number")
        if num is None or lap_num is None:
            continue
        num_int = int(num)
        lap_int = int(lap_num)
        info_p = mapa_pilotos.get(num_int, {"Driver": str(num_int), "Team": "Desconocido"})
        stint_info = _buscar_stint(stints_por_piloto.get(num_int, []), lap_int)

        lap_start = stint_info.get("lap_start")
        age_start = stint_info.get("tyre_age_at_start") or 0
        tyre_life = (
            int(age_start) + (lap_int - int(lap_start)) + 1
            if lap_start is not None
            else None
        )

        filas.append(
            {
                "Driver": info_p["Driver"],
                "DriverNumber": num_int,
                "Team": info_p["Team"],
                "LapNumber": lap_int,
                "LapStartDate": lap.get("date_start"),
                "LapTime": _segundos_a_timedelta(lap.get("lap_duration")),
                "Sector1Time": _segundos_a_timedelta(lap.get("duration_sector_1")),
                "Sector2Time": _segundos_a_timedelta(lap.get("duration_sector_2")),
                "Sector3Time": _segundos_a_timedelta(lap.get("duration_sector_3")),
                "Compound": stint_info.get("compound"),
                "FreshTyre": bool(age_start == 0) if stint_info else True,
                "TyreLife": tyre_life,
                "Stint": stint_info.get("stint_number"),
                "PitInTime": pd.NaT,
                "PitOutTime": pd.Timedelta(seconds=1) if lap.get("is_pit_out_lap") else pd.NaT,
            }
        )

    laps_df = pd.DataFrame(filas)

    fecha_raw = s_info.get("date_start")
    fecha_sesion: Optional[datetime] = None
    if fecha_raw:
        try:
            fecha_sesion = datetime.fromisoformat(str(fecha_raw).replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            fecha_sesion = None

    nombre_sesion = str(s_info.get("session_name") or "Race")
    cod_sesion = _MAPA_COD_SESION.get(nombre_sesion, nombre_sesion[:3].upper())

    metadata = {
        "session_key": int(session_key),
        "anio": int(s_info.get("year") or (fecha_sesion.year if fecha_sesion else 2024)),
        "ronda": int(s_info.get("meeting_key") or 0) % 1000,
        "nombre_evento": str(s_info.get("country_name") or s_info.get("location") or "Grand Prix"),
        "ubicacion": str(s_info.get("location") or "") or None,
        "pais": str(s_info.get("country_name") or "") or None,
        "cod_sesion": cod_sesion,
        "fecha_sesion": fecha_sesion,
    }

    return {
        "metadata": metadata,
        "laps": laps_df,
        "results": pd.DataFrame(),
        "telemetry": [],
    }


def extraer_mapa_calor_openf1(
    session_key: int,
    driver_number: int,
    lap_start_iso: str,
    lap_duration_s: float,
) -> pd.DataFrame:
    """Descarga coordenadas `(x, y)` y telemetría (`speed`, `throttle`, `n_gear`) de una vuelta en OpenF1."""
    inicio = pd.Timestamp(lap_start_iso)
    if inicio.tzinfo is not None:
        inicio = inicio.tz_convert("UTC").tz_localize(None)
    fin = inicio + pd.Timedelta(seconds=float(lap_duration_s) + 1.0)
    ini_str = inicio.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    fin_str = fin.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    url_loc = (
        f"{OPENF1_BASE_URL}/location?session_key={int(session_key)}"
        f"&driver_number={int(driver_number)}&date>={ini_str}&date<={fin_str}"
    )
    url_car = (
        f"{OPENF1_BASE_URL}/car_data?session_key={int(session_key)}"
        f"&driver_number={int(driver_number)}&date>={ini_str}&date<={fin_str}"
    )
    r_loc = requests.get(url_loc, timeout=20)
    if r_loc.status_code == 404:
        return pd.DataFrame()
    r_loc.raise_for_status()
    r_car = requests.get(url_car, timeout=20)
    if r_car.status_code == 404:
        return pd.DataFrame()
    r_car.raise_for_status()

    loc_df = pd.DataFrame(r_loc.json())
    car_df = pd.DataFrame(r_car.json())
    if loc_df.empty or car_df.empty:
        return pd.DataFrame()

    loc_df["date"] = pd.to_datetime(loc_df["date"], errors="coerce")
    car_df["date"] = pd.to_datetime(car_df["date"], errors="coerce")
    loc_df = loc_df.dropna(subset=["date", "x", "y"]).sort_values("date")
    car_df = car_df.dropna(subset=["date"]).sort_values("date")

    merged = pd.merge_asof(
        loc_df[["date", "x", "y"]],
        car_df[["date", "speed", "throttle", "brake", "n_gear", "rpm"]],
        on="date",
        direction="nearest",
    )
    return merged.dropna(subset=["x", "y", "speed"]).reset_index(drop=True)
