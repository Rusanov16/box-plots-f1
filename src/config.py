"""Configuración centralizada del proyecto SIE-F1.

Carga variables de entorno desde `.env` (vía `python-dotenv`) y, si está
disponible, desde `st.secrets` de Streamlit, sin credenciales hardcodeadas.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"


def _get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Obtiene un valor desde variables de entorno o `st.secrets`."""
    env_val = os.getenv(key)
    if env_val is not None and env_val != "":
        return env_val

    try:
        import streamlit as st  # type: ignore

        if key in st.secrets:
            val = st.secrets[key]
            return str(val) if val is not None else default
    except Exception:
        pass

    return default


def _resolve_cache_dir() -> Path:
    raw = _get_secret("FASTF1_CACHE_DIR")
    if raw:
        path = Path(raw)
        if not path.is_absolute():
            path = BASE_DIR / path
        return path
    return DATA_DIR / "fastf1_cache"


CACHE_DIR: Path = _resolve_cache_dir()
SQL_SCHEMA_PATH: Path = BASE_DIR / "sql" / "fastf1-suef1.sql"


def ensure_runtime_dirs() -> None:
    """Garantiza que existan los directorios locales de caché y logs."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class DatabaseConfig:
    """Parámetros de conexión a PostgreSQL 16."""

    host: str
    port: int
    dbname: str
    user: str
    password: str
    database_url: Optional[str] = None

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Construye la configuración leyendo entorno y/o `st.secrets`."""
        port_raw = _get_secret("DB_PORT", "5432") or "5432"
        return cls(
            host=_get_secret("DB_HOST", "localhost") or "localhost",
            port=int(port_raw),
            dbname=_get_secret("DB_NAME", "sie_f1") or "sie_f1",
            user=_get_secret("DB_USER", "postgres") or "postgres",
            password=_get_secret("DB_PASSWORD", "") or "",
            database_url=_get_secret("DATABASE_URL"),
        )


def get_admin_key() -> Optional[str]:
    """Devuelve la clave administrativa configurada (sin valor por defecto)."""
    return _get_secret("SIE_F1_ADMIN_KEY")
