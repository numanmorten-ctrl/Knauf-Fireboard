"""Documentation download helpers for the Fireboard sidebar."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from utils.icons import INLINE_ICONS, UI_ICONS


FIREBOARD_DOCUMENTATION_URL = (
    "https://knauf.com/api/download-center/v1/assets/"
    "f094f272-cb93-4ae1-ac0f-b7c9f4653378?download=true"
)

# Future documentation package actions to add here when project-level
# document generation is ready:
# - Download samlet dokumentationspakke
# - Download alle EPD'er for projektet
# - Download alle datablade for projektet
# - Download ZIP med projektdokumentation
FUTURE_PROJECT_DOCUMENTATION_DOWNLOADS = ()


def render_documentation_sidebar_section(t: Callable[[str], str]) -> None:
    """Render reusable sidebar controls for Fireboard documentation downloads."""

    st.divider()

    st.markdown(
        f"""
        <div class="sidebar-calculations-heading sidebar-documentation-heading">
            {INLINE_ICONS["downloads"]} {t("documentation_section_title")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.link_button(
        label=t("download_fireboard_documentation"),
        url=FIREBOARD_DOCUMENTATION_URL,
        icon=UI_ICONS["download_fireboard_documentation"],
        use_container_width=True,
    )
