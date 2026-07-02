import pandas as pd

from utils.calculation_state import (
    MATERIALS_KEY,
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
