"""Local Fireboard project save/load helpers."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from utils.calculation_state import (
    MATERIALS_KEY,
    rebuild_combined_materials,
    update_selected_calculation_material_settings,
)

FILE_TYPE = "fireboard_project"
PROJECT_FILE_VERSION = 1
PROJECT_FILE_EXTENSION = ".fireboard"
PROJECT_FILE_MIME = "application/json"

PROJECT_DETAIL_KEYS = ("project_name", "company", "prepared_by", "description")
CURRENT_WORKFLOW_KEYS = (
    "category",
    "profile_type",
    "selected_profile",
    "montage",
    "sides",
    "fire_time",
    "temperature",
    "apv_method",
    "custom_apv",
    "custom_profile_apv",
    "custom_profile_name",
    "surface_area",
    "steel_area",
    "custom_profile_a",
    "custom_profile_b",
    "custom_profile_A",
    "profile_length",
    "waste_percent",
    "selected_material_variant",
)
REQUIRED_KEYS = ("file_type", "version", "project", "calculations")


class ProjectLoadError(ValueError):
    """Raised when a Fireboard project file cannot be imported safely."""


def make_json_safe(value: Any) -> Any:
    """Return a JSON-serializable copy of common project/session values."""

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return None if pd.isna(value) else value
    if isinstance(value, pd.DataFrame):
        return [
            make_json_safe(record)
            for record in value.where(pd.notna(value), None).to_dict("records")
        ]
    if isinstance(value, pd.Series):
        series = value.where(pd.notna(value), None)
        if isinstance(series.index, pd.RangeIndex):
            return make_json_safe(series.tolist())
        return {str(key): make_json_safe(item) for key, item in series.to_dict().items()}
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if pd.isna(value) else float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(item) for item in value]

    return str(value)


def _dataframe_to_payload(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, pd.DataFrame):
        raise ProjectLoadError("Saved material data is incompatible.")
    return {
        "columns": [str(column) for column in value.columns],
        "records": make_json_safe(value),
    }


def _dataframe_from_payload(value: Any) -> pd.DataFrame | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ProjectLoadError("Saved material data is incompatible.")
    columns = value.get("columns")
    records = value.get("records")
    if not isinstance(columns, list) or not isinstance(records, list):
        raise ProjectLoadError("Saved material data is incomplete.")
    return pd.DataFrame(records, columns=columns)


def _serialize_calculation(calculation: dict[str, Any]) -> dict[str, Any]:
    serialized = deepcopy(calculation)
    if MATERIALS_KEY in serialized:
        serialized[MATERIALS_KEY] = _dataframe_to_payload(serialized[MATERIALS_KEY])
    return make_json_safe(serialized)


def _deserialize_calculation(calculation: Any) -> dict[str, Any]:
    if not isinstance(calculation, dict):
        raise ProjectLoadError("The calculations list contains an invalid item.")
    restored = deepcopy(calculation)
    if MATERIALS_KEY in restored:
        restored[MATERIALS_KEY] = _dataframe_from_payload(restored[MATERIALS_KEY])
    return restored


def project_filename(now: datetime | None = None) -> str:
    """Return the default local project filename."""

    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M")
    return f"fireboard_project_{timestamp}{PROJECT_FILE_EXTENSION}"


def export_project_state(session_state: Any) -> bytes:
    """Serialize the current Streamlit session project state to JSON bytes."""

    update_selected_calculation_material_settings(session_state)

    payload = {
        "file_type": FILE_TYPE,
        "version": PROJECT_FILE_VERSION,
        "project": {
            key: make_json_safe(session_state.get(key, ""))
            for key in PROJECT_DETAIL_KEYS
        },
        "current_workflow": {
            key: make_json_safe(session_state.get(key))
            for key in CURRENT_WORKFLOW_KEYS
            if key in session_state
        },
        "calculations": [
            _serialize_calculation(calculation)
            for calculation in session_state.get("calculations", [])
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def parse_project_file(file_bytes: bytes | str) -> dict[str, Any]:
    """Validate and parse Fireboard project JSON without mutating session state."""

    try:
        payload = json.loads(file_bytes.decode("utf-8") if isinstance(file_bytes, bytes) else file_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectLoadError("The selected file is not valid Fireboard JSON.") from exc

    if not isinstance(payload, dict):
        raise ProjectLoadError("The selected file is not a Fireboard project.")
    missing = [key for key in REQUIRED_KEYS if key not in payload]
    if missing:
        raise ProjectLoadError(f"The project file is missing required keys: {', '.join(missing)}.")
    if payload.get("file_type") != FILE_TYPE:
        raise ProjectLoadError("The selected file is not marked as a Fireboard project.")
    if payload.get("version") != PROJECT_FILE_VERSION:
        raise ProjectLoadError("This Fireboard project version is not supported.")
    if not isinstance(payload.get("project"), dict):
        raise ProjectLoadError("The project information is invalid.")
    if not isinstance(payload.get("calculations"), list):
        raise ProjectLoadError("The calculations data is invalid.")

    return {
        "project": {key: payload["project"].get(key, "") for key in PROJECT_DETAIL_KEYS},
        "current_workflow": payload.get("current_workflow") if isinstance(payload.get("current_workflow"), dict) else {},
        "calculations": [_deserialize_calculation(calc) for calc in payload["calculations"]],
    }


def import_project_state(session_state: Any, file_bytes: bytes | str) -> dict[str, Any]:
    """Load a validated Fireboard project into session state."""

    restored = parse_project_file(file_bytes)

    session_state["calculations"] = restored["calculations"]
    for key in PROJECT_DETAIL_KEYS:
        session_state[key] = restored["project"].get(key, "")
    for key in CURRENT_WORKFLOW_KEYS:
        if key in restored["current_workflow"]:
            session_state[key] = restored["current_workflow"][key]

    session_state["edit_index"] = None
    session_state["editing"] = False
    session_state["current_step"] = 0
    session_state["current_materials_signature"] = None
    session_state["current_materials_table"] = None
    session_state["project_package_cache"] = {}
    session_state["project_report_cache"] = {}
    session_state["project_material_exports_cache"] = {}
    session_state["last_updated"] = datetime.now()
    rebuild_combined_materials(session_state)
    return restored
