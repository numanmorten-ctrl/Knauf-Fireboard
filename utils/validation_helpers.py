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
