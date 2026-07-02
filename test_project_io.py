import json
from datetime import date, datetime
from pathlib import Path

import numpy as np

import pandas as pd
import pytest

from utils.calculation_state import MATERIALS_KEY
from utils.project_io import (
    FILE_TYPE,
    PROJECT_FILE_VERSION,
    ProjectLoadError,
    export_project_state,
    import_project_state,
    parse_project_file,
    project_filename,
)


class SessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


def test_project_filename_uses_fireboard_extension_and_timestamp():
    assert project_filename(datetime(2026, 7, 2, 9, 5)) == "fireboard_project_20260702_0905.fireboard"


def test_export_and_import_project_state_round_trips_calculations_and_material_settings():
    materials = pd.DataFrame([
        {
            "Varenr.": "123",
            "Beskrivelse": "Fireboard",
            "Total": np.float64(4.5),
            "Antal": np.int64(2),
            "Valgt": np.bool_(True),
            "Dato": date(2026, 7, 2),
        },
    ])
    source = SessionState(
        project_name="Project A",
        company="Knauf",
        prepared_by="Tester",
        description="Saved locally",
        category="H-profiler",
        profile_type="HEA",
        selected_profile="HEA 100",
        montage="Klammeløsning",
        sides=4,
        fire_time=60,
        temperature=500,
        profile_length="7,5",
        waste_percent="12",
        selected_material_variant=("2x20", "compact"),
        calculations=[
            {
                "category": "H-profiler",
                "profile": "HEA 100",
                "montage": "Klammeløsning",
                "sides": 4,
                "fire_time": 60,
                "temperature": 500,
                "apv": 123,
                "thickness": 40,
                "profile_length": "7,5",
                "waste_percent": "12",
                "selected_material_variant": ("2x20", "compact"),
                "material_build_up": pd.Series({"layer": np.int64(2), "variant": "2x20"}),
                "created_at": datetime(2026, 7, 2, 9, 5),
                "export_path": Path("projects/example.fireboard"),
                "tags": {"fire", "board"},
                MATERIALS_KEY: materials,
            }
        ],
    )

    exported = export_project_state(source)
    payload = json.loads(exported.decode("utf-8"))
    assert payload["file_type"] == FILE_TYPE
    assert payload["version"] == PROJECT_FILE_VERSION
    assert payload["current_workflow"]["selected_material_variant"] == ["2x20", "compact"]
    calculation_payload = payload["calculations"][0]
    assert calculation_payload["selected_material_variant"] == ["2x20", "compact"]
    assert calculation_payload["material_build_up"] == {"layer": 2, "variant": "2x20"}
    assert calculation_payload["created_at"] == "2026-07-02T09:05:00"
    assert calculation_payload["export_path"] == "projects/example.fireboard"
    assert sorted(calculation_payload["tags"]) == ["board", "fire"]
    assert calculation_payload[MATERIALS_KEY]["records"][0]["Antal"] == 2
    assert calculation_payload[MATERIALS_KEY]["records"][0]["Valgt"] is True
    assert calculation_payload[MATERIALS_KEY]["records"][0]["Dato"] == "2026-07-02"

    target = SessionState(language="DA", calculations=[{"profile": "old"}])
    import_project_state(target, exported)

    assert target.project_name == "Project A"
    assert target.calculations[0]["profile"] == "HEA 100"
    assert target.calculations[0]["profile_length"] == "7,5"
    assert target.selected_material_variant == ["2x20", "compact"]
    assert target.calculations[0]["material_build_up"] == {"layer": 2, "variant": "2x20"}
    expected_materials = materials.copy()
    expected_materials["Dato"] = expected_materials["Dato"].astype(str)
    pd.testing.assert_frame_equal(target.calculations[0][MATERIALS_KEY], expected_materials)
    assert target.combined_materials
    assert target.edit_index is None


def test_parse_project_file_rejects_invalid_json_without_mutation():
    with pytest.raises(ProjectLoadError, match="not valid Fireboard JSON"):
        parse_project_file(b"not-json")


def test_import_project_state_rejects_missing_marker_without_overwriting_existing_state():
    target = SessionState(project_name="Keep me", calculations=[{"profile": "existing"}])

    with pytest.raises(ProjectLoadError, match="file_type"):
        import_project_state(target, json.dumps({"version": 1, "project": {}, "calculations": []}).encode())

    assert target.project_name == "Keep me"
    assert target.calculations == [{"profile": "existing"}]
