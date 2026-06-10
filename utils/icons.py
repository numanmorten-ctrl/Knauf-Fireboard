"""Centralized UI icon definitions for the Fireboard app."""

from __future__ import annotations

from html import escape


# Streamlit supports Material Symbols by passing strings in the
# ``:material/icon_name:`` format to the ``icon`` parameter on buttons.
UI_ICONS = {
    "calculations": ":material/assignment:",
    "new_calculation": ":material/add:",
    "download_all_calculations": ":material/file_copy:",
    "download_combined_material_list": ":material/table_chart:",
    "download_material_list_per_calculation": ":material/backup_table:",
    "download_material_list": ":material/table_chart:",
    "delete_calculation": ":material/delete:",
    "delete_project": ":material/delete:",
    "language_selector": ":material/language:",
    "download_this_calculation": ":material/description:",
    "update_calculation": ":material/sync:",
    "add_calculation": ":material/add:",
}

# Neutral text glyph used where Streamlit's button icon API is not available,
# for example inside custom markdown headings.
INLINE_ICONS = {
    "calculations": "▤",
}

_ICON_PREFIXES = (
    "📄 ",
    "🔄 ",
    "➕ ",
)


def action_label(label: str) -> str:
    """Return an existing translated label without a legacy emoji prefix."""

    for prefix in _ICON_PREFIXES:
        if label.startswith(prefix):
            return label[len(prefix):]

    return label


def material_link_icon(icon_name: str) -> str:
    """Return an inline SVG icon for HTML material-link columns."""

    icons = {
        "epd": {
            "label": "EPD",
            "color": "#2e7d32",
            "path": (
                "M17.75 3.1c-4.55.35-8.16 1.74-10.75 4.13"
                "C4.76 9.29 3.64 12 3.64 15.28c0 2.62 1.45 4.37 3.61 4.37"
                "1.83 0 3.51-1.1 4.95-3.24 1.25-1.85 2.24-4.33 2.95-7.38"
                "-2.28.79-4.26 2.02-5.94 3.69a.75.75 0 1 1-1.06-1.06"
                "2.28-2.28 5.03-3.8 8.18-4.52a.75.75 0 0 1 .9.85"
                "-.69 4.31-1.94 7.69-3.71 10.05-1.72 2.29-3.8 3.45-6.18 3.45"
                "-3.04 0-5.11-2.48-5.11-5.87 0-3.69 1.29-6.81 3.84-9.3"
                "2.87-2.8 6.77-4.4 11.6-4.77a.75.75 0 0 1 .81.81Z"
            ),
        },
        "datasheet": {
            "label": "Datasheet",
            "color": "#6b7280",
            "path": (
                "M6.75 2.75h7.1c.2 0 .39.08.53.22l3.9 3.9c.14.14.22.33.22.53v13.85"
                "c0 .41-.34.75-.75.75h-11c-.41 0-.75-.34-.75-.75V3.5c0-.41.34-.75.75-.75Z"
                "M13.5 3v4.75h4.75M8.75 11.25h7M8.75 14.75h7M8.75 18.25h4.5"
            ),
        },
    }

    icon = icons[icon_name]

    return (
        f'<span class="material-link-icon material-link-icon-{escape(icon_name)}" '
        f'aria-label="{escape(icon["label"])}" title="{escape(icon["label"])}">'
        '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" '
        'focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" '
        f'style="color: {icon["color"]}; vertical-align: -0.2em;">'
        f'<path d="{icon["path"]}" />'
        '</svg>'
        '</span>'
    )
