"""Exercise the actual sidebar/reset actions without launching the full UI."""

import ast
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from utils.calculation_state import (
    replace_selected_calculation,
    restore_calculation_material_settings,
    update_selected_calculation_material_settings,
)
from utils.custom_profile_validation import (
    CUSTOM_PROFILE_CATEGORY,
    DIRECT_APV_METHOD,
    GEOMETRY_APV_METHOD,
)
from utils.data_loader import clean_numeric
from utils.geometry_helpers import calculate_custom_profile_apv
from utils.project_io import export_project_state, import_project_state
from utils.validation_helpers import reset_calculation_state


class SessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


class Rerun(Exception):
    """Stop an extracted UI action at its production rerun boundary."""


def rerun():
    raise Rerun()


def custom_calculation(name, apv=150, geometry=None, sides=4):
    a, b, area = geometry or ("", "", "")
    if geometry:
        apv = calculate_custom_profile_apv(a, b, area, sides)
    return dict(
        category=CUSTOM_PROFILE_CATEGORY, profile=name,
        montage="Klammeløsning", sides=sides, fire_time=60,
        temperature=450, apv=apv, thickness=25,
        apv_method=GEOMETRY_APV_METHOD if geometry else DIRECT_APV_METHOD,
        custom_profile_apv=apv, custom_apv=apv,
        custom_profile_a=a, custom_profile_b=b, custom_profile_A=area,
        surface_area=str(apv * float(area) / 1000) if geometry else "",
        steel_area=area, profile_length="6,0", waste_percent="10",
        selected_material_variant=None,
    )


def project_state(calculations):
    return SessionState(
        calculations=deepcopy(calculations), edit_index=None, editing=False,
        custom_profile_name="Previous draft", language="DA",
        project_name="Handover", company="Company", prepared_by="Designer",
        description="Keep project metadata", current_step=3,
        show_apv_geometry_help=True,
    )


@pytest.fixture(scope="module")
def app_actions():
    tree = ast.parse(Path("app.py").read_text(encoding="utf-8"))

    def button_key(node):
        if not isinstance(node, ast.If) or not isinstance(node.test, ast.Call):
            return None
        return next((kw.value for kw in node.test.keywords if kw.arg == "key"), None)

    sidebar = [
        node for node in ast.walk(tree)
        if isinstance(button_key(node), ast.JoinedStr)
        and isinstance(button_key(node).values[0], ast.Constant)
        and button_key(node).values[0].value == "sidebar_calc_"
    ]
    assert len(sidebar) == 1
    new_actions = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Call)
        and isinstance(node.test.func, ast.Attribute)
        and node.test.func.attr == "button"
        and node.test.args
        and isinstance(node.test.args[0], ast.Call)
        and isinstance(node.test.args[0].func, ast.Name)
        and node.test.args[0].func.id == "t"
        and ast.literal_eval(node.test.args[0].args[0]) == "new_calculation"
    ]
    assert len(new_actions) == 2

    def assignment(name):
        return [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
        ]

    calculation_data, = assignment("calculation_data")
    custom_profile_name, = [
        node for node in assignment("selected_profile")
        if isinstance(node.value, ast.IfExp)
        and isinstance(node.value.body, ast.Attribute)
        and node.value.body.attr == "custom_profile_name"
    ]
    helpers = [
        node for node in tree.body if isinstance(node, ast.FunctionDef)
        and node.name in {
            "get_valid_custom_profile_apv", "clear_calculated_custom_profile_apv",
            "store_custom_profile_apv", "calculate_and_store_custom_profile_apv_for_sides",
        }
    ]

    def compile_nodes(nodes):
        return compile(ast.Module(body=nodes, type_ignores=[]), "app.py", "exec")

    return dict(
        sidebar=compile_nodes(sidebar[0].body),
        new=[compile_nodes(node.body) for node in sorted(new_actions, key=lambda n: n.lineno)],
        helpers=compile_nodes(helpers),
        calculation=compile_nodes([custom_profile_name, calculation_data]),
    )


def action_namespace(state, app_actions):
    namespace = dict(
        st=SimpleNamespace(session_state=state, rerun=rerun),
        hide_apv_geometry_help=lambda: state.update(show_apv_geometry_help=False),
        clean_numeric=clean_numeric,
        calculate_custom_profile_apv=calculate_custom_profile_apv,
        update_selected_calculation_material_settings=update_selected_calculation_material_settings,
        restore_calculation_material_settings=restore_calculation_material_settings,
        reset_calculation_state=reset_calculation_state,
        t=lambda key: "Special profile" if key == "special_profile" else key,
    )
    exec(app_actions["helpers"], namespace)
    return namespace


def select(state, index, app_actions):
    namespace = action_namespace(state, app_actions)
    namespace.update(calc=state.calculations[index], idx=index)
    with pytest.raises(Rerun):
        exec(app_actions["sidebar"], namespace)
    return namespace


def assert_restored(state, expected, index):
    assert state.custom_profile_name == expected["profile"]
    assert state.selected_profile == expected["profile"]
    for field in (
        "apv_method", "custom_profile_apv", "custom_apv",
        "custom_profile_a", "custom_profile_b", "custom_profile_A",
        "surface_area", "steel_area", "sides", "montage", "fire_time", "temperature",
    ):
        assert state[field] == expected[field], field
    assert state.edit_index == index
    assert state.editing is True
    assert state.current_step == 0


@pytest.mark.parametrize("mode", ["direct", "geometry", "mixed"])
def test_switching_custom_calculations_restores_their_own_inputs(app_actions, mode):
    calculations = [
        custom_calculation("Custom A", apv=111,
                           geometry=("100", "50", "2000") if mode == "geometry" else None),
        custom_calculation("Custom B", apv=222, sides=3,
                           geometry=("120", "80", "2500") if mode != "direct" else None),
    ]
    state = project_state(calculations)
    for index in (1, 0, 1, 0):
        namespace = select(state, index, app_actions)
        assert_restored(state, calculations[index], index)
        if state.apv_method == GEOMETRY_APV_METHOD:
            namespace["clear_calculated_custom_profile_apv"](state)
            result = namespace["calculate_and_store_custom_profile_apv_for_sides"](state, state.sides)
            assert result == calculations[index]["apv"]


@pytest.mark.parametrize("geometry", [None, ("100", "50", "2000")])
def test_edit_and_update_replaces_only_selected_custom_calculation(app_actions, geometry):
    calculations = [custom_calculation("A", geometry=geometry), custom_calculation("B", apv=222)]
    state = project_state(calculations)
    namespace = select(state, 0, app_actions)
    state.custom_profile_name = "A edited"
    if geometry:
        state.custom_profile_b = "60"
        apv = namespace["calculate_and_store_custom_profile_apv_for_sides"](state, state.sides)
    else:
        apv = namespace["store_custom_profile_apv"](state, 175)
    namespace.update({key: state[key] for key in ("category", "montage", "sides", "fire_time", "temperature")})
    namespace.update(apv=apv, thickness=25)
    exec(app_actions["calculation"], namespace)
    assert replace_selected_calculation(state, namespace["calculation_data"])
    assert len(state.calculations) == 2
    assert state.calculations[1] == calculations[1]
    assert state.calculations[0]["profile"] == "A edited"
    assert state.calculations[0]["apv"] == apv
    select(state, 1, app_actions)
    select(state, 0, app_actions)
    assert_restored(state, state.calculations[0], 0)


@pytest.mark.parametrize("action_index", [0, 1], ids=["header", "sidebar"])
@pytest.mark.parametrize("geometry", [None, ("100", "50", "2000")])
def test_new_calculation_clears_custom_inputs_and_preserves_project(app_actions, action_index, geometry):
    state = project_state([custom_calculation("Saved A", geometry=geometry), custom_calculation("Saved B")])
    namespace = select(state, 0, app_actions)
    saved = deepcopy(state.calculations)
    metadata = {key: state[key] for key in ("project_name", "company", "prepared_by", "description")}
    # Populate inactive inputs too: reset must clear the entire custom draft.
    state.update(custom_profile_a="100", custom_profile_b="50", custom_profile_A="2000",
                 surface_area="300", steel_area="2000", show_apv_geometry_help=True)
    with pytest.raises(Rerun):
        exec(app_actions["new"][action_index], namespace)
    assert state.custom_profile_name == ""
    assert state.custom_profile_apv is None
    assert state.custom_apv is None
    for field in ("custom_profile_a", "custom_profile_b", "custom_profile_A", "surface_area", "steel_area"):
        assert state[field] == "", field
    assert state.apv_method == DIRECT_APV_METHOD
    assert state.show_apv_geometry_help is False
    assert state.edit_index is None
    assert state.editing is False
    assert state.current_step == 0
    assert state.calculations == saved
    assert {key: state[key] for key in metadata} == metadata
    select(state, 0, app_actions)
    assert_restored(state, saved[0], 0)


def test_project_file_roundtrip_restores_multiple_custom_calculations(app_actions):
    calculations = [
        custom_calculation("Direct A", apv=111),
        custom_calculation("Geometry B", geometry=("100", "50", "2000")),
        custom_calculation("Direct C", apv=222),
    ]
    source = project_state(calculations)
    select(source, 1, app_actions)
    target = project_state([])
    import_project_state(target, export_project_state(source))
    assert target.calculations == source.calculations
    for index in (2, 0, 1):
        select(target, index, app_actions)
        assert_restored(target, calculations[index], index)


@pytest.mark.parametrize("category,profile,family", [("H-profiler", "HEB100", "HEB"), ("I-profiler", "IPE120", "IPE")])
def test_standard_profile_selection_remains_unchanged(app_actions, category, profile, family):
    calculation = custom_calculation(profile)
    calculation.update(category=category)
    state = project_state([calculation])
    select(state, 0, app_actions)
    assert state.custom_profile_name == "Previous draft"
    assert state.selected_profile == profile
    assert state.category == category
    assert state.profile_type == family
    for field in ("montage", "sides", "fire_time", "temperature"):
        assert state[field] == calculation[field]
    assert state.edit_index == 0
    assert state.editing is True


def test_legacy_direct_apv_alias_still_restores(app_actions):
    calculation = custom_calculation("Legacy", apv=175)
    del calculation["custom_profile_apv"]
    state = project_state([calculation])
    select(state, 0, app_actions)
    assert state.custom_profile_name == "Legacy"
    assert state.custom_profile_apv == state.custom_apv == 175
