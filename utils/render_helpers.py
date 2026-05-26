import streamlit as st


def render_materials_table(materials_df):
    """
    Render materials table.
    """

    st.dataframe(
        materials_df,
        use_container_width=True,
        hide_index=True
    )
