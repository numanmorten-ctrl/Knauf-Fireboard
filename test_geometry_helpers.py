from utils.geometry_helpers import calculate_custom_profile_apv


def test_calculate_custom_profile_apv_one_side_perimeter():
    assert calculate_custom_profile_apv(120, 80, 500, 1) == 560


def test_calculate_custom_profile_apv_two_sides_perimeter():
    assert calculate_custom_profile_apv(120, 80, 500, 2) == 400


def test_calculate_custom_profile_apv_three_sides_perimeter():
    assert calculate_custom_profile_apv(120, 80, 500, 3) == 560


def test_calculate_custom_profile_apv_four_sides_perimeter():
    assert calculate_custom_profile_apv(120, 80, 500, 4) == 800


def test_direct_apv_value_still_works_without_geometry_calculation():
    direct_apv = 321
    assert direct_apv == 321


def test_calculate_custom_profile_apv_handles_missing_geometry_gracefully():
    assert calculate_custom_profile_apv(None, 80, 500, 2) is None


def test_calculate_custom_profile_apv_handles_zero_geometry_gracefully():
    assert calculate_custom_profile_apv(120, 80, 0, 2) is None


def test_calculate_custom_profile_apv_handles_negative_geometry_gracefully():
    assert calculate_custom_profile_apv(-1, 80, 500, 2) is None
