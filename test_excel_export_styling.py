from io import BytesIO

import pandas as pd
from openpyxl import load_workbook

from utils.export_helpers import (
    KNAUF_BLUE,
    TABLE_START_ROW,
    add_system_separator_rows,
    create_materials_excel,
)


MATERIAL_COLUMNS_DA = [
    "ART.NR.",
    "DB.nr.",
    "Producent",
    "Materiale",
    "Forbrug",
    "Enhed",
    "Total",
]


def _sample_materials_df():
    return pd.DataFrame(
        [
            ["2906", "5959671", "Knauf A/S", "15 mm Fireboard", 1.5, "m²", 3.0],
            ["181533", "8156069", "Knauf A/S", "Skrue RAB25", 2.0, "stk", 20.0],
        ],
        columns=MATERIAL_COLUMNS_DA,
    )


def _load_workbook_from_export(excel_file):
    excel_file.seek(0)
    return load_workbook(BytesIO(excel_file.read()))


def _assert_header_style(row):
    for cell in row:
        assert cell.fill.fgColor.rgb == f"00{KNAUF_BLUE}"
        assert cell.font.color.rgb == "00FFFFFF"
        assert cell.font.bold is True


def _worksheet_values(worksheet, min_row, max_row, max_col):
    return [
        [
            worksheet.cell(row=row, column=column).value
            for column in range(1, max_col + 1)
        ]
        for row in range(min_row, max_row + 1)
    ]


def test_normal_material_list_excel_is_styled_without_changing_data_values():
    source_df = _sample_materials_df()

    workbook = _load_workbook_from_export(
        create_materials_excel(source_df, language="DA")
    )
    worksheet = workbook["Materialeliste"]

    assert worksheet.cell(row=4, column=1).value == "Materialeliste"
    assert len(worksheet._images) == 1
    _assert_header_style(worksheet[TABLE_START_ROW])
    assert worksheet.freeze_panes == f"A{TABLE_START_ROW + 1}"

    exported_values = _worksheet_values(
        worksheet,
        TABLE_START_ROW + 1,
        TABLE_START_ROW + len(source_df),
        len(source_df.columns),
    )
    assert exported_values == source_df.values.tolist()


def test_combined_material_list_excel_is_styled_without_changing_aggregation_values():
    aggregated_df = pd.DataFrame(
        [
            ["2906", "5959671", "Knauf A/S", "15 mm Fireboard", 3.0, "m²", 6.0],
            ["181533", "8156069", "Knauf A/S", "Screw RAB25", 4.0, "pcs", 40.0],
        ],
        columns=[
            "ART.NO.",
            "DB no.",
            "Manufacturer",
            "Material",
            "Consumption",
            "Unit",
            "Total",
        ],
    )

    workbook = _load_workbook_from_export(
        create_materials_excel(aggregated_df, language="EN")
    )
    worksheet = workbook["Materialeliste"]

    assert worksheet.cell(row=4, column=1).value == "Material list"
    assert len(worksheet._images) == 1
    _assert_header_style(worksheet[TABLE_START_ROW])

    exported_values = _worksheet_values(
        worksheet,
        TABLE_START_ROW + 1,
        TABLE_START_ROW + len(aggregated_df),
        len(aggregated_df.columns),
    )
    assert exported_values == aggregated_df.values.tolist()


def test_per_system_material_list_preserves_structure_and_styles_repeated_headers():
    materials_df = pd.DataFrame(
        [
            ["System B", "181533", "Skrue RAB25", 2.0],
            ["System A", "2906", "15 mm Fireboard", 1.5],
            ["System B", "181534", "Skrue RAB35", 4.0],
        ],
        columns=["SYSTEM", "ART.NR.", "Materiale", "Total"],
    )
    per_system_df = add_system_separator_rows(materials_df)

    workbook = _load_workbook_from_export(
        create_materials_excel(
            per_system_df,
            include_header=False,
            language="DA",
            per_system=True,
        )
    )
    worksheet = workbook["Materialeliste"]

    assert worksheet.cell(row=4, column=1).value == "Materialeliste pr. system"
    assert len(worksheet._images) == 1
    assert worksheet.cell(row=TABLE_START_ROW, column=1).value == "SYSTEM"
    assert worksheet.freeze_panes == f"A{TABLE_START_ROW + 1}"

    repeated_header_rows = []
    for row_number in range(TABLE_START_ROW, worksheet.max_row + 1):
        row_values = [
            worksheet.cell(row=row_number, column=column).value
            for column in range(1, len(per_system_df.columns) + 1)
        ]
        if row_values == list(per_system_df.columns):
            repeated_header_rows.append(row_number)
            _assert_header_style(worksheet[row_number])

    assert len(repeated_header_rows) == 2

    system_name_rows = [TABLE_START_ROW + 1, TABLE_START_ROW + 5]
    for row_number in system_name_rows:
        assert worksheet.cell(row=row_number, column=1).font.bold is True
        assert worksheet.cell(row=row_number, column=1).fill.fgColor.rgb in (
            "00000000",
            "000000",
        )

    exported_values = _worksheet_values(
        worksheet,
        TABLE_START_ROW,
        TABLE_START_ROW + len(per_system_df) - 1,
        len(per_system_df.columns),
    )
    expected_values = per_system_df.where(pd.notna(per_system_df), None).values.tolist()
    expected_values = [
        [None if value == "" else value for value in row]
        for row in expected_values
    ]
    assert exported_values == expected_values


def test_streamlit_header_logo_uses_original_remote_asset():
    app_source = open("app.py", encoding="utf-8").read()

    assert (
        '<img class="knauf-logo" '
        'src="https://knauf.com/api/download-center/v1/assets/'
        '8355fec5-8cb9-42fe-b5d7-4e7258bf446a?download=true">'
    ) in app_source
