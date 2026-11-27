"""Pruebas smoke offline de arranque de Streamlit y reglas invariables de arquitectura."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
APP_ROOT = ROOT / "app"
SRC_ROOT = ROOT / "src"

PAGINAS = [
    APP_ROOT / "app.py",
    APP_ROOT / "inicio.py",
    APP_ROOT / "pages" / "05_Mundiales_GP.py",
    APP_ROOT / "pages" / "06_Duelos_y_Fiabilidad.py",
    APP_ROOT / "pages" / "08_Mapa_y_Salon_Fama.py",
    APP_ROOT / "pages" / "09_Glosario_y_Reglamento_2026.py",
]


@pytest.mark.parametrize("ruta", PAGINAS, ids=[p.name for p in PAGINAS])
def test_pagina_streamlit_arranca_sin_excepciones(ruta: Path):
    assert ruta.exists(), f"No existe la página: {ruta}"
    at = AppTest.from_file(str(ruta), default_timeout=15)
    at.run()
    assert not at.exception, f"Excepción al renderizar {ruta.name}: {at.exception}"


def test_reglas_invariables_sin_codigo_deprecado_ni_sql_en_app():
    """Verifica ausencia de `pick_driver(`, `core.queries` y SQL crudo en `app/`."""
    for py_file in list(APP_ROOT.rglob("*.py")) + list(SRC_ROOT.rglob("*.py")):
        texto = py_file.read_text(encoding="utf-8")
        assert ".pick_driver(" not in texto, f"Uso deprecado de .pick_driver() en {py_file}"
        assert "core.queries" not in texto, f"Import roto core.queries en {py_file}"

    for py_file in APP_ROOT.rglob("*.py"):
        texto = py_file.read_text(encoding="utf-8").upper()
        assert "SELECT " not in texto, f"SQL crudo prohibido en capa UI: {py_file}"
        assert "INSERT INTO " not in texto, f"SQL crudo prohibido en capa UI: {py_file}"
