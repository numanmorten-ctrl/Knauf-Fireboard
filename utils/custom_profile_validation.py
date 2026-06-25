"""Validation helpers for custom profile Ap/V input modes."""

CUSTOM_PROFILE_CATEGORY = "Andre profiler"
DIRECT_APV_METHOD = "Direkte"
GEOMETRY_APV_METHOD = "Beregn"


def should_show_direct_apv_validation(category, apv_method, custom_profile_apv):
    """Return True only when direct custom Ap/V input is required and invalid."""
    return (
        category == CUSTOM_PROFILE_CATEGORY
        and apv_method == DIRECT_APV_METHOD
        and custom_profile_apv is None
    )


def should_show_geometry_apv_validation(category, apv_method, calculated_apv):
    """Return True only when geometry custom Ap/V calculation is selected and invalid."""
    return (
        category == CUSTOM_PROFILE_CATEGORY
        and apv_method == GEOMETRY_APV_METHOD
        and calculated_apv is None
    )
