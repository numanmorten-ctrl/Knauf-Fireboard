"""Documentation download helpers for the Fireboard sidebar."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from utils.documentation_urls import (
    FIREBOARD_INSTALLATION_SECTION_URL,
    FIREBOARD_MANUAL_SECTION_URL,
)
from utils.icons import INLINE_ICONS, UI_ICONS

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
        url=FIREBOARD_MANUAL_SECTION_URL,
        icon=UI_ICONS["download_fireboard_documentation"],
        use_container_width=True,
    )

    st.link_button(
        label=t("download_fireboard_installation_section"),
        url=FIREBOARD_INSTALLATION_SECTION_URL,
        icon=UI_ICONS["download_fireboard_installation_section"],
        use_container_width=True,
    )
