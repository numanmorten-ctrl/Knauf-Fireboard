"""Geometry helpers for custom profile Ap/V calculations."""

from __future__ import annotations


def calculate_custom_profile_apv(
    a: float | None,
    b: float | None,
    area: float | None,
    sides: int | str | None,
) -> int | None:
    """Calculate Ap/V for an Andre profiler geometry.

    ``a`` and ``b`` are profile geometry lengths in mm, ``area`` is the steel
    cross-sectional area (A) in mm², and ``sides`` is the selected number of
    protected/cladded sides. The exposed/internal perimeter follows the
    selected side count and the resulting Ap/V is returned in m²/m³, rounded to
    the nearest integer. Invalid or incomplete geometry returns ``None`` so the
    UI can keep guiding the user instead of failing.
    """

    try:
        a_value = float(a)
        b_value = float(b)
        area_value = float(area)
        sides_value = int(sides)
    except (TypeError, ValueError):
        return None

    if a_value <= 0 or b_value <= 0 or area_value <= 0:
        return None

    perimeter_by_sides = {
        1: a_value + (2 * b_value),
        2: a_value + b_value,
        3: a_value + (2 * b_value),
        4: (2 * a_value) + (2 * b_value),
    }

    perimeter = perimeter_by_sides.get(sides_value)
    if perimeter is None:
        return None

    return round((perimeter * 1000) / area_value)
