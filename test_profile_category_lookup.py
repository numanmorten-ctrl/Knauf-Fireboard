"""Exercise the production lookup expressions against the repository CSVs."""

import ast
from pathlib import Path

import pandas as pd
import pytest
import streamlit as st

from utils.data_loader import clean_numeric, clean_text, load_and_clean_csv
from utils.validation_helpers import validate_fireboard_lookup


ROOT = Path(__file__).resolve().parent
CLAMP = "Klammeløsning"
BEAM = "Bjælkeprofil eller PHL profil"
HEAVY = "Cirkulære rør svære"
MEDIUM = "Cirkulære rør middelsvære"
COLD_SQUARE = "Kvadratiske rør koldvalsede"
COLD_RECTANGLE = "Rektangulære rør koldvalsede"
KEY_COLUMNS = ["profile_category", "profile", "montage", "sides"]
CASES = [
    (HEAVY, "100 mm", CLAMP, 4, 130),
    (MEDIUM, "100 mm", CLAMP, 4, 154),
    (COLD_SQUARE, "100x100x4 mm", BEAM, 3, 242),
    (COLD_RECTANGLE, "180x100x5 mm", BEAM, 4, 258),
    ("H-profiler", "HEB100", CLAMP, 3, 116),
    ("I-profiler", "IPE120", CLAMP, 3, 231),
]


@pytest.fixture(scope="module")
def app_tree():
    return ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def apv_data():
    data = load_and_clean_csv(ROOT / "data" / "apv.csv").copy()
    for column in ["sides", "apv"]:
        data[column] = data[column].map(clean_numeric)
    return data


@pytest.fixture(scope="module", params=["row", "amount_row"], ids=["apv", "materials"])
def lookup(request, app_tree):
    # Compile the actual app filters, without launching its UI or duplicating
    # the predicates in test code. Locate by syntax, not source line numbers.
    target_name = request.param
    assignments = [
        node for node in ast.walk(app_tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == target_name for t in node.targets)
        and isinstance(node.value, ast.Subscript)
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "apv_df"
    ]
    assert len(assignments) == 1
    code = compile(ast.Module(body=assignments, type_ignores=[]), str(ROOT / "app.py"), "exec")

    def run(data, category, profile, montage, sides):
        namespace = dict(
            apv_df=data, category=category, selected_profile=profile,
            montage=montage, sides=sides,
            clean_text=clean_text, clean_numeric=clean_numeric,
        )
        exec(code, namespace)
        return namespace[target_name]

    return run


@pytest.mark.parametrize("category,profile,montage,sides,expected_apv", CASES)
def test_category_specific_examples(lookup, apv_data, category, profile, montage, sides, expected_apv):
    result = lookup(apv_data, category, profile, montage, sides)
    assert len(result) == 1
    assert result.iloc[0]["profile_category"] == category
    assert result.iloc[0]["apv"] == expected_apv


def test_all_repository_configurations_resolve_their_own_record(lookup, apv_data):
    assert len(apv_data) == 3050
    for index, expected in apv_data.iterrows():
        result = lookup(apv_data, *(expected[column] for column in KEY_COLUMNS))
        assert result.index.tolist() == [index], tuple(expected[KEY_COLUMNS])
        # Compare the entire row, including all five consumption rates. Their
        # current values coincide across categories, so also assert identity.
        pd.testing.assert_series_equal(result.iloc[0], expected)


def test_no_duplicate_four_field_keys(apv_data):
    assert not apv_data.duplicated(KEY_COLUMNS).any()


@pytest.mark.parametrize("order", ["reversed", "shuffled"])
def test_lookup_is_independent_of_csv_order(lookup, apv_data, order):
    reordered = (
        apv_data.iloc[::-1]
        if order == "reversed"
        else apv_data.sample(frac=1, random_state=42)
    ).reset_index(drop=True)
    for category, profile, montage, sides, expected_apv in CASES:
        result = lookup(reordered, category, profile, montage, sides)
        assert len(result) == 1
        assert result.iloc[0]["profile_category"] == category
        assert result.iloc[0]["apv"] == expected_apv
        original = lookup(apv_data, category, profile, montage, sides)
        pd.testing.assert_series_equal(result.iloc[0], original.iloc[0], check_names=False)


@pytest.mark.parametrize("category,profile,montage,sides", [
    (HEAVY, "100 mm", BEAM, 4),
    (HEAVY, "100 mm", CLAMP, 1),
    (HEAVY, "100 mm", CLAMP, 2),
    (HEAVY, "100 mm", CLAMP, 3),
    ("H-profiler", "100 mm", CLAMP, 4),
    (COLD_SQUARE, "nonexistent profile", CLAMP, 4),
])
def test_unsupported_combinations_do_not_fall_back(lookup, apv_data, category, profile, montage, sides):
    assert lookup(apv_data, category, profile, montage, sides).empty


def test_lookup_preserves_whitespace_normalization(lookup, apv_data):
    result = lookup(apv_data, f" {HEAVY} ", " 100 mm ", f" {CLAMP} ", "4")
    assert len(result) == 1
    assert result.iloc[0]["apv"] == 130


@pytest.fixture(scope="module")
def fire_tables(app_tree):
    loader = next(
        node for node in app_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "load_fireboard"
    )
    namespace = dict(
        st=st, pd=pd, load_and_clean_csv=load_and_clean_csv,
        clean_text=clean_text, clean_numeric=clean_numeric,
    )
    exec(compile(ast.Module(body=[loader], type_ignores=[]), str(ROOT / "app.py"), "exec"), namespace)
    return {
        duration: namespace["load_fireboard"](ROOT / "data" / f"fireboard_{duration}.csv")
        for duration in [60, 90, 120]
    }


@pytest.mark.parametrize("category,profile,montage,sides,duration,temperature,expected_mm", [
    (COLD_SQUARE, "100x100x4 mm", BEAM, 3, 60, 750, 20),
    (COLD_RECTANGLE, "100x60x5 mm", BEAM, 3, 90, 550, 35),
    (COLD_RECTANGLE, "180x100x5 mm", BEAM, 4, 120, 750, 40),
    (HEAVY, "100 mm", CLAMP, 4, 60, 350, 25),
])
def test_category_specific_thickness(lookup, apv_data, fire_tables, category, profile, montage,
                                     sides, duration, temperature, expected_mm):
    result = lookup(apv_data, category, profile, montage, sides)
    assert len(result) == 1
    apv = int(result.iloc[0]["apv"])
    table = fire_tables[duration]
    assert validate_fireboard_lookup(table, apv, temperature) is None
    assert table.loc[temperature, apv] == expected_mm
