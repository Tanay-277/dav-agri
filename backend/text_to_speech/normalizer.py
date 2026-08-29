from __future__ import annotations

import re


def normalize_number(value: float | int | str, language: str = "en") -> str:
    """Convert a numeric value to a spoken-form string.

    For backend TTS, we keep numbers as digits with commas for readability.
    The TTS engine will handle digit-to-speech conversion.
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)

    if num == int(num):
        return f"{int(num):,}"
    return f"{num:,.2f}"


def normalize_unit(metric: str, value: float, language: str = "en") -> str:
    """Return a localized unit string for a given metric and value."""
    units = {
        "rainfall_mm": "mm",
        "temperature_c": "degrees",
        "humidity_pct": "percent",
        "soil_moisture_pct": "percent",
        "wind_speed_kmh": "km/h",
        "yield_kg_per_ha": "kg per hectare",
        "production_tonnes": "tonnes",
    }
    unit = units.get(metric, "")
    if not unit:
        return ""
    if unit == "percent":
        return f"{normalize_number(value)} percent"
    if unit == "degrees":
        return f"{normalize_number(value)} degrees"
    return f"{normalize_number(value)} {unit}"


def normalize_for_tts(text: str, language: str = "en") -> str:
    """Prepare text for speech synthesis."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\bmm\b", "millimeters", text, flags=re.IGNORECASE)
    text = re.sub(r"\bkg\b", "kilograms", text, flags=re.IGNORECASE)
    text = re.sub(r"\bkm/h\b", "kilometers per hour", text, flags=re.IGNORECASE)
    return text.strip()
