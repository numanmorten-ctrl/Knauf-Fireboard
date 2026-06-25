import pytest

from utils.geometry_helpers import calculate_custom_profile_apv


def test_calculate_custom_profile_apv_uses_a_b_and_area():
    assert calculate_custom_profile_apv(120, 80, 500) == 400


def test_calculate_custom_profile_apv_rejects_zero_area():
    with pytest.raises(ValueError):
        calculate_custom_profile_apv(120, 80, 0)


def test_calculate_custom_profile_apv_rejects_negative_geometry():
    with pytest.raises(ValueError):
        calculate_custom_profile_apv(-1, 80, 500)
