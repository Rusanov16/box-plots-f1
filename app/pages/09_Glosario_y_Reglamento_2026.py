"""Página 09: Glosario Técnico F1, Guía de Neumáticos y Nuevo Reglamento FIA 2026."""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = APP_DIR.parent
for _p in (str(ROOT_DIR), str(APP_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import streamlit as st

from components.theme import inject_editorial_theme, render_crt_header

st.set_page_config(page_title="Glosario y Reglamento 2026 — Box Plots F1", layout="wide")
inject_editorial_theme()
render_crt_header(
    canal="CH 05 · GLOSARIO & REGLAMENTO 2026",
    titulo="📖 Glosario Técnico F1 y Nuevo Reglamento 2026",
    subtitulo="Diccionario ilustrado de estrategia, aerodinámica, telemetría y cambios técnicos FIA 2026.",
)

GLOSARIO = [
    # Básicos de F1
    {
        "termino": "Pole Position",
        "categoria": "Básicos de F1",
        "nivel": "Básico",
        "definicion": "Primer puesto en la parrilla de salida, ganado por el piloto que registra la vuelta más rápida en la sesión de clasificación (Q3) (sujeto a posibles penalizaciones en parrilla).",
        "ejemplo": "Salir desde la pole en Mónaco es decisivo por la dificultad de adelantar en pista.",
    },
    {
        "termino": "Parrilla (Grid)",
        "categoria": "Básicos de F1",
        "nivel": "Básico",
        "definicion": "Orden de salida de los coches al comienzo del Gran Premio, determinado por la clasificación y posibles penalizaciones.",
        "ejemplo": "Salir P10 en parrilla significa arrancar desde la quinta fila.",
    },
    {
        "termino": "Pit Stop (Parada en Boxes)",
        "categoria": "Básicos de F1",
        "nivel": "Básico",
        "definicion": "Detención rápida en el pit box del equipo (frente al garaje, dentro del pit lane) para cambiar los cuatro neumáticos (obligatorio usar al menos dos compuestos distintos en carrera seca) o reparar daños.",
        "ejemplo": "Los equipos de punta cambian las 4 ruedas en ~2.0 a 2.4 segundos.",
    },
    {
        "termino": "Vuelta Rápida (Fastest Lap)",
        "categoria": "Básicos de F1",
        "nivel": "Básico",
        "definicion": "El giro más veloz registrado por un piloto durante toda la carrera, normalmente al final con poco combustible y neumáticos frescos.",
        "ejemplo": "Suele marcarse en las últimas vueltas cuando el coche pesa ~70 kg menos que en la salida (con las unidades de potencia de 2026 y combustible 100% sostenible).",
    },
    {
        "termino": "Penalizaciones (5s, 10s, Grid Drop)",
        "categoria": "Básicos de F1",
        "nivel": "Básico",
        "definicion": "Sanciones deportivas impuestas por los comisarios FIA por exceder límites de pista, causar colisiones o cambiar componentes de motor fuera de cuota.",
        "ejemplo": "Una sanción de 5 segundos se cumple en la siguiente parada o se suma al tiempo final.",
    },
    {
        "termino": "Grand Chelem (Grand Slam)",
        "categoria": "Básicos de F1",
        "nivel": "Básico",
        "definicion": "Hazaña de lograr en un mismo Gran Premio la Pole Position, la victoria, la vuelta rápida y liderar absolutamente todas las vueltas de la carrera.",
        "ejemplo": "Jim Clark (8), Lewis Hamilton (6) y Max Verstappen (6) lideran este registro histórico.",
    },
    # Estrategia & Neumáticos
    {
        "termino": "Undercut",
        "categoria": "Estrategia & Neumáticos",
        "definicion": "Entrar a boxes una o dos vueltas antes que un rival directo para aprovechar el mayor agarre del neumático nuevo, marcar vueltas rápidas y superarlo cuando el rival haga su parada.",
        "ejemplo": "Si el neumático nuevo es 1.5 s/vuelta más rápido, una parada anticipada puede voltear una desventaja de 1–2 s.",
    },
    {
        "termino": "Overcut",
        "categoria": "Estrategia & Neumáticos",
        "definicion": "Estrategia opuesta al undercut: quedarse en pista más vueltas que el rival cuando los neumáticos viejos aún mantienen buen ritmo o cuesta calentar el compuesto nuevo.",
        "ejemplo": "Muy efectivo en circuitos urbanos como Mónaco donde el aire limpio vale más que la goma fresca.",
    },
    {
        "termino": "Stint",
        "categoria": "Estrategia & Neumáticos",
        "definicion": "Tramo continuo de vueltas que completa un piloto con un mismo juego de neumáticos entre la salida y una parada en boxes (o entre dos paradas).",
        "ejemplo": "Una carrera a 2 paradas consta de 3 stints (ej. Soft → Medium → Hard).",
    },
    {
        "termino": "Degradación (s/vuelta)",
        "categoria": "Estrategia & Neumáticos",
        "definicion": "Pérdida progresiva de rendimiento del neumático por desgaste térmico o mecánico, medida en segundos perdidos por cada vuelta adicional del stint.",
        "ejemplo": "Una degradación de 0.15 s/vuelta implica perder ~1.5 s de ritmo tras 10 vueltas.",
    },
    {
        "termino": "Pit Loss (Tiempo en Pit Lane)",
        "categoria": "Estrategia & Neumáticos",
        "definicion": "Tiempo neto perdido por entrar al pit lane, detenerse a cambiar neumáticos y reincorporarse a pista respecto a un coche que sigue a velocidad de carrera.",
        "ejemplo": "Oscila entre ~18–20 s (Spa / Austria) y ~28–29 s (Singapur / Imola).",
    },
    {
        "termino": "Graining",
        "categoria": "Estrategia & Neumáticos",
        "definicion": "Deslizamiento excesivo del neumático cuando la goma aún está fría o la pista tiene poco agarre, arrancando pequeñas virutas que se pegan a la banda de rodadura y reducen el grip.",
        "ejemplo": "Suele aparecer en el eje delantero en circuitos fríos como Las Vegas o China.",
    },
    {
        "termino": "Blistering",
        "categoria": "Estrategia & Neumáticos",
        "definicion": "Sobrecalentamiento interno de la goma que genera ampollas en la superficie del neumático, provocando vibraciones y pérdida brusca de rendimiento.",
        "ejemplo": "Frecuente en curvas rápidas de alta energía lateral como Silverstone o Spa.",
    },
    {
        "termino": "Cliff (Caída de rendimiento)",
        "categoria": "Estrategia & Neumáticos",
        "definicion": "Punto crítico de desgaste a partir del cual el neumático pierde agarre de golpe y los tiempos por vuelta empeoran varios segundos en apenas 1 o 2 giros.",
        "ejemplo": "Alargar demasiado un stint con Soft suele terminar en el 'cliff' antes de boxes.",
    },
    # Aerodinámica & Técnica
    {
        "termino": "Downforce (Carga Aerodinámica)",
        "categoria": "Aerodinámica & Técnica",
        "definicion": "Fuerza vertical hacia abajo generada por los alerones y el suelo del monoplaza que pega los neumáticos al asfalto, permitiendo pasar mucho más rápido por curva.",
        "ejemplo": "En Mónaco se usa carga máxima; en Monza se reduce al mínimo para priorizar velocidad punta.",
    },
    {
        "termino": "Aire Sucio (Dirty Air)",
        "categoria": "Aerodinámica & Técnica",
        "definicion": "Estela turbulenta que deja el coche de adelante y que reduce la carga aerodinámica del perseguidor en curvas, dificultando acercarse y sobrecalentando sus neumáticos.",
        "ejemplo": "Seguir a <1.5 s en curvas rápidas aumenta notablemente la degradación delantera.",
    },
    {
        "termino": "Rebufo (Slipstream / Tow)",
        "categoria": "Aerodinámica & Técnica",
        "definicion": "Ganancia de velocidad punta en recta al rodar justo detrás de otro coche, aprovechando el vacío aerodinámico que corta el viento.",
        "ejemplo": "En rectas largas como Bakú o Monza puede aportar +10 a +15 km/h extra.",
    },
    {
        "termino": "Efecto Suelo y Porpoising",
        "categoria": "Aerodinámica & Técnica",
        "definicion": "Generación de succión mediante túneles Venturi bajo el coche. El porpoising es el rebote vertical a alta velocidad cuando esa succión se pierde y recupera cíclicamente.",
        "ejemplo": "Fue el gran desafío técnico al inicio de la era reglamentaria 2022–2025.",
    },
    {
        "termino": "Aerodinámica Activa (Corner / Straight Mode)",
        "categoria": "Aerodinámica & Técnica",
        "definicion": "Sistema introducido en 2026 donde alerón delantero y trasero cambian de ángulo: Corner Mode (Z-Mode) ofrece máxima carga en curva y Straight Mode (X-Mode) reduce la resistencia al aire en rectas.",
        "ejemplo": "Reemplaza al DRS tradicional y está disponible para todos los pilotos en zonas designadas.",
    },
    {
        "termino": "Overtake Mode / Manual Override (2026)",
        "categoria": "Aerodinámica & Técnica",
        "definicion": "Modo de adelantamiento eléctrico de 2026 que permite al piloto a menos de 1 segundo del coche delantero mantener los 350 kW del MGU-K hasta los 337 km/h (en lugar del recorte progresivo desde los 290 km/h) con energía adicional.",
        "ejemplo": "Cumple el rol táctico de adelantamiento que antes tenía el DRS.",
    },
    # Carrera & Telemetría
    {
        "termino": "DNF / DNS / DSQ",
        "categoria": "Carrera & Telemetría",
        "definicion": "Siglas oficiales de clasificación: DNF (Did Not Finish — abandono), DNS (Did Not Start — no tomó la salida) y DSQ (Disqualified — descalificado tras verificación técnica).",
        "ejemplo": "Un fallo de motor en la vuelta 40 figura como DNF; un fondo plano fuera de norma, como DSQ.",
    },
    {
        "termino": "Safety Car (SC) / Virtual Safety Car (VSC)",
        "categoria": "Carrera & Telemetría",
        "definicion": "Neutralizaciones de carrera por incidente en pista. Reducen la velocidad del pelotón y abaratan drásticamente el tiempo perdido al entrar a boxes ('parada barata').",
        "ejemplo": "Bajo VSC el pit loss cae ~40%, abriendo ventanas tácticas inesperadas.",
    },
    {
        "termino": "Apex (Vértice)",
        "categoria": "Carrera & Telemetría",
        "definicion": "Punto más interior de una curva por donde pasa el monoplaza para maximizar el radio de giro y acelerar lo antes posible hacia la salida.",
        "ejemplo": "Un 'late apex' sacrifica entrada para salir más recto y rápido hacia una recta larga.",
    },
    {
        "termino": "Lift and Coast",
        "categoria": "Carrera & Telemetría",
        "definicion": "Técnica de soltar el acelerador metros antes de la frenada y dejar rodar el coche por inercia para ahorrar combustible, enfriar frenos o cuidar la unidad de potencia.",
        "ejemplo": "Habitual en los últimos giros de carrera cuando el coche va al límite de gasolina o temperatura.",
    },
    {
        "termino": "Parc Fermé",
        "categoria": "Carrera & Telemetría",
        "definicion": "Régimen reglamentario que congela la puesta a punto del monoplaza desde el inicio de la clasificación hasta la carrera; romperlo obliga a salir desde el pit lane.",
        "ejemplo": "Cambiar especificaciones de suspensión o alerón tras Qualy implica salida desde boxes. En fines de semana Sprint, el Parc Fermé se reabre brevemente entre la carrera Sprint y la clasificación del GP.",
    },
    {
        "termino": "Delta vs. Compañero",
        "categoria": "Carrera & Telemetría",
        "definicion": "Diferencia de posición o ritmo entre dos pilotos que conducen el mismo coche, la métrica más justa para aislar el rendimiento del piloto frente al del monoplaza.",
        "ejemplo": "Bajo la convención (Posición piloto − Posición compañero), un delta negativo (-1.8) indica terminar sistemáticamente delante del compañero.",
    },
]

tab_glos, tab_pirelli, tab_2026 = st.tabs(
    ["📖 Glosario Interactivo", "Compuestos Pirelli & Banderas", "Nuevo Reglamento FIA 2026"]
)

with tab_glos:
    c1, c2, c3 = st.columns([2, 1, 1])
    busqueda = c1.text_input("Buscar término o palabra clave", placeholder="Ej. pole, undercut, graining, Corner Mode...")
    categorias = ["Todas"] + sorted({g["categoria"] for g in GLOSARIO})
    cat_sel = c2.selectbox("Categoría", categorias)
    niveles_disponibles = sorted(
        {g.get("nivel", "Técnico") for g in GLOSARIO if cat_sel == "Todas" or g["categoria"] == cat_sel}
    )
    opciones_nivel = ["Todos"] + niveles_disponibles if len(niveles_disponibles) > 1 else niveles_disponibles
    nivel_sel = c3.selectbox("Nivel", opciones_nivel)

    filtrados = [
        g
        for g in GLOSARIO
        if (cat_sel == "Todas" or g["categoria"] == cat_sel)
        and (nivel_sel == "Todos" or g.get("nivel", "Técnico") == nivel_sel)
        and (
            not busqueda.strip()
            or busqueda.lower() in g["termino"].lower()
            or busqueda.lower() in g["definicion"].lower()
        )
    ]

    if not filtrados:
        st.info("No se encontraron términos que coincidan con tu búsqueda.")
    else:
        st.caption(f"Mostrando **{len(filtrados)}** de {len(GLOSARIO)} términos.")
        for i in range(0, len(filtrados), 2):
            cols = st.columns(2)
            for col, item in zip(cols, filtrados[i : i + 2]):
                nivel = item.get("nivel", "Técnico")
                badge_bg = "#277B47" if nivel == "Básico" else "#1C1C1C"
                col.markdown(
                    f'<div style="background:#FFFFFF; border:1px solid rgba(28,28,28,0.14); '
                    f'border-left:4px solid #E11D24; border-radius:8px; padding:16px 18px; '
                    f'margin-bottom:12px; min-height:178px; display:flex; flex-direction:column; justify-content:space-between;">'
                    f'<div>'
                    f'<div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">'
                    f'<span style="font-family:\'IBM Plex Mono\',monospace; font-size:0.70rem; color:#5A564E; text-transform:uppercase; letter-spacing:0.08em;">{item["categoria"]}</span>'
                    f'<span style="font-family:\'IBM Plex Mono\',monospace; font-size:0.64rem; color:#FFFFFF; background:{badge_bg}; padding:2px 7px; border-radius:4px; text-transform:uppercase;">{nivel}</span>'
                    f'</div>'
                    f'<div style="font-family:\'Plus Jakarta Sans\',sans-serif; font-size:1.12rem; font-weight:800; color:#1C1C1C; margin:6px 0 8px 0;">{item["termino"]}</div>'
                    f'<p style="font-size:0.88rem; color:#2A2A2A; margin:0 0 10px 0; line-height:1.45;">{item["definicion"]}</p>'
                    f'</div>'
                    f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.76rem; color:#277B47; background:#F7F4EC; padding:6px 10px; border-radius:4px;">💡 {item["ejemplo"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

with tab_pirelli:
    st.subheader("Gama de Compuestos Pirelli")
    compuestos = [
        ("SOFT", "#E11D24", 5, 1, "Clasificación (Qualy) y stints cortos de máximo ataque."),
        ("MEDIUM", "#FFD100", 3, 3, "Equilibrio ideal para estrategias a 1 o 2 paradas."),
        ("HARD", "#D9D9D9", 2, 5, "Stints largos en circuitos exigentes o asfalto abrasivo."),
        ("INTERMEDIO", "#277B47", 4, 3, "Pista húmeda o lluvia ligera (~30 L/s a 300 km/h)."),
        ("WET", "#1E6BD6", 3, 4, "Lluvia intensa y agua estancada (~85 L/s a 300 km/h)."),
    ]

    def _mini_barras(nivel: int, color: str) -> str:
        return "".join(
            f'<span style="display:inline-block; width:16%; height:6px; border-radius:2px; margin-right:3px; '
            f'background:{color if idx < nivel else "#E5E0D5"};"></span>'
            for idx in range(5)
        )

    cols_p = st.columns(5)
    for col, (nombre, color_aro, agarre, durab, desc) in zip(cols_p, compuestos):
        ring_svg = (
            f'<svg width="56" height="56" viewBox="0 0 64 64" style="display:block; margin:0 auto 8px auto;">'
            f'<circle cx="32" cy="32" r="28" fill="#1C1C1C"/>'
            f'<circle cx="32" cy="32" r="21" fill="none" stroke="{color_aro}" stroke-width="5"/>'
            f'<circle cx="32" cy="32" r="11" fill="#F7F4EC"/>'
            f'<circle cx="32" cy="32" r="4" fill="#1C1C1C"/>'
            f'</svg>'
        )
        col.markdown(
            f'<div style="background:#FFFFFF; border:1px solid rgba(28,28,28,0.14); border-top:3px solid {color_aro}; '
            f'border-radius:8px; padding:14px 12px; min-height:235px; display:flex; flex-direction:column; justify-content:space-between;">'
            f'<div>{ring_svg}'
            f'<div style="font-family:\'IBM Plex Mono\',monospace; font-weight:700; font-size:0.86rem; text-align:center; color:#1C1C1C; margin-bottom:10px;">{nombre}</div>'
            f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.65rem; color:#5A564E; margin-bottom:2px;">AGARRE</div>'
            f'<div style="margin-bottom:6px;">{_mini_barras(agarre, "#E11D24")}</div>'
            f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.65rem; color:#5A564E; margin-bottom:2px;">DURABILIDAD</div>'
            f'<div style="margin-bottom:10px;">{_mini_barras(durab, "#277B47")}</div>'
            f'</div>'
            f'<p style="font-size:0.78rem; color:#2A2A2A; margin:0; line-height:1.38;">{desc}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.subheader("Referencia Rápida de Banderas FIA")
    banderas_cards = [
        ("Verde", "background:#277B47;", "Pista libre, inicio de sesión o fin de zona de peligro."),
        ("Amarilla", "background:#FFD100;", "Peligro en el sector: reducir velocidad y prohibido adelantar."),
        ("Roja", "background:#E11D24;", "Sesión o carrera detenida; todos los coches regresan al pit lane."),
        ("Azul", "background:#1E6BD6;", "Coche más rápido a punto de doblarte: ceder el paso."),
        ("Blanca y Negra", "background:linear-gradient(135deg, #1C1C1C 50%, #FFFFFF 50%);", "Advertencia por conducta antideportiva (último aviso antes de sanción)."),
        ("Cuadros", "background:repeating-conic-gradient(#1C1C1C 0% 25%, #FFFFFF 0% 50%) 50% / 14px 14px;", "Fin oficial de la sesión o del Gran Premio."),
    ]
    tarjetas_band = "".join(
        f'<div style="background:#FFFFFF; border:1px solid rgba(28,28,28,0.14); border-radius:8px; '
        f'padding:12px 14px; display:flex; align-items:center; gap:14px;">'
        f'<div style="width:52px; height:36px; border-radius:4px; border:1px solid #1C1C1C; flex-shrink:0; {css_bg}"></div>'
        f'<div><div style="font-family:\'Plus Jakarta Sans\',sans-serif; font-weight:800; font-size:0.94rem; color:#1C1C1C;">{nom}</div>'
        f'<div style="font-size:0.80rem; color:#4A4A4A; line-height:1.35; margin-top:2px;">{sig}</div></div>'
        f'</div>'
        for nom, css_bg, sig in banderas_cards
    )
    st.markdown(
        f'<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(290px, 1fr)); gap:12px; margin-top:8px;">{tarjetas_band}</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("Sistema Oficial de Puntos FIA")
    escala_puntos = [
        ("P1", 25, 8), ("P2", 18, 7), ("P3", 15, 6), ("P4", 12, 5), ("P5", 10, 4),
        ("P6", 8, 3), ("P7", 6, 2), ("P8", 4, 1), ("P9", 2, 0), ("P10", 1, 0),
    ]
    cards_pts = "".join(
        f'<div style="background:#FFFFFF; border:1px solid rgba(28,28,28,0.14); '
        f'border-top:3px solid {"#E11D24" if pos == "P1" else ("#277B47" if pos in ("P2", "P3") else "#2A2A2A")}; '
        f'border-radius:6px; padding:10px 8px; text-align:center;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.70rem; color:#5A564E; font-weight:600;">{pos}</div>'
        f'<div style="font-family:\'Plus Jakarta Sans\',sans-serif; font-size:1.35rem; font-weight:800; color:#1C1C1C; margin:2px 0;">{gp}</div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.66rem; color:#5A564E;">GP pts</div>'
        f'<div style="margin-top:6px; font-family:\'IBM Plex Mono\',monospace; font-size:0.66rem; '
        f'background:{"#F7F4EC" if sp > 0 else "transparent"}; color:{"#277B47" if sp > 0 else "#A09A8E"}; '
        f'padding:2px 4px; border-radius:4px;">{"Sprint +" + str(sp) if sp > 0 else "—"}</div>'
        f'</div>'
        for pos, gp, sp in escala_puntos
    )
    st.markdown(
        f'<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(92px, 1fr)); gap:10px; margin-top:8px;">{cards_pts}</div>',
        unsafe_allow_html=True,
    )

with tab_2026:
    st.subheader("Nuevo Reglamento Técnico FIA 2026")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Potencia Eléctrica", "350 kW", delta="50% eléctrica · 3x vs. 2025")
    k2.metric("Peso Mínimo", "768 kg", delta="-30 kg más ágiles", delta_color="inverse")
    k3.metric("Combustible", "E-Fuel", delta="100% sostenible (cero fósil)")
    k4.metric("Parrilla 2026", "22 Pilotos", delta="11 equipos (+Audi, +Cadillac)")

    # Láminas técnicas editoriales FIA 2026
    img_car = APP_DIR / "assets" / "fia_2026_car.jpg"
    img_cmp = APP_DIR / "assets" / "fia_2025_vs_2026.jpg"
    if img_car.exists() or img_cmp.exists():
        c_img1, c_img2 = st.columns(2)
        if img_car.exists():
            c_img1.image(str(img_car), caption="Aerodinámica activa (Corner / Straight Mode), fondo plano y MGU-K", width="stretch")
        if img_cmp.exists():
            c_img2.image(str(img_cmp), caption="Unidad de potencia 50/50 (350 kW) y chasis más compacto", width="stretch")

    st.markdown("### Comparativa Técnica: Era 2022–2025 vs. Nuevo Reglamento 2026")
    comp_2026 = pd.DataFrame(
        [
            {
                "Área Técnica": "Unidad de Potencia",
                "Reglamento 2022–2025": "V6 Turbo híbrido (~80% térmica / ~20% eléctrica) con MGU-K (120 kW) y MGU-H.",
                "Nuevo Reglamento 2026": "Reparto ~50% térmica / ~50% eléctrica: MGU-K sube a 350 kW y se elimina el complejo MGU-H.",
            },
            {
                "Área Técnica": "Aerodinámica y Adelantamiento",
                "Reglamento 2022–2025": "DRS tradicional solo en el alerón trasero cuando se está a <1.0 s del coche delantero.",
                "Nuevo Reglamento 2026": "Aerodinámica activa en ambos alerones: Z-Mode (alta carga en curva) y X-Mode (baja resistencia en recta) + Manual Override Mode eléctrico.",
            },
            {
                "Área Técnica": "Dimensiones y Peso",
                "Reglamento 2022–2025": "Distancia entre ejes máx. 3600 mm, ancho 2000 mm, peso mínimo 798 kg.",
                "Nuevo Reglamento 2026": "Coches más cortos (3400 mm), más estrechos (1900 mm) y 30 kg más ligeros (768 kg).",
            },
            {
                "Área Técnica": "Combustible",
                "Reglamento 2022–2025": "E10 (10% etanol renovable).",
                "Nuevo Reglamento 2026": "Combustible 100% sostenible avanzado (E-Fuel) en toda la parrilla.",
            },
            {
                "Área Técnica": "Parrilla Oficial",
                "Reglamento 2022–2025": "10 escuderías / 20 pilotos.",
                "Nuevo Reglamento 2026": "11 escuderías / 22 pilotos con la entrada oficial de Audi y Cadillac.",
            },
        ]
    )
    st.dataframe(comp_2026, width="stretch", hide_index=True)
