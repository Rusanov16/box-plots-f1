"""Pruebas unitarias offline para indicadores, extractor, transformador y loader (Fase 3)."""

from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.domain.indicators import (
    calcular_degradacion_stints,
    calcular_efectividad_pit_stops,
    detectar_vuelta_rapida,
    etiquetar_anomalias_ritmo,
)
from src.etl import extractor, loader, openf1_service, transformer


def _sample_laps_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Driver": ["ver", "ver", "ver", "ver", "ver"],
            "Team": ["Red Bull"] * 5,
            "LapNumber": [1, 2, 3, 4, 5],
            "LapTime": [
                pd.Timedelta(seconds=90.0),
                pd.Timedelta(seconds=90.5),
                pd.Timedelta(seconds=91.0),
                pd.Timedelta(seconds=130.0),  # Safety Car / Pit (NO se debe borrar)
                pd.NaT,
            ],
            "Sector1Time": [pd.Timedelta(seconds=30)] * 4 + [pd.NaT],
            "Sector2Time": [pd.Timedelta(seconds=30)] * 4 + [pd.NaT],
            "Sector3Time": [pd.Timedelta(seconds=30)] * 4 + [pd.NaT],
            "Compound": ["SOFT", "SOFT", "SOFT", "UNKNOWN", "HARD"],
            "FreshTyre": [True, False, False, False, True],
            "TyreLife": [1, 2, 3, 4, 1],
            "Stint": [1, 1, 1, 1, 2],
            "PitInTime": [pd.NaT, pd.NaT, pd.NaT, pd.Timedelta(minutes=10), pd.NaT],
            "PitOutTime": [pd.NaT, pd.NaT, pd.NaT, pd.NaT, pd.Timedelta(minutes=10, seconds=24.5)],
        }
    )


def test_transformar_vueltas_no_destructivo_y_nat_a_none():
    laps = _sample_laps_df()
    df_norm, alertas = transformer.transformar_vueltas(laps)

    # Regla F3: nunca se eliminan filas (5 entran, 5 salen)
    assert len(df_norm) == 5
    assert df_norm["id_piloto"].iloc[0] == "VER"
    assert df_norm["nombre_equipo"].iloc[0] == "Red Bull Racing"
    assert df_norm["tiempo_lap"].iloc[0] == timedelta(seconds=90.0)
    assert df_norm["tiempo_lap"].iloc[4] is None
    assert bool(df_norm["vuelta_rapida"].iloc[0]) is True
    assert bool(df_norm["es_anomalia"].iloc[3]) is True
    assert bool(df_norm["es_anomalia"].iloc[4]) is True
    assert any(a["regla"] == "compuesto_no_estandar" for a in alertas)


def test_extraer_pit_stops_y_efectividad():
    laps = _sample_laps_df()
    pits = transformer.extraer_pit_stops(laps)
    assert len(pits) == 1
    assert pits["duracion_parada"].iloc[0] == 24.5
    assert pits["compuesto_entrante"].iloc[0] == "HARD"

    metrics = calcular_efectividad_pit_stops(pits)
    assert metrics["total_paradas"] == 1
    assert metrics["media_s"] == 24.5


def test_indicadores_degradacion_y_vuelta_rapida():
    laps = etiquetar_anomalias_ritmo(_sample_laps_df())
    vr = detectar_vuelta_rapida(laps)
    assert vr.sum() == 1

    deg = calcular_degradacion_stints(laps, excluir_anomalias=True)
    assert len(deg) == 1
    assert deg[0]["id_piloto"] == "ver"
    assert deg[0]["degradacion_s_por_vuelta"] == pytest.approx(0.5, abs=0.01)


def test_transformar_telemetria_genera_timestamp_valido():
    tel = pd.DataFrame(
        {
            "Time": [pd.Timedelta(seconds=1), pd.Timedelta(seconds=2)],
            "Speed": [310, 420],  # 420 fuera de rango -> alerta y None
            "RPM": [11500, 12000],
            "nGear": [8, 8],
            "Throttle": [100, 100],
            "Brake": [False, False],
            "DRS": [12, 0],
        }
    )
    fecha = datetime(2024, 3, 2, 15, 0, 0)
    tel_norm, alertas = transformer.transformar_telemetria(tel, fecha_sesion=fecha)

    assert len(tel_norm) == 2
    assert pd.api.types.is_datetime64_any_dtype(tel_norm["tiempo_registro"])
    assert tel_norm["velocidad"].iloc[0] == 310
    assert pd.isna(tel_norm["velocidad"].iloc[1])
    assert bool(tel_norm["drs_abierto"].iloc[0]) is True
    assert bool(tel_norm["drs_abierto"].iloc[1]) is False
    assert any("Speed" in a["regla"] for a in alertas)


def test_extractor_rechaza_anio_menor_2018_y_compara_ergast():
    with pytest.raises(ValueError):
        extractor.extraer_sesion_fastf1(2015, "Monza", "R")

    f1_res = pd.DataFrame({"Abbreviation": ["VER", "HAM"], "Position": [1, 2]})
    erg_res = pd.DataFrame({"driverCode": ["VER", "HAM"], "position": [1, 3]})
    disc = extractor.comparar_consistencia_fastf1_ergast(f1_res, erg_res)
    assert len(disc) == 1
    assert disc[0]["id_piloto"] == "HAM"


def test_loader_carga_ordenada_y_masiva(mocker):
    mock_conn = MagicMock()
    cur = mock_conn.cursor.return_value.__enter__.return_value
    cur.fetchone.return_value = (99,)  # id_sesion

    @contextmanager
    def fake_get_conn():
        yield mock_conn

    mocker.patch.object(loader, "get_conn", fake_get_conn)
    mocker.patch.object(
        loader,
        "upsert_dimensiones",
        return_value={
            "pilotos": {"VER": "VER"},
            "escuderias": {"Red Bull Racing": 1},
            "circuitos": {"Gulf Air Bahrain Grand Prix": 2},
            "neumaticos": {("SOFT", True): 3, ("SOFT", False): 4, ("HARD", True): 5},
        },
    )
    mock_part = mocker.patch.object(loader, "ensure_telemetry_partition", return_value="telemetria_2024")
    mock_exec_vals = mocker.patch.object(
        loader,
        "execute_values",
        side_effect=[
            [(101, "VER", 1), (102, "VER", 2), (103, "VER", 3), (104, "VER", 4), (105, "VER", 5)],
            None,
            None,
        ],
    )
    mock_aud = mocker.patch.object(loader, "registrar_auditoria_etl", return_value=777)

    tel_df = pd.DataFrame(
        {
            "Date": [datetime(2024, 3, 2, 15, 0, 1)],
            "Speed": [300],
            "RPM": [11000],
            "nGear": [7],
            "Throttle": [100],
            "Brake": [False],
            "DRS": [0],
        }
    )

    datos = {
        "metadata": {
            "anio": 2024,
            "ronda": 1,
            "nombre_evento": "Bahrain",
            "ubicacion": "Sakhir",
            "pais": "Bahrain",
            "cod_sesion": "R",
            "fecha_sesion": datetime(2024, 3, 2, 15, 0, 0),
        },
        "laps": _sample_laps_df(),
        "telemetry": [{"id_piloto": "VER", "numero_vuelta": 1, "telemetry": tel_df}],
    }

    res = loader.cargar_sesion_en_bd(datos, usuario="test_user")
    assert res["id_sesion"] == 99
    assert res["registros_vueltas"] == 5
    assert res["registros_telemetria"] == 1
    assert res["id_auditoria"] == 777
    mock_part.assert_called_once_with(mock_conn, 2024)
    assert mock_exec_vals.call_count == 3
    mock_aud.assert_called_once()


def test_extraer_sesion_openf1_offline(mocker):
    mocker.patch.object(
        openf1_service,
        "_get_json",
        side_effect=[
            [
                {
                    "session_key": 9158,
                    "meeting_key": 1229,
                    "year": 2024,
                    "country_name": "Bahrain",
                    "location": "Sakhir",
                    "session_name": "Race",
                    "date_start": "2024-03-02T15:00:00Z",
                }
            ],
            [{"driver_number": 1, "name_acronym": "VER", "team_name": "Red Bull Racing"}],
            [
                {
                    "driver_number": 1,
                    "lap_number": 1,
                    "lap_duration": 92.5,
                    "duration_sector_1": 30.1,
                    "duration_sector_2": 31.2,
                    "duration_sector_3": 31.2,
                    "is_pit_out_lap": False,
                }
            ],
            [
                {
                    "driver_number": 1,
                    "stint_number": 1,
                    "lap_start": 1,
                    "lap_end": 15,
                    "compound": "SOFT",
                    "tyre_age_at_start": 0,
                }
            ],
        ],
    )

    datos = openf1_service.extraer_sesion_openf1(9158)
    assert datos["metadata"]["anio"] == 2024
    assert datos["metadata"]["cod_sesion"] == "R"
    assert len(datos["laps"]) == 1
    assert datos["laps"]["Driver"].iloc[0] == "VER"
    assert datos["laps"]["Compound"].iloc[0] == "SOFT"
