import streamlit as st
import streamlit.components.v1 as components


def render_materials_table(materials_df):
    """
    Render materials table.
    """

    html = materials_df.to_html(
        index=False,
        escape=False
    )

    components.html(
        html,
        height=1200,
        scrolling=True
    )
