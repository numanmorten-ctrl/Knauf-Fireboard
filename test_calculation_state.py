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
