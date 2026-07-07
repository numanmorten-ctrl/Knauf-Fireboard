"""Helpers for storing calculations and their material lists in session state."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable

import pandas as pd


MATERIALS_KEY = "materials_table"
PENDING_MATERIALS_KEY = "current_materials_table"
PENDING_SIGNATURE_KEY = "current_materials_signature"
MATERIAL_SETTING_KEYS = (
    "profile_length",
    "waste_percent",
    "selected_material_variant",
)
MATERIAL_SETTING_DEFAULTS = {
    "profile_length": "6,0",
    "waste_percent": "10",
    "selected_material_variant": None,
}


def coerce_available_material_variants(variants: Iterable[Any]) -> list[Any]:
    """Return non-empty material build-up variants preserving result order."""

    available_variants: list[Any] = []
    for variant in variants:
        if variant is None:
            continue
        try:
            if pd.isna(variant):
                continue
        except (TypeError, ValueError):
            pass
        if variant not in available_variants:
            available_variants.append(variant)
    return available_variants


def resolve_material_variant(saved_variant: Any, available_variants: Iterable[Any]) -> Any:
    """Return a valid saved variant, or the first valid result variant.

    Material build-up selections must always come from the calculated result
    data.  This prevents stale/default UI state from inventing a non-existing
    build-up such as a single board matching the total thickness.
    """

    variants = coerce_available_material_variants(available_variants)
    if not variants:
        return None
    if saved_variant in variants:
        return saved_variant
    return variants[0]


def ensure_session_material_variant(session_state: Any, available_variants: Iterable[Any]) -> Any:
    """Store and return the valid material variant for the current result."""

    selected_variant = resolve_material_variant(
        session_state.get("selected_material_variant"),
        available_variants,
    )
    session_state["selected_material_variant"] = deepcopy(selected_variant)
    return selected_variant


def material_settings_from_session(session_state: Any) -> dict[str, Any]:
    """Return material-list inputs from session state with UI defaults."""

    return {
        key: deepcopy(session_state.get(key, MATERIAL_SETTING_DEFAULTS[key]))
        for key in MATERIAL_SETTING_KEYS
    }


def attach_material_settings(
    session_state: Any,
    calculation: dict[str, Any],
) -> dict[str, Any]:
    """Return a calculation copy with current material-list input settings."""

    saved_calculation = deepcopy(calculation)
    saved_calculation.update(material_settings_from_session(session_state))
    return saved_calculation


def restore_calculation_material_settings(
    session_state: Any,
    calculation: dict[str, Any],
) -> None:
    """Restore saved material-list inputs for the selected calculation.

    Defaults are only used for older calculations that do not yet carry saved
    material settings. Streamlit widgets with these keys read from
    ``session_state`` during reruns, so this must happen before the widgets are
    rendered.
    """

    for key in MATERIAL_SETTING_KEYS:
        session_state[key] = deepcopy(
            calculation.get(key, MATERIAL_SETTING_DEFAULTS[key])
        )


def apply_default_material_settings(session_state: Any) -> None:
    """Apply material-list defaults for a brand-new calculation draft."""

    for key in MATERIAL_SETTING_KEYS:
        session_state[key] = deepcopy(MATERIAL_SETTING_DEFAULTS[key])


def update_selected_calculation_material_settings(session_state: Any) -> bool:
    """Persist current material-list widget values to the active calculation."""

    edit_index = session_state.get("edit_index")
    calculations = session_state.get("calculations", [])

    if edit_index is None or not 0 <= edit_index < len(calculations):
        return False

    calculations[edit_index].update(material_settings_from_session(session_state))
    return True



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
        calculation.get("custom_profile_apv"),
        calculation.get("surface_area"),
        calculation.get("steel_area"),
        calculation.get("custom_profile_a"),
        calculation.get("custom_profile_b"),
        calculation.get("custom_profile_A"),
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

    saved_calculation = attach_material_settings(session_state, calculation)

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

    calculations = session_state.setdefault("calculations", [])
    calculations.append(saved_calculation)
    session_state["edit_index"] = len(calculations) - 1
    session_state["editing"] = True
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
