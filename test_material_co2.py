import ast
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from translations import translations
from utils import material_helpers as mh
from utils.data_loader import clean_numeric, clean_text, load_and_clean_csv


ROOT = Path(__file__).resolve().parent


@pytest.fixture
def material_data(monkeypatch):
    def read_csv(filename):
        return pd.read_csv(ROOT / "data" / filename, sep=";")

    materials = read_csv("materials.csv")
    by_art, by_db, by_description = {}, {}, {}
    # Match the application's material lookup construction.
    for row in materials.to_dict("records"):
        art = str(row.get("ART.NR.", "") or "").strip()
        db = str(row.get("DB_NR.", "") or "").strip()
        description = str(row.get("BESKRIVELSE_DK", "") or "").strip().lower()
        if art:
            by_art[art] = row
        if db:
            by_db[db] = row
        if description:
            by_description.setdefault(description, row)

    apv = load_and_clean_csv(ROOT / "data" / "apv.csv")
    amount = apv[
        (apv["profile"] == "IPE120")
        & (apv["montage"] == "Klammeløsning")
        & (apv["sides"].map(clean_numeric) == 3)
    ].iloc[0]
    rate = clean_numeric(amount["Antal m² fireboard pr. m profil"])
    assert rate == pytest.approx(0.349)
    angles = read_csv("angle_profile_logic.csv")

    # Exclusion labels need a language, without touching live Streamlit state.
    monkeypatch.setattr(
        mh, "st", SimpleNamespace(session_state=SimpleNamespace(language="DA"))
    )
    return SimpleNamespace(
        materials=materials,
        layers=read_csv("layer_logic.csv"),
        rate=rate,
        lookup=dict(
            materials_by_artnr=by_art,
            materials_by_dbnr=by_db,
            materials_by_description=by_description,
        ),
        generation=dict(
            fireboard_rate=rate,
            screw_rate=clean_numeric(amount["Antal skruer pr. m profil"]) or 0,
            staple_rate=clean_numeric(amount["Antal klammer pr. m profil"]) or 0,
            angle_rate=clean_numeric(amount["Antal vinkelprofil pr. m profil"]) or 0,
            angle_lookup=angles[angles["sides"] == 3],
            beam_rate=clean_numeric(amount["Antal bjælkeprofiler/PHL pr. m profil"]) or 0,
            beam_text=mh.resolve_beam_text(
                read_csv("beam_profile_logic.csv"), "IPE120", clean_text
            ),
            screw_clamp_logic_df=read_csv("screw_clamp_logic.csv"),
            materials_lookup_df=materials,
            materials_by_artnr=by_art,
            materials_by_dbnr=by_db,
            get_material_label=mh.get_material_label,
            clean_numeric=clean_numeric,
            clean_text=clean_text,
        ),
    )


@pytest.fixture
def unrounded(monkeypatch):
    # Expose production calculations before display rounding; leave all formulas intact.
    monkeypatch.setattr(mh, "format_number", float)


def build_case(data, thickness, variant, waste):
    layers = data.layers[
        (data.layers["total_mm"] == thickness) & (data.layers["variant"] == variant)
    ]
    raw = mh.generate_materials(
        layer_rows=layers, thickness=thickness, **data.generation
    )
    table = mh.build_materials_dataframe(
        raw, 6, waste, data.rate, **data.lookup
    )
    return raw, table.set_index("ART.NR.")


@pytest.mark.parametrize("waste", [0, 10])
@pytest.mark.parametrize(
    "thickness,variant,article,product_layers,co2_at_ten_percent",
    [
        (25, "A", "00002907", 1, 11.897061),
        (50, "A", "00002907", 2, 23.794122),
        (50, "B", "00002908", 1, 9.5176488),
        (50, "B", "00002909", 1, 14.2764732),
    ],
)
def test_board_quantity_and_co2_before_rounding(
    material_data, unrounded, waste, thickness, variant, article,
    product_layers, co2_at_ten_percent,
):
    raw, table = build_case(material_data, thickness, variant, waste)
    assert sum(row["Enhed"] == "m²" for row in raw) == (1 if thickness == 25 else 2)
    assert table.index.is_unique
    assert sum(table["ENHED"] == "m²") == (2 if variant == "B" else 1)
    row = table.loc[article]
    quantity = material_data.rate * product_layers
    total = quantity * 6 * (1 + waste / 100)
    factor = clean_numeric(
        material_data.lookup["materials_by_artnr"][str(int(article))]["CO2"]
    )
    assert row["FORBRUG PR. LBM"] == pytest.approx(quantity, abs=1e-12)
    assert row["SAMLET FORBRUG"] == pytest.approx(total, abs=1e-12)
    assert row["CO2"] == pytest.approx(total * factor, rel=1e-12)
    assert row["CO2"] == pytest.approx(
        co2_at_ten_percent / 1.1 * (1 + waste / 100), rel=1e-12
    )


@pytest.mark.parametrize("waste", [0, 10])
def test_same_article_aggregation_conserves_quantity_and_emissions(
    material_data, unrounded, waste,
):
    raw, _ = build_case(material_data, 50, "A", waste)
    boards = [dict(row) for row in raw if row["Enhed"] == "m²"]
    assert len(boards) == 2
    # Different label forms must still resolve to the same article.
    boards[1]["Materiale"] = material_data.lookup["materials_by_artnr"]["2907"][
        "BESKRIVELSE_DK"
    ]
    aggregated = mh.deduplicate_materials(boards, **material_data.lookup)
    assert len(aggregated) == 1
    assert aggregated[0]["Mængde"] == pytest.approx(sum(r["Mængde"] for r in boards))
    assert mh.deduplicate_materials(aggregated, **material_data.lookup) == aggregated

    def calculate(row):
        return mh.build_material_row(row, 6, waste, material_data.rate, **material_data.lookup)

    separate = [calculate(row) for row in boards]
    combined = calculate(aggregated[0])
    assert combined["SAMLET FORBRUG"] == pytest.approx(
        sum(row["SAMLET FORBRUG"] for row in separate)
    )
    assert combined["CO2"] == pytest.approx(sum(row["CO2"] for row in separate))


@pytest.mark.parametrize("waste", [0, 10])
@pytest.mark.parametrize("thickness,variant", [(25, "A"), (50, "A"), (50, "B")])
def test_filler_keeps_reference_area_and_length_keeps_linear_quantity(
    material_data, unrounded, waste, thickness, variant,
):
    _, table = build_case(material_data, thickness, variant, waste)
    area = material_data.rate * 6 * (1 + waste / 100)
    filler = table.loc["00603402"]
    filler_info = material_data.lookup["materials_by_artnr"]["603402"]
    assert filler_info["CO2_TYPE"] == "AREA"
    assert filler["ENHED"] == "kg"
    assert filler["SAMLET FORBRUG"] == pytest.approx(area * 0.35)
    assert filler["CO2"] == pytest.approx(area * clean_numeric(filler_info["CO2"]))

    angle = table.loc["00003331"]
    angle_info = material_data.lookup["materials_by_artnr"]["3331"]
    assert angle_info["CO2_TYPE"] == "LENGTH"
    assert angle["ENHED"] == "m"
    linear_total = material_data.generation["angle_rate"] * 6 * (1 + waste / 100)
    assert angle["SAMLET FORBRUG"] == pytest.approx(linear_total)
    assert angle["CO2"] == pytest.approx(linear_total * clean_numeric(angle_info["CO2"]))


@pytest.mark.parametrize(
    "language,label",
    [("DA", "Medregnes ikke jf. BR18"), ("EN", "Not included according to BR18")],
)
def test_all_ignore_products_remain_excluded(material_data, language, label):
    mh.st.session_state.language = language
    ignored = material_data.materials[material_data.materials["CO2_TYPE"] == "IGNORE"]
    assert not ignored.empty
    for product in ignored.to_dict("records"):
        row = mh.build_material_row(
            {"Materiale": product["BESKRIVELSE_DK"], "Mængde": 1, "Enhed": "stk"},
            6, 10, material_data.rate, **material_data.lookup,
        )
        assert row["CO2"] == label


@pytest.fixture(scope="module")
def app_total_calculation():
    # Execute the application's actual total calculation without running its UI/state.
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    assignments = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id in {"co2_values", "total_co2"}
            for target in node.targets
        )
    ]
    assert len(assignments) == 2
    body = sorted(assignments, key=lambda node: node.lineno)
    return compile(ast.Module(body=body, type_ignores=[]), str(ROOT / "app.py"), "exec")


@pytest.mark.parametrize("language", ["DA", "EN"])
@pytest.mark.parametrize(
    "thickness,variant,expected_total", [(25, "A", 26.83), (50, "A", 38.72), (50, "B", 38.73)]
)
def test_displayed_total_sums_valid_rounded_rows(
    material_data, app_total_calculation, language, thickness, variant, expected_total,
):
    mh.st.session_state.language = language
    _, table = build_case(material_data, thickness, variant, 10)
    displayed_values = [clean_numeric(value) for value in table["CO2"]]
    assert any(value is None for value in displayed_values)
    expected_sum = sum(value for value in displayed_values if value is not None)
    co2_column = translations[language]["material_co2"]
    namespace = {
        "pd": pd,
        "materials_table_df": table.rename(columns={"CO2": co2_column}),
        "t": translations[language].__getitem__,
    }
    exec(app_total_calculation, namespace)
    assert namespace["total_co2"] == pytest.approx(expected_sum)
    assert namespace["total_co2"] == pytest.approx(expected_total)
    assert mh.format_number(namespace["total_co2"]) == mh.format_number(expected_total)
