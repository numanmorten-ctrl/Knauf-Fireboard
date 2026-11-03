"""Check the Ap/V limit through the production sizing flow and real tables."""

import ast
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest
import streamlit as st

from translations import translations
from utils.custom_profile_validation import (
    CUSTOM_PROFILE_CATEGORY,
    DIRECT_APV_METHOD,
    GEOMETRY_APV_METHOD,
    should_show_direct_apv_validation,
    should_show_geometry_apv_validation,
)
from utils.data_loader import clean_numeric, clean_text, load_and_clean_csv
from utils.geometry_helpers import calculate_custom_profile_apv
from utils.validation_helpers import validate_fireboard_lookup


ROOT = Path(__file__).resolve().parent
MESSAGES = {
    "DA": "Profilforholdet (Ap/V) overstiger 380 m²/m³, vælg et andet eller større profil",
    "EN": "The profile factor (Ap/V) exceeds 380 m²/m³. Select another or larger steel profile.",
}


class SessionState(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class CalculationStopped(Exception):
    """Represent Streamlit stopping before a thickness can be assigned."""


def stop():
    raise CalculationStopped()


@pytest.fixture(scope="module")
def sizing_flow():
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    helpers = {
        "load_fireboard", "get_valid_custom_profile_apv",
        "store_custom_profile_apv", "clear_calculated_custom_profile_apv",
        "calculate_and_store_custom_profile_apv_for_sides",
    }
    functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in helpers
    ]
    assert len(functions) == len(helpers)
    # Execute the actual common sizing block, including standard/custom
    # selection, localized validation, st.stop(), and the thickness lookup.
    blocks = [
        node for node in tree.body
        if isinstance(node, ast.If) and any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id == "validate_fireboard_lookup"
            for child in ast.walk(node)
        )
    ]
    assert len(blocks) == 1
    namespace = dict(
        st=st, pd=pd, clean_numeric=clean_numeric, clean_text=clean_text,
        load_and_clean_csv=load_and_clean_csv,
        calculate_custom_profile_apv=calculate_custom_profile_apv,
        GEOMETRY_APV_METHOD=GEOMETRY_APV_METHOD,
        should_show_direct_apv_validation=should_show_direct_apv_validation,
        should_show_geometry_apv_validation=should_show_geometry_apv_validation,
        validate_fireboard_lookup=validate_fireboard_lookup,
    )
    exec(compile(ast.Module(body=functions, type_ignores=[]), "app.py", "exec"), namespace)
    tables = {
        duration: namespace["load_fireboard"](ROOT / "data" / f"fireboard_{duration}.csv")
        for duration in (30, 60, 90, 120)
    }
    data = load_and_clean_csv(ROOT / "data" / "apv.csv").copy()
    data["apv"] = data["apv"].map(clean_numeric)
    code = compile(ast.Module(body=blocks, type_ignores=[]), "app.py", "exec")
    return namespace, tables, data, code


@pytest.mark.parametrize("mode", ["standard", "direct", "geometry"])
@pytest.mark.parametrize("apv", [379, 380, 381, 400, 401])
@pytest.mark.parametrize("duration", [30, 60, 90, 120])
@pytest.mark.parametrize("language", ["DA", "EN"])
def test_maximum_in_all_sizing_paths(sizing_flow, mode, apv, duration, language):
    helpers, tables, data, code = sizing_flow
    errors = []
    state = SessionState(custom_profile_name="Custom profile", custom_profile_apv=None)
    namespace = dict(
        helpers, st=SimpleNamespace(session_state=state, error=errors.append, stop=stop),
        t=translations[language].__getitem__, apv_df=data.copy(),
        fire_tables=tables, fire_time=duration, temperature=750,
        category=CUSTOM_PROFILE_CATEGORY, selected_profile=None,
        montage="Klammeløsning", sides=4,
    )
    if mode == "standard":
        records = data[data["apv"] == apv]
        if apv == 401:
            # No catalogue row has exactly 401. Use an in-memory standard
            # record for this boundary; never modify the source CSV.
            records = data[data["apv"] == 400].iloc[[0]].copy()
            records["apv"] = apv
            namespace["apv_df"] = records
        assert not records.empty
        record = records.iloc[0]
        namespace.update(
            category=record["profile_category"], selected_profile=record["profile"],
            montage=record["montage"], sides=int(record["sides"]),
        )
    elif mode == "direct":
        state.apv_method = DIRECT_APV_METHOD
        helpers["store_custom_profile_apv"](state, str(apv))
    else:
        # Four sides, A=1000 mm²: the production formula yields exactly apv.
        state.update(
            apv_method=GEOMETRY_APV_METHOD, custom_profile_a=str(apv / 2 - 1),
            custom_profile_b="1", custom_profile_A="1000",
        )

    if apv <= 380:
        exec(code, namespace)
        assert not errors
        assert namespace["apv"] == apv
        assert namespace["thickness"] == {30: 15, 60: 30, 90: 30, 120: 40}[duration]
    else:
        with pytest.raises(CalculationStopped):
            exec(code, namespace)
        assert namespace["apv"] == apv
        assert errors == [MESSAGES[language]]
        assert "thickness" not in namespace


@pytest.mark.parametrize("duration", [30, 60])
@pytest.mark.parametrize("apv", [381, 400])
def test_existing_out_of_range_table_values_cannot_bypass_limit(sizing_flow, duration, apv):
    _, tables, _, _ = sizing_flow
    table = tables[duration]
    assert pd.notna(table.loc[750, apv])
    assert validate_fireboard_lookup(table, apv, 750) == MESSAGES["DA"]


@pytest.mark.parametrize("duration,temperature,apv", [(90, 747, 379), (120, 664, 17)])
@pytest.mark.parametrize("language", ["DA", "EN"])
def test_unsupported_in_range_thickness_remains_rejected(sizing_flow, duration, temperature, apv, language):
    _, tables, _, _ = sizing_flow
    table = tables[duration]
    assert pd.isna(table.loc[temperature, apv])
    message = validate_fireboard_lookup(table, apv, temperature, translations[language].__getitem__)
    assert message is not None
    assert message != MESSAGES[language]


@pytest.mark.parametrize("duration", [30, 60, 90, 120])
def test_missing_lookup_coordinates_remain_rejected(sizing_flow, duration):
    _, tables, _, _ = sizing_flow
    table = tables[duration]
    assert validate_fireboard_lookup(table, 380, 751) is not None
    assert validate_fireboard_lookup(table.drop(columns=[380]), 380, 750) is not None
