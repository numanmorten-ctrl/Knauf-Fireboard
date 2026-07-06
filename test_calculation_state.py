import pandas as pd

from utils.calculation_state import (
    MATERIALS_KEY,
    MATERIAL_UI_STATE_KEY,
    append_new_calculation,
    rebuild_combined_materials,
    remember_current_materials,
    replace_selected_calculation,
)


def calculation(thickness, fire_time=30):
    return {
        "category": "H-profiler",
        "profile": "HEB 100",
        "montage": "Klammeløsning",
        "sides": 4,
        "fire_time": fire_time,
        "temperature": 450,
        "apv": 123,
        "thickness": thickness,
        "apv_method": "Direkte",
        "custom_apv": None,
        "surface_area": "",
        "steel_area": "",
    }


def materials(description):
    return pd.DataFrame(
        [
            {
                "ART.NR.": "123",
                "DB NR": "456",
                "PRODUCENT": "Knauf",
                "BESKRIVELSE": description,
                "FORBRUG PR. LBM": 1.0,
                "ENHED": "m2",
                "SAMLET MÆNGDE": 6.0,
            }
        ]
    )


def test_update_replaces_selected_calculation_and_materials_without_append():
    state = {"calculations": [], "edit_index": None, "editing": False}

    first_calc = calculation(20)
    remember_current_materials(state, first_calc, materials("Fireboard 20 mm"))
    assert append_new_calculation(state, first_calc)

    assert state["edit_index"] == 0
    assert state["editing"] is True
    updated_calc = calculation(25, fire_time=60)
    remember_current_materials(state, updated_calc, materials("Fireboard 25 mm"))

    assert replace_selected_calculation(state, updated_calc)

    assert len(state["calculations"]) == 1
    assert state["calculations"][0]["thickness"] == 25
    assert (
        state["calculations"][0][MATERIALS_KEY].iloc[0]["BESKRIVELSE"]
        == "Fireboard 25 mm"
    )
    assert state["edit_index"] == 0
    assert state["editing"] is True

    combined = state["combined_materials"]
    assert len(combined) == 1
    combined_df = next(iter(combined.values()))
    assert combined_df.iloc[0]["BESKRIVELSE"] == "Fireboard 25 mm"
    assert "Fireboard 20 mm" not in combined_df.to_string()


def test_rebuild_combined_materials_uses_current_calculations_only():
    state = {
        "calculations": [],
        "combined_materials": {"stale": materials("Fireboard 20 mm")},
    }

    current_calc = calculation(25)
    current_calc[MATERIALS_KEY] = materials("Fireboard 25 mm")
    state["calculations"].append(current_calc)

    combined = rebuild_combined_materials(state)

    assert "stale" not in combined
    assert len(combined) == 1
    combined_df = next(iter(combined.values()))
    assert combined_df.iloc[0]["BESKRIVELSE"] == "Fireboard 25 mm"
    assert "SYSTEM" in combined_df.columns


def test_append_new_calculation_still_appends_distinct_calculations():
    state = {"calculations": [], "edit_index": None, "editing": False}

    first_calc = calculation(20)
    second_calc = calculation(25)
    remember_current_materials(state, first_calc, materials("Fireboard 20 mm"))
    assert append_new_calculation(state, first_calc)
    assert state["edit_index"] == 0
    assert state["editing"] is True

    state["edit_index"] = None
    state["editing"] = False
    remember_current_materials(state, second_calc, materials("Fireboard 25 mm"))
    assert append_new_calculation(state, second_calc)

    assert len(state["calculations"]) == 2
    assert len(state["combined_materials"]) == 2
    assert state["edit_index"] == 1
    assert state["editing"] is True


def test_newly_appended_calculation_enters_update_mode_immediately():
    state = {"calculations": [], "edit_index": None, "editing": False}

    first_calc = calculation(20)
    second_calc = calculation(25)
    remember_current_materials(state, first_calc, materials("Fireboard 20 mm"))
    assert append_new_calculation(state, first_calc)

    state["edit_index"] = None
    state["editing"] = False
    remember_current_materials(state, second_calc, materials("Fireboard 25 mm"))
    assert append_new_calculation(state, second_calc)

    assert state["edit_index"] == 1
    assert state["editing"] is True

    updated_second_calc = calculation(30, fire_time=60)
    remember_current_materials(
        state, updated_second_calc, materials("Fireboard 30 mm")
    )
    assert replace_selected_calculation(state, updated_second_calc)

    assert len(state["calculations"]) == 2
    assert state["calculations"][0]["thickness"] == 20
    assert state["calculations"][1]["thickness"] == 30
    assert state["calculations"][1][MATERIALS_KEY].iloc[0]["BESKRIVELSE"] == (
        "Fireboard 30 mm"
    )
    assert state["edit_index"] == 1
    assert state["editing"] is True


def test_material_settings_are_saved_per_calculation_profile_length():
    state = {"calculations": [], "edit_index": None, "editing": False}

    first_calc = calculation(20)
    state["profile_length"] = "5,0"
    remember_current_materials(state, first_calc, materials("5m list"))
    assert append_new_calculation(state, first_calc)

    state["edit_index"] = None
    state["editing"] = False
    second_calc = calculation(20, fire_time=60)
    state["profile_length"] = "8,0"
    remember_current_materials(state, second_calc, materials("8m list"))
    assert append_new_calculation(state, second_calc)

    assert state["calculations"][0]["profile_length"] == "5,0"
    assert state["calculations"][1]["profile_length"] == "8,0"
    assert state["calculations"][0][MATERIAL_UI_STATE_KEY]["profile_length"] == "5,0"
    assert state["calculations"][1][MATERIAL_UI_STATE_KEY]["profile_length"] == "8,0"


def test_material_settings_are_saved_per_calculation_waste_percent():
    state = {"calculations": [], "edit_index": None, "editing": False}

    first_calc = calculation(20)
    state["waste_percent"] = "5"
    remember_current_materials(state, first_calc, materials("5 percent waste"))
    assert append_new_calculation(state, first_calc)

    state["edit_index"] = None
    state["editing"] = False
    second_calc = calculation(25)
    state["waste_percent"] = "15"
    remember_current_materials(state, second_calc, materials("15 percent waste"))
    assert append_new_calculation(state, second_calc)

    assert state["calculations"][0]["waste_percent"] == "5"
    assert state["calculations"][1]["waste_percent"] == "15"
    assert state["calculations"][0][MATERIAL_UI_STATE_KEY]["waste_percent"] == "5"
    assert state["calculations"][1][MATERIAL_UI_STATE_KEY]["waste_percent"] == "15"


def test_material_settings_are_saved_and_restored_per_selected_layer_build_up():
    from utils.calculation_state import restore_calculation_material_settings

    state = {"calculations": [], "edit_index": None, "editing": False}

    first_calc = calculation(40)
    state["selected_material_variant"] = "2x20"
    remember_current_materials(state, first_calc, materials("2x20 list"))
    assert append_new_calculation(state, first_calc)

    state["edit_index"] = None
    state["editing"] = False
    second_calc = calculation(40, fire_time=60)
    state["selected_material_variant"] = "15+25"
    remember_current_materials(state, second_calc, materials("15+25 list"))
    assert append_new_calculation(state, second_calc)

    restore_calculation_material_settings(state, state["calculations"][0])
    assert state["selected_material_variant"] == "2x20"
    assert state["profile_length"] == "6,0"
    assert state["waste_percent"] == "10"

    restore_calculation_material_settings(state, state["calculations"][1])
    assert state["selected_material_variant"] == "15+25"


def test_switching_calculations_restores_saved_profile_lengths_without_defaults():
    from utils.calculation_state import (
        restore_calculation_material_settings,
        update_selected_calculation_material_settings,
    )

    state = {"calculations": [], "edit_index": None, "editing": False}

    first_calc = calculation(20)
    state["profile_length"] = "5"
    remember_current_materials(state, first_calc, materials("5m list"))
    assert append_new_calculation(state, first_calc)

    state["edit_index"] = None
    state["editing"] = False
    second_calc = calculation(20, fire_time=60)
    state["profile_length"] = "8"
    remember_current_materials(state, second_calc, materials("8m list"))
    assert append_new_calculation(state, second_calc)

    restore_calculation_material_settings(state, state["calculations"][0])
    state["edit_index"] = 0
    assert state["profile_length"] == "5"
    assert state["profile_length"] != "6,0"

    update_selected_calculation_material_settings(state)
    restore_calculation_material_settings(state, state["calculations"][1])
    state["edit_index"] = 1
    assert state["profile_length"] == "8"
    assert state["profile_length"] != "6,0"

    update_selected_calculation_material_settings(state)
    restore_calculation_material_settings(state, state["calculations"][0])
    state["edit_index"] = 0
    assert state["profile_length"] == "5"


def test_active_calculation_material_settings_update_before_switching_away():
    from utils.calculation_state import (
        restore_calculation_material_settings,
        update_selected_calculation_material_settings,
    )

    state = {"calculations": [], "edit_index": None, "editing": False}

    first_calc = calculation(20)
    state["profile_length"] = "5"
    state["waste_percent"] = "7"
    state["selected_material_variant"] = "2x20"
    remember_current_materials(state, first_calc, materials("A list"))
    assert append_new_calculation(state, first_calc)

    state["edit_index"] = None
    state["editing"] = False
    second_calc = calculation(20, fire_time=60)
    state["profile_length"] = "8"
    state["waste_percent"] = "12"
    state["selected_material_variant"] = "15+25"
    remember_current_materials(state, second_calc, materials("B list"))
    assert append_new_calculation(state, second_calc)

    restore_calculation_material_settings(state, state["calculations"][0])
    state["edit_index"] = 0
    state["profile_length"] = "5,5"
    state["waste_percent"] = "9"
    state["selected_material_variant"] = "updated-build-up"

    assert update_selected_calculation_material_settings(state)

    restore_calculation_material_settings(state, state["calculations"][1])
    state["edit_index"] = 1
    assert state["profile_length"] == "8"

    restore_calculation_material_settings(state, state["calculations"][0])
    state["edit_index"] = 0
    assert state["profile_length"] == "5,5"
    assert state["waste_percent"] == "9"
    assert state["selected_material_variant"] == "updated-build-up"


def test_multiple_build_up_options_default_to_first_valid_variant():
    from utils.calculation_state import resolve_material_variant

    assert resolve_material_variant(None, ["A", "B"]) == "A"
    assert resolve_material_variant("missing", ["A", "B"]) == "A"


def test_existing_valid_build_up_survives_update_resolution():
    from utils.calculation_state import resolve_material_variant

    assert resolve_material_variant("B", ["A", "B"]) == "B"


def test_invalid_non_existing_build_up_is_not_kept_or_created():
    from utils.calculation_state import ensure_session_material_variant

    state = {"selected_material_variant": "45 mm Fireboard"}

    selected = ensure_session_material_variant(state, ["A", "B"])

    assert selected == "A"
    assert state["selected_material_variant"] == "A"
    assert state["selected_material_variant"] != "45 mm Fireboard"


def test_switching_a_b_a_and_b_a_b_restores_per_calculation_material_ui_state():
    from utils.calculation_state import (
        restore_calculation_material_settings,
        update_selected_calculation_material_settings,
    )

    state = {"calculations": [], "edit_index": None, "editing": False}

    first_calc = calculation(40, fire_time=30)
    state["profile_length"] = "5"
    state["waste_percent"] = "10"
    state["selected_material_variant"] = "2x20"
    remember_current_materials(state, first_calc, materials("A list"))
    assert append_new_calculation(state, first_calc)

    state["edit_index"] = None
    state["editing"] = False
    second_calc = calculation(40, fire_time=60)
    state["profile_length"] = "8"
    state["waste_percent"] = "15"
    state["selected_material_variant"] = "15+25"
    remember_current_materials(state, second_calc, materials("B list"))
    assert append_new_calculation(state, second_calc)

    restore_calculation_material_settings(state, state["calculations"][0])
    state["edit_index"] = 0
    assert (state["profile_length"], state["waste_percent"], state["selected_material_variant"]) == ("5", "10", "2x20")

    assert update_selected_calculation_material_settings(state)
    restore_calculation_material_settings(state, state["calculations"][1])
    state["edit_index"] = 1
    assert (state["profile_length"], state["waste_percent"], state["selected_material_variant"]) == ("8", "15", "15+25")

    assert update_selected_calculation_material_settings(state)
    restore_calculation_material_settings(state, state["calculations"][0])
    state["edit_index"] = 0
    assert (state["profile_length"], state["waste_percent"], state["selected_material_variant"]) == ("5", "10", "2x20")

    assert update_selected_calculation_material_settings(state)
    restore_calculation_material_settings(state, state["calculations"][1])
    state["edit_index"] = 1
    assert (state["profile_length"], state["waste_percent"], state["selected_material_variant"]) == ("8", "15", "15+25")


def test_material_ui_state_wins_over_stale_legacy_values_when_switching_profiles():
    from utils.calculation_state import restore_calculation_material_settings

    heb100 = calculation(40, fire_time=30)
    heb100["profile"] = "HEB100"
    heb100.update(
        {
            "profile_length": "6,0",
            "waste_percent": "10",
            "selected_material_variant": "stale-default-build-up",
            MATERIAL_UI_STATE_KEY: {
                "profile_length": "12",
                "waste_percent": "12",
                "selected_material_variant": "upper-build-up",
            },
        }
    )

    ipe200 = calculation(40, fire_time=60)
    ipe200["profile"] = "IPE200"
    ipe200.update(
        {
            "profile_length": "6,0",
            "waste_percent": "10",
            "selected_material_variant": "stale-default-build-up",
            MATERIAL_UI_STATE_KEY: {
                "profile_length": "4",
                "waste_percent": "4",
                "selected_material_variant": "lower-non-default-build-up",
            },
        }
    )

    state = {"calculations": [heb100, ipe200], "edit_index": 0, "editing": True}

    restore_calculation_material_settings(state, state["calculations"][0])
    assert (
        state["profile_length"],
        state["waste_percent"],
        state["selected_material_variant"],
    ) == ("12", "12", "upper-build-up")

    state["edit_index"] = 1
    restore_calculation_material_settings(state, state["calculations"][1])
    assert (
        state["profile_length"],
        state["waste_percent"],
        state["selected_material_variant"],
    ) == ("4", "4", "lower-non-default-build-up")

    state["edit_index"] = 0
    restore_calculation_material_settings(state, state["calculations"][0])
    assert (state["profile_length"], state["waste_percent"]) == ("12", "12")

    state["edit_index"] = 1
    restore_calculation_material_settings(state, state["calculations"][1])
    assert (
        state["profile_length"],
        state["waste_percent"],
        state["selected_material_variant"],
    ) == ("4", "4", "lower-non-default-build-up")


def test_missing_or_invalid_restored_build_up_uses_existing_first_valid_resolution():
    from utils.calculation_state import (
        ensure_session_material_variant,
        restore_calculation_material_settings,
    )

    state = {}
    restore_calculation_material_settings(state, {"material_ui_state": {"selected_material_variant": "missing"}})
    assert ensure_session_material_variant(state, ["A", "B"]) == "A"
    assert state["selected_material_variant"] == "A"

    restore_calculation_material_settings(state, {"material_ui_state": {}})
    assert ensure_session_material_variant(state, ["A", "B"]) == "A"
    assert state["selected_material_variant"] == "A"
