# Box Plots F1

Plataforma interactiva de **datos, telemetría e historia de la Fórmula 1 (1950–2026)**, construida en **Python + Streamlit + Plotly**.

🔗 **App en vivo:** [box-plots-f1.streamlit.app](https://box-plots-f1.streamlit.app)

> **Fuentes oficiales de datos:** [OpenF1 API](https://openf1.org/) (telemetría y sesiones 2023+) · [Jolpica / Ergast F1 API](https://github.com/jolpica/jolpica-f1) (archivo histórico 1950–2026).

---

## Secciones Principales

1. **🏁 Pit Wall · Telemetría (`app/inicio.py`):**
   - Selección directa de temporada, Gran Premio y sesión vía **OpenF1**.
   - Resumen de ritmo por vuelta con filtro de vueltas de Pit, Safety Car y tráfico.
   - Comparativa de telemetría y mapa de calor del circuito `(x, y)` entre dos pilotos.
   - Estrategia de neumáticos, degradación por stint y ventana estimada de *undercut*.
2. **🏆 Archivo de Temporadas (`app/pages/05_Mundiales_GP.py`):**
   - Resumen ejecutivo de cada campeonato (`1950–2026`) y fichas ilustradas de los monoplazas campeones.
   - Clasificaciones mundiales de Pilotos y Constructores con gráficos editoriales horizontales.
   - Resultados carrera por carrera con podio visual.
3. **⚔️ Duelos H2H & Fiabilidad (`app/pages/06_Duelos_y_Fiabilidad.py`):**
   - Comparativa cabeza a cabeza (*Head-to-Head*) de puntos acumulados y ritmo vuelta a vuelta.
   - Tasa de fiabilidad por constructor y principales causas de abandono.
   - Índice de movilidad en carrera (`Parrilla → Meta`) por piloto y por circuito.
4. **🏛️ Circuitos & Leyendas (`app/pages/08_Mapa_y_Salon_Fama.py`):**
   - Globo terráqueo 3D interactivo con todos los circuitos de la Fórmula 1 y zoom sobre cada trazado.
   - Salón de la Fama con perfiles históricos, retratos editoriales y evolución de puntos por temporada.
5. **📖 Glosario & 2026 (`app/pages/09_Glosario_y_Reglamento_2026.py`):**
   - Glosario interactivo con búsqueda y filtro condicionado por categoría y nivel (`Básico` / `Técnico`).
   - Gama visual de compuestos Pirelli, banderas FIA y sistema oficial de puntos.
   - Guía ilustrada del **Nuevo Reglamento Técnico FIA 2026**.
6. **🏎️ Raceboxd (`app/pages/10_Raceboxd.py`):**
   - Diario personal de Grandes Premios con calificaciones (`0.5★`–`5.0★`), etiquetas rápidas, Piloto del Día y reseñas.
   - Generador de **Tickets de Paddock descargables en PNG** (formato vertical `9:16` y panorámico `16:9`) con paleta dinámica por país, trazado del circuito y podio oficial.
7. **🎲 Predicciones (En Pits) (`app/pages/11_Predicciones_Construccion.py`):**
   - Sección reservada en boxes para futuras actualizaciones.

---

## Ejecución Local

```bash
git clone https://github.com/Rusanov16/box-plots-f1.git
cd box-plots-f1
python -m venv .venv
.\.venv\Scripts\activate      # Windows
pip install -r requirements.txt
streamlit run app/app.py
```

---

*Desarrollado por **Russanov & Nina Motorsport** · 2026*
