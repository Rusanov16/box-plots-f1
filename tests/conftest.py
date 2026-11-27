"""Fixtures compartidos offline para la suite de pruebas SIE-F1."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest


@pytest.fixture
def sample_laps_df() -> pd.DataFrame:
    """DataFrame simulado de vueltas FastF1 con vuelta lenta, pit stop y NaT."""
    return pd.DataFrame(
        {
            "Driver": ["ver", "ver", "ver", "ver", "ver"],
            "Team": ["Red Bull"] * 5,
            "LapNumber": [1, 2, 3, 4, 5],
            "LapTime": [
                pd.Timedelta(seconds=90.0),
                pd.Timedelta(seconds=90.5),
                pd.Timedelta(seconds=91.0),
                pd.Timedelta(seconds=135.0),
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


@pytest.fixture
def sample_telemetry_df() -> pd.DataFrame:
    """DataFrame simulado de telemetría FastF1."""
    return pd.DataFrame(
        {
            "Date": [datetime(2024, 3, 2, 15, 0, 1), datetime(2024, 3, 2, 15, 0, 2)],
            "Speed": [310, 325],
            "RPM": [11500, 11800],
            "nGear": [8, 8],
            "Throttle": [100, 100],
            "Brake": [False, False],
            "DRS": [12, 0],
        }
    )
