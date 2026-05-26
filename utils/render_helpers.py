import streamlit as st


def render_materials_table(materials_df):
    """
    Render styled materials table.
    """

    styled_df = (
        materials_df.style

        # HEADER STYLE
        .set_table_styles([
            {
                "selector": "thead th",
                "props": [
                    ("background-color", "#f3f4f6"),
                    ("color", "#374151"),
                    ("font-weight", "600"),
                    ("border-top", "none"),
                    ("border-left", "none"),
                    ("border-right", "none"),
                    ("border-bottom", "1px solid #d1d5db"),
                    ("padding", "12px"),
                    ("text-align", "left"),
                ]
            },

            # BODY CELLS
            {
                "selector": "tbody td",
                "props": [
                    ("border-left", "none"),
                    ("border-right", "none"),
                    ("border-top", "none"),
                    ("border-bottom", "1px solid #e5e7eb"),
                    ("padding", "12px"),
                ]
            },

            # TABLE
            {
                "selector": "table",
                "props": [
                    ("border-collapse", "collapse"),
                    ("width", "100%"),
                    ("font-size", "14px"),
                ]
            }
        ])

        .hide(axis="index")
    )

    st.table(styled_df)
