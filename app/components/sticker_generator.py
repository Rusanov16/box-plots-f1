"""Generador de tickets PNG editoriales para Raceboxd (9:16 vertical y 16:9 horizontal)."""

from __future__ import annotations

import io
import math
import re
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

# Constante de marca fácil de editar
BRAND_FOOTER = "BOX PLOTS F1 · ARCHIVO"

CREAM = "#F2EAD7"
CREAM_TAG = "#E8DFC8"
INK = "#1C1C1C"
MUTED = "#5A564E"
MCLAREN_RED = "#E11D24"
CHAOS_TEXT = "#9E1B1B"
DARK_BAR = "#161B26"
OUTER_BG = "#14181C"
DEFAULT_STUB = "#1C1C1C"

COLORES_PAIS: Dict[str, str] = {
    "BRA": "#1B4D2E",  # Verde bosque
    "ITA": "#9E1B1B",  # Rosso corsa oscuro
    "EMI": "#9E1B1B",
    "MON": "#1B365D",  # Azul marino clásico
    "FRA": "#1B365D",
    "GBR": "#143D2B",  # British Racing Green
    "NED": "#B84A14",  # Naranja quemado
    "JPN": "#222222",  # Carbón
    "BEL": "#2C221E",  # Carbón cálido
    "AUT": "#7A1C1C",
    "ESP": "#8C2D19",
    "USA": "#1E2D4A",
    "UAE": "#1E3A3A",
    "AUS": "#174A38",
    "CAN": "#7C1D24",
    "MEX": "#1B4D3E",
    "SIN": "#2B1E3E",
}

ETIQUETAS_CAOS = {"CAOS MECANICO", "CAOS MECÁNICO", "BANDERA ROJA", "RULETA RUSA", "DRAMA RADIO"}

# Puntos de control de circuitos (se suavizan con Catmull-Rom a ~48-60 vértices)
_CONTROL_CIRCUITOS: Dict[str, List[Tuple[float, float]]] = {
    "ITA": [(0.14, 0.84), (0.86, 0.84), (0.92, 0.74), (0.80, 0.58), (0.72, 0.34), (0.64, 0.16), (0.44, 0.16), (0.30, 0.28), (0.36, 0.50), (0.16, 0.64)],
    "BRA": [(0.16, 0.22), (0.50, 0.14), (0.82, 0.18), (0.88, 0.40), (0.66, 0.50), (0.74, 0.72), (0.50, 0.88), (0.24, 0.74), (0.40, 0.54), (0.14, 0.44)],
    "MON": [(0.12, 0.76), (0.34, 0.58), (0.54, 0.28), (0.74, 0.16), (0.90, 0.24), (0.84, 0.44), (0.62, 0.50), (0.50, 0.70), (0.28, 0.86)],
    "GBR": [(0.20, 0.80), (0.54, 0.86), (0.80, 0.68), (0.74, 0.40), (0.90, 0.24), (0.62, 0.14), (0.36, 0.26), (0.24, 0.48), (0.14, 0.64)],
    "BEL": [(0.14, 0.70), (0.36, 0.84), (0.60, 0.70), (0.78, 0.46), (0.88, 0.22), (0.64, 0.14), (0.46, 0.34), (0.26, 0.40)],
    "JPN": [(0.12, 0.62), (0.38, 0.52), (0.62, 0.24), (0.86, 0.22), (0.88, 0.46), (0.72, 0.68), (0.44, 0.54), (0.26, 0.82), (0.10, 0.74)],
    "AUT": [(0.14, 0.78), (0.52, 0.80), (0.86, 0.74), (0.80, 0.24), (0.46, 0.16), (0.36, 0.44), (0.22, 0.56)],
    "ESP": [(0.14, 0.76), (0.52, 0.78), (0.86, 0.74), (0.84, 0.36), (0.60, 0.20), (0.38, 0.40), (0.20, 0.32)],
    "USA": [(0.14, 0.80), (0.44, 0.48), (0.72, 0.16), (0.88, 0.28), (0.64, 0.52), (0.78, 0.74), (0.44, 0.86)],
    "UAE": [(0.16, 0.82), (0.54, 0.84), (0.84, 0.80), (0.86, 0.46), (0.54, 0.42), (0.56, 0.16), (0.24, 0.22)],
    "NED": [(0.18, 0.78), (0.52, 0.82), (0.84, 0.64), (0.78, 0.24), (0.48, 0.18), (0.32, 0.44), (0.16, 0.52)],
}
_CONTROL_DEFAULT: List[Tuple[float, float]] = [
    (0.18, 0.76), (0.52, 0.80), (0.84, 0.72), (0.88, 0.44), (0.68, 0.20), (0.32, 0.20), (0.14, 0.48)
]


def _suavizar_catmull_rom(pts: List[Tuple[float, float]], pasos_por_seg: int = 6) -> List[Tuple[float, float]]:
    """Interpola una curva cerrada Catmull-Rom de 45–60 vértices."""
    n = len(pts)
    if n < 3:
        return pts
    out: List[Tuple[float, float]] = []
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        for s in range(pasos_por_seg):
            t = s / pasos_por_seg
            t2, t3 = t * t, t * t * t
            x = 0.5 * (
                (2 * p1[0])
                + (-p0[0] + p2[0]) * t
                + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                (2 * p1[1])
                + (-p0[1] + p2[1]) * t
                + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            out.append((x, y))
    out.append(out[0])
    return out


def _dibujar_silueta_circuito(
    draw: ImageDraw.ImageDraw, codigo: str, x0: int, y0: int, w: int, h: int
) -> None:
    ctrl = _CONTROL_CIRCUITOS.get(codigo.upper(), _CONTROL_DEFAULT)
    suave = _suavizar_catmull_rom(ctrl, pasos_por_seg=6)
    pts = [(x0 + px * w, y0 + py * h) for px, py in suave]
    draw.line(pts, fill=CREAM, width=3, joint="curve")
    sx, sy = pts[0]
    draw.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=MCLAREN_RED, outline=CREAM, width=1)


def _dibujar_codigo_barras(
    draw: ImageDraw.ImageDraw, x0: int, y0: int, w: int, h: int, seed_str: str, color: str = INK
) -> None:
    """Dibuja un código de barras minimalista determinista basado en la carrera."""
    patron = [((ord(ch) * (i + 3)) % 3) + 1 for i, ch in enumerate(seed_str * 4)]
    x = x0
    idx = 0
    while x < x0 + w:
        bw = patron[idx % len(patron)]
        if idx % 2 == 0 and x + bw <= x0 + w:
            draw.rectangle([x, y0, x + bw, y0 + h], fill=color)
        x += bw + 2
        idx += 1


def _load_font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidatos: List[str] = []
    if mono:
        candidatos = [
            "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ]
    else:
        candidatos = [
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]
    for path in candidatos:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _limpiar_texto_png(texto: str) -> str:
    limpio = re.sub(r"[^\x20-\x7E\u00C0-\u024F\u2013\u2014\u201C\u201D\u00B7]", "", str(texto))
    return " ".join(limpio.split())


def _dibujar_estrella(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, color: str, media: bool = False) -> None:
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    if not media:
        draw.polygon(pts, fill=color)
    else:
        draw.polygon(pts, fill="#D5CCB8")
        draw.polygon([(min(x, cx), y) for x, y in pts], fill=color)


def _dibujar_estrellas(
    draw: ImageDraw.ImageDraw, x0: int, y0: int, valor: float, color: str, r: int = 16, gap: int = 40
) -> None:
    enteras = int(valor)
    tiene_media = (valor - enteras) >= 0.5
    for i in range(5):
        cx = x0 + i * gap + r
        cy = y0 + r
        if i < enteras:
            _dibujar_estrella(draw, cx, cy, r, color, media=False)
        elif i == enteras and tiene_media:
            _dibujar_estrella(draw, cx, cy, r, color, media=True)
        else:
            _dibujar_estrella(draw, cx, cy, r, "#D5CCB8", media=False)


def _dibujar_etiquetas(
    draw: ImageDraw.ImageDraw, x0: int, y0: int, etiquetas: List[str], max_x: int, font_size: int = 16
) -> int:
    """Dibuja hasta 2 etiquetas compactas en una sola fila. Devuelve la nueva posición Y."""
    if not etiquetas:
        return y0
    f_tag = _load_font(font_size, bold=True, mono=True)
    tx = x0
    h_box = font_size + 14
    for tag in etiquetas[:2]:
        tw = int(draw.textlength(tag, font=f_tag)) + 20
        if tx + tw > max_x:
            break
        es_caos = tag.upper() in ETIQUETAS_CAOS
        borde = MCLAREN_RED if es_caos else INK
        txt_col = CHAOS_TEXT if es_caos else INK
        draw.rectangle([tx, y0, tx + tw, y0 + h_box], outline=borde, width=2, fill=CREAM_TAG)
        draw.text((tx + 10, y0 + 6), tag, fill=txt_col, font=f_tag)
        tx += tw + 10
    return y0 + h_box + 16


def generar_sticker_ticket_png(entrada: Dict[str, Any], formato: str = "ig") -> bytes:
    """Genera un PNG estilo Ticket de Paddock para vertical ('ig', 9:16) u horizontal ('x', 16:9)."""
    gp = _limpiar_texto_png(entrada.get("gp", "Gran Premio"))
    codigo = _limpiar_texto_png(entrada.get("codigo", "GP")).upper()[:3] or "GP"
    anio = str(entrada.get("anio", ""))
    ronda = int(entrada.get("ronda", 1) or 1)
    usuario = _limpiar_texto_png(entrada.get("usuario", "anonimo")) or "anonimo"
    dotd = _limpiar_texto_png(entrada.get("dotd", ""))
    podio = _limpiar_texto_png(entrada.get("podio", ""))
    resena = _limpiar_texto_png(entrada.get("resena", ""))
    estrellas = float(entrada.get("estrellas", 0.0))
    favorita = bool(entrada.get("favorita", False))
    etiquetas = [_limpiar_texto_png(t).upper() for t in entrada.get("etiquetas", []) if _limpiar_texto_png(t)][:2]

    stub_color = COLORES_PAIS.get(codigo, DEFAULT_STUB)
    star_color = stub_color if stub_color != "#222222" else INK
    serial_no = f"NO. {anio}{ronda:02d}"

    if formato == "x":
        W, H = 1200, 675
        img = Image.new("RGB", (W, H), OUTER_BG)
        d = ImageDraw.Draw(img)
        pad = 34
        d.rectangle([pad, pad, W - pad, H - pad], fill=CREAM, outline=INK, width=3)

        # Barra superior oscura
        d.rectangle([pad, pad, W - pad, pad + 54], fill=DARK_BAR)
        d.text((pad + 24, pad + 16), "RACEBOXD", fill=CREAM, font=_load_font(20, bold=True, mono=True))
        r_txt = f"R{ronda} | {anio}   {serial_no}"
        rw = int(d.textlength(r_txt, font=_load_font(18, mono=True)))
        d.text((W - pad - 24 - rw, pad + 18), r_txt, fill="#C8C0AA", font=_load_font(18, mono=True))

        # Talón izquierdo de color dinámico + silueta circuito
        lx0, ly0, lx1, ly1 = pad + 22, pad + 72, 386, H - pad - 76
        d.rectangle([lx0, ly0, lx1, ly1], fill=stub_color)
        d.text((lx0 + 24, ly0 + 18), f"TEMPORADA {anio}", fill="#E5E0D5", font=_load_font(17, mono=True))
        d.text((lx0 + 22, ly0 + 52), codigo, fill=CREAM, font=_load_font(114, bold=True))
        _dibujar_silueta_circuito(d, codigo, lx0 + 46, ly0 + 205, 226, 175)
        d.text((lx0 + 24, ly1 - 40), f"RONDA {ronda:02d}  |  {estrellas:.1f}/5", fill="#E5E0D5", font=_load_font(19, bold=True, mono=True))

        # Línea troquelada vertical + muescas arriba y abajo
        vx = 414
        for yy in range(pad + 66, H - pad - 68, 12):
            d.line([(vx, yy), (vx, min(yy + 6, H - pad - 68))], fill=MUTED, width=2)
        d.ellipse([vx - 15, pad + 39, vx + 15, pad + 69], fill=OUTER_BG)
        d.ellipse([vx - 15, H - pad - 78, vx + 15, H - pad - 48], fill=OUTER_BG)

        # Contenido derecho
        rx = 446
        y = pad + 76
        d.text((rx, y), gp[:28], fill=INK, font=_load_font(42, bold=True))
        y += 58
        _dibujar_estrellas(d, rx, y, estrellas, star_color, r=17, gap=42)
        if favorita:
            d.rectangle([W - pad - 170, y + 2, W - pad - 26, y + 34], outline=MCLAREN_RED, width=2, fill=CREAM_TAG)
            d.text((W - pad - 148, y + 8), "FAVORITA", fill=CHAOS_TEXT, font=_load_font(17, bold=True, mono=True))
        y += 50

        y = _dibujar_etiquetas(d, rx, y, etiquetas, W - pad - 26, font_size=16)

        if resena:
            lineas = textwrap.wrap(f'"{resena}"', width=44)[:3]
            q_h = max(46, len(lineas) * 30 + 6)
            d.rectangle([rx, y, rx + 6, y + q_h], fill=MCLAREN_RED)
            f_q = _load_font(22)
            for idx_l, lin in enumerate(lineas):
                d.text((rx + 20, y + idx_l * 30), lin, fill="#2A2A2A", font=f_q)

        # Bloque inferior anclado: Podio + Piloto del Día + Código de barras
        by = H - pad - 154 if (podio and dotd) else H - pad - 126
        for xx in range(rx, W - pad - 26, 10):
            d.line([(xx, by), (min(xx + 5, W - pad - 26), by)], fill=MUTED, width=1)
        by += 12
        if podio:
            d.text((rx, by), f"PODIO: {podio}", fill=INK, font=_load_font(18, bold=True, mono=True))
            by += 28
        if dotd:
            d.text((rx, by), f"PILOTO DEL DIA: {dotd.upper()}", fill=MUTED, font=_load_font(17, bold=True, mono=True))

        _dibujar_codigo_barras(d, W - pad - 156, H - pad - 134, 130, 44, f"{anio}{ronda}{codigo}", color=INK)

        # Pie oscuro
        d.rectangle([pad, H - pad - 58, W - pad, H - pad], fill=DARK_BAR)
        d.text((pad + 24, H - pad - 38), BRAND_FOOTER, fill=CREAM, font=_load_font(18, bold=True, mono=True))
        u_txt = f"@{usuario}"
        uw = int(d.textlength(u_txt, font=_load_font(18, mono=True)))
        d.text((W - pad - 24 - uw, H - pad - 38), u_txt, fill="#C8C0AA", font=_load_font(18, mono=True))

    else:
        # Vertical 9:16 (720 x 1280)
        W, H = 720, 1280
        img = Image.new("RGB", (W, H), OUTER_BG)
        d = ImageDraw.Draw(img)
        pad = 38
        d.rectangle([pad, pad, W - pad, H - pad], fill=CREAM, outline=INK, width=3)

        # Cabecera oscura
        d.rectangle([pad, pad, W - pad, pad + 78], fill=DARK_BAR)
        d.text((pad + 26, pad + 26), "RACEBOXD", fill=CREAM, font=_load_font(24, bold=True, mono=True))
        r_txt = f"R{ronda} | {anio}"
        rw = int(d.textlength(r_txt, font=_load_font(22, mono=True)))
        d.text((W - pad - 26 - rw, pad + 27), r_txt, fill="#C8C0AA", font=_load_font(22, mono=True))

        # Talón superior de color dinámico + silueta circuito
        gx0, gy0, gx1, gy1 = pad + 26, pad + 104, W - pad - 26, pad + 372
        d.rectangle([gx0, gy0, gx1, gy1], fill=stub_color)
        d.text((gx0 + 26, gy0 + 36), codigo, fill=CREAM, font=_load_font(134, bold=True))
        d.text((gx0 + 30, gy0 + 198), f"{anio}  |  {estrellas:.1f} / 5.0", fill="#FFD100", font=_load_font(26, bold=True, mono=True))
        _dibujar_silueta_circuito(d, codigo, gx1 - 224, gy0 + 40, 194, 184)

        # Muescas laterales + línea troquelada horizontal
        cy = pad + 412
        for xx in range(pad + 22, W - pad - 22, 12):
            d.line([(xx, cy), (min(xx + 6, W - pad - 22), cy)], fill=MUTED, width=2)
        d.ellipse([pad - 18, cy - 18, pad + 18, cy + 18], fill=OUTER_BG)
        d.ellipse([W - pad - 18, cy - 18, W - pad + 18, cy + 18], fill=OUTER_BG)

        # Título GP + Estrellas + Favorita
        y = cy + 34
        f_gp = _load_font(46, bold=True)
        for lin_gp in textwrap.wrap(gp, width=20)[:2]:
            d.text((pad + 30, y), lin_gp, fill=INK, font=f_gp)
            y += 54
        y += 12
        _dibujar_estrellas(d, pad + 30, y, estrellas, star_color, r=19, gap=46)
        if favorita:
            d.rectangle([W - pad - 178, y + 2, W - pad - 30, y + 36], outline=MCLAREN_RED, width=2, fill=CREAM_TAG)
            d.text((W - pad - 156, y + 9), "FAVORITA", fill=CHAOS_TEXT, font=_load_font(18, bold=True, mono=True))
        y += 62

        # Etiquetas (máx 2 en una fila; si no hay, no ocupa espacio)
        y = _dibujar_etiquetas(d, pad + 30, y, etiquetas, W - pad - 30, font_size=17)

        # Cita con barra roja
        if resena:
            lineas = textwrap.wrap(f'"{resena}"', width=34)[:5]
            q_h = max(62, len(lineas) * 34 + 8)
            d.rectangle([pad + 30, y, pad + 37, y + q_h], fill=MCLAREN_RED)
            f_q = _load_font(25)
            for idx_l, lin in enumerate(lineas):
                d.text((pad + 54, y + idx_l * 34), lin, fill="#2A2A2A", font=f_q)

        # Bloque inferior anclado: Podio + Piloto del Día + Código de barras + Serie
        by = H - pad - 235 if (podio and dotd) else H - pad - 200
        for xx in range(pad + 30, W - pad - 30, 10):
            d.line([(xx, by), (min(xx + 5, W - pad - 30), by)], fill=MUTED, width=1)
        by += 16
        if podio:
            d.text((pad + 30, by), f"PODIO: {podio}", fill=INK, font=_load_font(21, bold=True, mono=True))
            by += 34
        if dotd:
            d.text((pad + 30, by), f"PILOTO DEL DIA: {dotd.upper()}", fill=MUTED, font=_load_font(19, bold=True, mono=True))

        _dibujar_codigo_barras(d, pad + 30, H - pad - 134, 210, 38, f"{anio}{ronda}{codigo}", color=INK)
        sw = int(d.textlength(serial_no, font=_load_font(18, bold=True, mono=True)))
        d.text((W - pad - 30 - sw, H - pad - 118), serial_no, fill=MUTED, font=_load_font(18, bold=True, mono=True))

        # Pie oscuro
        d.rectangle([pad, H - pad - 72, W - pad, H - pad], fill=DARK_BAR)
        d.text((pad + 26, H - pad - 47), BRAND_FOOTER, fill=CREAM, font=_load_font(20, bold=True, mono=True))
        u_txt = f"@{usuario}"
        uw = int(d.textlength(u_txt, font=_load_font(20, mono=True)))
        d.text((W - pad - 26 - uw, H - pad - 47), u_txt, fill="#C8C0AA", font=_load_font(20, mono=True))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
