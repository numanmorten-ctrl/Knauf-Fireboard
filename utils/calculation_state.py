"""Helpers for storing calculations and their material lists in session state."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pandas as pd


MATERIALS_KEY = "materials_table"
PENDING_MATERIALS_KEY = "current_materials_table"
PENDING_SIGNATURE_KEY = "current_materials_signature"


def calculation_signature(calculation: dict[str, Any]) -> tuple[Any, ...]:
    """Return the input/result signature that identifies a rendered draft."""

    return (
        calculation.get("category"),
        calculation.get("profile"),
        calculation.get("montage"),
        calculation.get("sides"),
        calculation.get("fire_time"),
        calculation.get("temperature"),
        calculation.get("apv"),
        calculation.get("thickness"),
        calculation.get("apv_method"),
        calculation.get("custom_apv"),
        calculation.get("surface_area"),
        calculation.get("steel_area"),
    )


def calculation_material_key(calculation: dict[str, Any], index: int) -> str:
    """Build a stable display key for a calculation material list."""

    return (
        f"{index + 1}. {calculation.get('profile')}_"
        f"R{calculation.get('fire_time')}_"
        f"{calculation.get('temperature')}"
    )


def remember_current_materials(
    session_state: Any,
    calculation: dict[str, Any],
    materials_df: pd.DataFrame,
) -> None:
    """Store the currently rendered material list as the pending draft list."""

    session_state[PENDING_SIGNATURE_KEY] = calculation_signature(calculation)
    session_state[PENDING_MATERIALS_KEY] = materials_df.copy(deep=True)


def attach_pending_materials(
    session_state: Any,
    calculation: dict[str, Any],
) -> dict[str, Any]:
    """Return a calculation copy with the matching pending material list attached."""

    saved_calculation = deepcopy(calculation)

    if (
        session_state.get(PENDING_SIGNATURE_KEY)
        == calculation_signature(calculation)
        and session_state.get(PENDING_MATERIALS_KEY) is not None
    ):
        saved_calculation[MATERIALS_KEY] = session_state[
            PENDING_MATERIALS_KEY
        ].copy(deep=True)

    return saved_calculation


def replace_selected_calculation(
    session_state: Any,
    calculation: dict[str, Any],
) -> bool:
    """Replace the selected calculation at edit_index without appending."""

    edit_index = session_state.get("edit_index")
    calculations = session_state.get("calculations", [])

    if edit_index is None or not 0 <= edit_index < len(calculations):
        return False

    calculations[edit_index] = attach_pending_materials(
        session_state,
        calculation,
    )
    session_state["editing"] = True
    rebuild_combined_materials(session_state)
    return True


def append_new_calculation(
    session_state: Any,
    calculation: dict[str, Any],
) -> bool:
    """Append a new calculation unless it duplicates the latest saved input data."""

    saved_calculation = attach_pending_materials(session_state, calculation)
    comparable_saved = {
        key: value
        for key, value in saved_calculation.items()
        if key != MATERIALS_KEY
    }

    if session_state.get("calculations"):
        latest = {
            key: value
            for key, value in session_state["calculations"][-1].items()
            if key != MATERIALS_KEY
        }
        if latest == comparable_saved:
            return False

    session_state.setdefault("calculations", []).append(saved_calculation)
    rebuild_combined_materials(session_state)
    return True


def rebuild_combined_materials(session_state: Any) -> dict[str, pd.DataFrame]:
    """Rebuild combined materials from saved calculations only."""

    combined_materials: dict[str, pd.DataFrame] = {}

    for index, calculation in enumerate(session_state.get("calculations", [])):
        materials_df = calculation.get(MATERIALS_KEY)

        if materials_df is None:
            continue

        calculation_key = calculation_material_key(calculation, index)
        export_df = materials_df.copy(deep=True)
        export_df["SYSTEM"] = calculation_key
        combined_materials[calculation_key] = export_df

    session_state["combined_materials"] = combined_materials
    return combined_materials
