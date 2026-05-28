import streamlit as st


def render_materials_table(materials_df):
    """
    Render materials table.
    """

    html = materials_df.to_html(
        index=False,
        escape=False
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )
