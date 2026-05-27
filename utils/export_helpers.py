from io import BytesIO

import pandas as pd


def create_materials_excel(materials_df):
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
