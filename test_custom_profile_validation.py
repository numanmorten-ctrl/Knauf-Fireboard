from utils.validation_helpers import should_show_invalid_custom_apv_message


def test_invalid_custom_apv_message_shown_for_direct_entry_without_value():
    assert should_show_invalid_custom_apv_message(
        "Andre profiler",
        "Direkte",
        None
    )


def test_invalid_custom_apv_message_hidden_for_geometry_method_before_calculation():
    assert not should_show_invalid_custom_apv_message(
        "Andre profiler",
        "Beregn",
        None
    )


def test_invalid_custom_apv_message_hidden_for_direct_entry_with_value():
    assert not should_show_invalid_custom_apv_message(
        "Andre profiler",
        "Direkte",
        321
    )


def test_invalid_custom_apv_message_hidden_for_standard_profiles():
    assert not should_show_invalid_custom_apv_message(
        "H-profiler",
        "Direkte",
        None
    )
