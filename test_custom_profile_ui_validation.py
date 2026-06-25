from pathlib import Path

from utils.custom_profile_validation import (
    DIRECT_APV_METHOD,
    GEOMETRY_APV_METHOD,
    should_show_direct_apv_validation,
    should_show_geometry_apv_validation,
)
from utils.geometry_helpers import calculate_custom_profile_apv
from translations import translations


CUSTOM_CATEGORY = "Andre profiler"
DIRECT_MESSAGE = "Indtast gyldig Ap/V værdi"
GEOMETRY_MESSAGE = "Indtast gyldige positive værdier for a, b og A"


def test_direct_mode_with_missing_apv_shows_only_direct_validation():
    assert should_show_direct_apv_validation(CUSTOM_CATEGORY, DIRECT_APV_METHOD, None)
    assert not should_show_geometry_apv_validation(CUSTOM_CATEGORY, DIRECT_APV_METHOD, None)



def test_geometry_mode_with_missing_or_invalid_geometry_shows_only_geometry_validation():
    calculated_apv = calculate_custom_profile_apv(None, 80, 500, 2)

    assert calculated_apv is None
    assert should_show_geometry_apv_validation(CUSTOM_CATEGORY, GEOMETRY_APV_METHOD, calculated_apv)
    assert not should_show_direct_apv_validation(CUSTOM_CATEGORY, GEOMETRY_APV_METHOD, calculated_apv)



def test_geometry_mode_never_shows_direct_apv_validation_for_invalid_geometry_values():
    invalid_geometry_values = [
        (None, 80, 500),
        (120, 0, 500),
        (120, 80, -1),
    ]

    for a, b, area in invalid_geometry_values:
        calculated_apv = calculate_custom_profile_apv(a, b, area, 2)
        assert calculated_apv is None
        assert not should_show_direct_apv_validation(
            CUSTOM_CATEGORY,
            GEOMETRY_APV_METHOD,
            calculated_apv,
        )



def test_direct_mode_never_shows_geometry_validation():
    assert not should_show_geometry_apv_validation(CUSTOM_CATEGORY, DIRECT_APV_METHOD, None)



def test_method_selector_is_not_rendered_as_streamlit_radio_group():
    app_source = Path("app.py").read_text()

    assert "st.radio" not in app_source
    assert 'key="custom_profile_method_direct"' in app_source
    assert 'key="custom_profile_method_geometry"' in app_source
    assert 't("enter_apv")' in app_source
    assert 't("calculate_apv")' in app_source
    assert 'type=(\n                    "primary"' in app_source



def test_existing_geometry_apv_calculation_still_passes():
    assert calculate_custom_profile_apv(120, 80, 500, 1) == 560
    assert calculate_custom_profile_apv(120, 80, 500, 2) == 400
    assert calculate_custom_profile_apv(120, 80, 500, 3) == 560
    assert calculate_custom_profile_apv(120, 80, 500, 4) == 800



def test_validation_message_copy_is_mode_specific_in_danish():
    da = translations["DA"]

    assert da["invalid_apv"] == DIRECT_MESSAGE
    assert da["invalid_geometry_for_apv"] == GEOMETRY_MESSAGE
    assert DIRECT_MESSAGE != GEOMETRY_MESSAGE
