from io import BytesIO

import pandas as pd


def add_system_separator_rows(materials_df, system_column="SYSTEM"):
    """
    Sort materials by system and add a separator row for each system.
    """

    if system_column not in materials_df.columns:

        return materials_df.copy()

    sorted_df = materials_df.sort_values(
        by=system_column,
        kind="stable"
    )

    rows = []
    previous_system = object()

    for _, row in sorted_df.iterrows():

        current_system = row[system_column]
        current_system_key = (
            ("__MISSING_SYSTEM__",)
            if pd.isna(current_system)
            else current_system
        )

        if current_system_key != previous_system:

            separator_row = {
                column: ""
                for column in sorted_df.columns
            }
            separator_row[system_column] = current_system
            rows.append(separator_row)
            previous_system = current_system_key

        rows.append(row.to_dict())

    return pd.DataFrame(
        rows,
        columns=sorted_df.columns
    )


def create_materials_excel(materials_df, autosize_columns=True):
    """
    Create Excel file from materials dataframe.
    """

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        materials_df.to_excel(
            writer,
            index=False,
            sheet_name="Materialeliste"
        )

        if autosize_columns:

            worksheet = writer.sheets["Materialeliste"]

            # Autosize columns
            for column_cells in worksheet.columns:

                max_length = max(
                    len(str(cell.value))
                    if cell.value is not None
                    else 0
                    for cell in column_cells
                )

                adjusted_width = max_length + 4

                worksheet.column_dimensions[
                    column_cells[0].column_letter
                ].width = adjusted_width

    output.seek(0)

    return output
