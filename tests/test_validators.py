"""Pruebas unitarias para validadores de dominio y configuración (Fase 1)."""

import pandas as pd

from src.config import CACHE_DIR, DatabaseConfig, SQL_SCHEMA_PATH
from src.domain.catalogos import (
    normalizar_circuito,
    normalizar_codigo_piloto,
    normalizar_compuesto,
    normalizar_escuderia,
)
from src.domain.conceptos import buscar_concepto
from src.domain.validators import (
    validar_compuestos,
    validar_telemetria,
    validar_tiempo_vuelta,
    validar_vida_neumatico,
)


def test_config_paths_and_db_defaults():
    cfg = DatabaseConfig.from_env()
    assert isinstance(cfg.port, int)
    assert SQL_SCHEMA_PATH.name == "fastf1-suef1.sql"
    assert SQL_SCHEMA_PATH.exists()
    assert CACHE_DIR.name == "fastf1_cache"


def test_catalogos_y_conceptos():
    assert normalizar_codigo_piloto(" ver ") == "VER"
    assert normalizar_escuderia("Red Bull") == "Red Bull Racing"
    assert normalizar_circuito("monza") == "Pirelli Italian Grand Prix"
    assert normalizar_compuesto(" soft ") == "SOFT"
    assert buscar_concepto("Fastest lap") is not None


def test_validar_tiempo_vuelta_con_nat_y_negativos():
    df = pd.DataFrame(
        {
            "LapTime": [
                pd.Timedelta(seconds=90),
                pd.Timedelta(seconds=0),
                pd.Timedelta(seconds=-5),
                pd.NaT,
            ]
        }
    )
    anomalias = validar_tiempo_vuelta(df)
    assert len(anomalias) == 2


def test_validar_compuestos_y_vida_neumatico():
    df = pd.DataFrame(
        {
            "Compound": ["SOFT", "UNKNOWN", None, "hard"],
            "TyreLife": [10, -1, 150, None],
        }
    )
    assert len(validar_compuestos(df)) == 1
    assert len(validar_vida_neumatico(df)) == 2


def test_validar_telemetria_rangos():
    tel = pd.DataFrame(
        {
            "Speed": [320.0, -5.0, 450.0, None],
            "RPM": [12000, 25000, 10500, None],
            "nGear": [8, 9, 0, None],
            "Throttle": [100.0, 105.0, 0.0, None],
        }
    )
    res = validar_telemetria(tel)
    assert len(res["Speed"]) == 2
    assert len(res["RPM"]) == 1
    assert len(res["nGear"]) == 1
    assert len(res["Throttle"]) == 1
