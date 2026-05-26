import streamlit as st


def render_materials_table(materials_df):
    """
    Render materials table.
    """

    st.table(materials_df)
