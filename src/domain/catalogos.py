"""Catálogos y funciones de normalización estadística de Fórmula 1 (Función F2).

Contiene los códigos estándar oficiales (pilotos, escuderías, circuitos,
neumáticos y sesiones) y utilidades de normalización para el ETL y la UI.
"""

from __future__ import annotations

from typing import Dict

DRIVER_CODES: Dict[str, str] = {
    "HAM": "Lewis Hamilton",
    "RUS": "George Russell",
    "VER": "Max Verstappen",
    "PER": "Sergio Pérez",
    "LEC": "Charles Leclerc",
    "SAI": "Carlos Sainz",
    "NOR": "Lando Norris",
    "PIA": "Oscar Piastri",
    "ALO": "Fernando Alonso",
    "STR": "Lance Stroll",
    "GAS": "Pierre Gasly",
    "OCO": "Esteban Ocon",
    "ALB": "Alexander Albon",
    "SAR": "Logan Sargeant",
    "TSU": "Yuki Tsunoda",
    "RIC": "Daniel Ricciardo",
    "BOT": "Valtteri Bottas",
    "ZHO": "Guanyu Zhou",
    "HUL": "Nico Hülkenberg",
    "MAG": "Kevin Magnussen",
}

TEAM_CODES: Dict[str, str] = {
    "Red Bull": "Red Bull Racing",
    "Mercedes": "Mercedes-AMG Petronas",
    "Ferrari": "Scuderia Ferrari",
    "McLaren": "McLaren Formula 1 Team",
    "Aston Martin": "Aston Martin Aramco",
    "Alpine": "Alpine F1 Team",
    "Williams": "Williams Racing",
    "RB": "Visa Cash App RB",
    "Kick Sauber": "Stake F1 Team Kick Sauber",
    "Haas": "Haas F1 Team",
    "AlphaTauri": "Scuderia AlphaTauri",
    "Alfa Romeo": "Alfa Romeo F1 Team",
}

CIRCUIT_CODES: Dict[str, str] = {
    "Bahrain": "Gulf Air Bahrain Grand Prix",
    "Jeddah": "STC Saudi Arabian Grand Prix",
    "Melbourne": "Rolex Australian Grand Prix",
    "Suzuka": "MSC Cruises Japanese Grand Prix",
    "Shanghai": "Chinese Grand Prix",
    "Miami": "Crypto.com Miami Grand Prix",
    "Imola": "Emilia Romagna Grand Prix",
    "Monaco": "Grand Prix de Monaco",
    "Montreal": "Canadian Grand Prix",
    "Barcelona": "Spanish Grand Prix",
    "Spielberg": "Austrian Grand Prix",
    "Silverstone": "British Grand Prix",
    "Budapest": "Hungarian Grand Prix",
    "Spa": "Belgian Grand Prix",
    "Zandvoort": "Dutch Grand Prix",
    "Monza": "Pirelli Italian Grand Prix",
    "Baku": "Azerbaijan Grand Prix",
    "Singapore": "Singapore Grand Prix",
    "Austin": "United States Grand Prix",
    "Mexico": "Mexico City Grand Prix",
    "Interlagos": "São Paulo Grand Prix",
    "Las Vegas": "Las Vegas Grand Prix",
    "Losail": "Qatar Grand Prix",
    "Yas Marina": "Abu Dhabi Grand Prix",
    "Portimao": "Portuguese Grand Prix",
    "Istanbul": "Turkish Grand Prix",
    "Nürburgring": "Eifel Grand Prix",
}

TYRE_COMPOUNDS: Dict[str, str] = {
    "SOFT": "Blando",
    "MEDIUM": "Medio",
    "HARD": "Duro",
    "INTERMEDIATE": "Intermedio",
    "WET": "Lluvia extremo",
}

SESSION_CODES: Dict[str, str] = {
    "FP1": "Práctica Libre 1",
    "FP2": "Práctica Libre 2",
    "FP3": "Práctica Libre 3",
    "Q": "Clasificación",
    "Q1": "Clasificación - Q1",
    "Q2": "Clasificación - Q2",
    "Q3": "Clasificación - Q3",
    "R": "Carrera",
    "S": "Sprint",
    "SQ": "Clasificación Sprint",
    "SS": "Sprint Shootout",
}

# Alias de compatibilidad
driver_codes = DRIVER_CODES
team_codes = TEAM_CODES
circuit_codes = CIRCUIT_CODES
tyre_compounds = TYRE_COMPOUNDS
session_codes = SESSION_CODES


def normalizar_codigo_piloto(codigo: str) -> str:
    """Normaliza un código de piloto a mayúsculas sin espacios (ej. 'ver ' -> 'VER')."""
    return str(codigo).strip().upper()


def normalizar_escuderia(nombre: str) -> str:
    """Devuelve el nombre oficial normalizado de una escudería si existe en catálogo."""
    limpio = str(nombre).strip()
    if limpio in TEAM_CODES:
        return TEAM_CODES[limpio]
    for clave, oficial in TEAM_CODES.items():
        if clave.lower() == limpio.lower() or oficial.lower() == limpio.lower():
            return oficial
    return limpio


def normalizar_circuito(nombre: str) -> str:
    """Devuelve el nombre oficial normalizado de un circuito si existe en catálogo."""
    limpio = str(nombre).strip()
    if limpio in CIRCUIT_CODES:
        return CIRCUIT_CODES[limpio]
    for clave, oficial in CIRCUIT_CODES.items():
        if clave.lower() == limpio.lower() or oficial.lower() == limpio.lower():
            return oficial
    return limpio


def normalizar_compuesto(compuesto: str) -> str:
    """Normaliza el compuesto de neumático a mayúsculas estándar FIA."""
    return str(compuesto).strip().upper()
