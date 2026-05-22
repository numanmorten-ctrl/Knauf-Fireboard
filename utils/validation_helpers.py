def validate_temperature(temperature, t):

    try:
        temperature = int(temperature)

    except:
        return t("temperature_must_be_integer")

    if temperature < 350 or temperature > 750:
        return t("temperature_must_be_between")

    return None
