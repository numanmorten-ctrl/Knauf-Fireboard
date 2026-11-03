import pandas as pd

from translations import translations
from utils.calculation_state import apply_default_material_settings

def validate_temperature(temperature, t):

    try:
        temperature = int(temperature)

    except:
        return t("temperature_must_be_integer")

    if temperature < 350 or temperature > 750:
        return t("temperature_must_be_between")

    return None



def validate_fireboard_lookup(
    table,
    apv,
    temperature,
    t=None
):

    if apv > 380 or apv not in table.columns:

        if t is not None:
            return t("apv_exceeds_maximum")

        return translations["DA"]["apv_exceeds_maximum"]

    if int(temperature) not in table.index:

        return "Temperaturen findes ikke"

    thickness = table.loc[
        int(temperature),
        apv
    ]

    if pd.isna(thickness):

        return (
            "Profilet kan ikke inddækkes, "
            "vælg et andet eller større profil"
        )

    return None

def reset_calculation_state(session_state):

    reset_keys = [

        "category",
        "profile_type",
        "montage",
        "sides",
        "selected_profile",
        "fire_time",
        "temperature"
    ]

    for key in reset_keys:

        session_state[key] = None

    session_state["custom_profile_name"] = ""
    session_state["custom_profile_apv"] = None
    session_state["custom_apv"] = None
    session_state["custom_profile_a"] = ""
    session_state["custom_profile_b"] = ""
    session_state["custom_profile_A"] = ""
    session_state["surface_area"] = ""
    session_state["steel_area"] = ""
    session_state["apv_method"] = "Direkte"

    session_state["show_apv_geometry_help"] = False

    session_state.editing = False

    session_state.edit_index = None

    apply_default_material_settings(session_state)

    session_state.current_step = 0
