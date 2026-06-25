def validate_temperature(temperature, t):

    try:
        temperature = int(temperature)

    except:
        return t("temperature_must_be_integer")

    if temperature < 350 or temperature > 750:
        return t("temperature_must_be_between")

    return None

import pandas as pd


def validate_fireboard_lookup(
    table,
    apv,
    temperature
):

    if apv not in table.columns:

        return (
            "Profilforholdet (Ap/V) overstiger "
            "380 m²/m³, vælg et andet eller større profil"
        )

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


def should_show_invalid_custom_apv_message(
    category,
    apv_method,
    custom_profile_apv
):

    return (
        category == "Andre profiler"
        and apv_method == "Direkte"
        and custom_profile_apv is None
    )


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

    session_state.editing = False

    session_state.edit_index = None

    session_state.current_step = 0
