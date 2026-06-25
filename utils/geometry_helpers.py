"""Geometry helpers for custom profile Ap/V calculations."""

from __future__ import annotations


def calculate_custom_profile_apv(a: float, b: float, area: float) -> int:
    """Calculate Ap/V for an Andre profiler geometry.

    ``a`` and ``b`` are the exposed/internal profile geometry lengths in mm and
    ``area`` is the steel cross-sectional area (A) in mm². The resulting Ap/V is
    returned in m²/m³, rounded to the nearest integer.
    """

    if area <= 0:
        raise ValueError("Area (A) must be greater than zero")

    if a < 0 or b < 0:
        raise ValueError("Geometry lengths a and b cannot be negative")

    return round(((a + b) * 1000) / area)
