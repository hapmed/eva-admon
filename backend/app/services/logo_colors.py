"""Extracción de los colores dominantes de un logo (para personalizar el PDF)."""

from __future__ import annotations

import io

from PIL import Image


def extract_colors(data: bytes) -> tuple[str, str]:
    """Devuelve (primary, secondary) en formato #rrggbb, o ("", "") si falla."""
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:  # noqa: BLE001 - imagen inválida
        return "", ""

    image.thumbnail((160, 160))
    quantized = image.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    palette: list[int] = quantized.getpalette() or []
    entries: list[tuple[int, int]] = sorted(quantized.getcolors() or [], reverse=True)  # type: ignore[arg-type]

    colors: list[tuple[int, int, int]] = []
    for _count, index in entries:
        rgb = tuple(palette[index * 3 : index * 3 + 3])
        if len(rgb) < 3:
            continue
        r, g, b = rgb
        if r > 238 and g > 238 and b > 238:  # casi blanco
            continue
        if r < 18 and g < 18 and b < 18:  # casi negro
            continue
        colors.append((r, g, b))
        if len(colors) >= 2:
            break

    if not colors:
        return "", ""

    primary = "#{:02x}{:02x}{:02x}".format(*colors[0])
    secondary = "#{:02x}{:02x}{:02x}".format(*(colors[1] if len(colors) > 1 else colors[0]))
    return primary, secondary
