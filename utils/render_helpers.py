import streamlit as st


def render_materials_table(materials_df):
    """
    Render materials table.
    """

    st.table(
        materials_df.style.set_properties(
            subset=["ART.NR."],
            **{"text-align": "right"}
        )
    )
