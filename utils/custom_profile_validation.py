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


def _is_positive_number(value):
    """Return True when value can be interpreted as a positive number."""
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def should_show_geometry_apv_validation(category, apv_method, a, b=None, steel_area=None):
    """Return True only when geometry mode is selected and geometry input is invalid."""
    return (
        category == CUSTOM_PROFILE_CATEGORY
        and apv_method == GEOMETRY_APV_METHOD
        and not (
            _is_positive_number(a)
            and _is_positive_number(b)
            and _is_positive_number(steel_area)
        )
    )
