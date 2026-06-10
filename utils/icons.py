"""Centralized UI icon definitions for the Fireboard app."""

from __future__ import annotations

from html import escape


# Streamlit supports Material Symbols by passing strings in the
# ``:material/icon_name:`` format to the ``icon`` parameter on buttons.
UI_ICONS = {
    "calculations": ":material/view_list:",
    "new_calculation": ":material/add:",
    "download_all_calculations": ":material/file_copy:",
    "download_combined_material_list": ":material/backup_table:",
    "download_material_list_per_calculation": ":material/inventory_2:",
    "download_material_list": ":material/table_chart:",
    "delete_calculation": ":material/delete:",
    "delete_project": ":material/delete:",
    "language_selector": ":material/language:",
    "download_this_calculation": ":material/description:",
    "update_calculation": ":material/sync:",
    "add_calculation": ":material/add:",
}

# Neutral inline SVGs used where Streamlit's button icon API is not available,
# for example inside custom markdown headings.
INLINE_ICONS = {
    "calculations": (
        '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" '
        'focusable="false" fill="none" stroke="#6b7280" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: -0.22em; margin-right: 0.25rem;">'
        '<path d="M8 6.25h10.25M8 12h10.25M8 17.75h10.25" />'
        '<path d="M4.75 6.25h.5M4.75 12h.5M4.75 17.75h.5" />'
        '</svg>'
    ),
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
            "paths": (
                {
                    "color": "#6b7280",
                    "d": (
                        "M6.75 2.75h7.1c.2 0 .39.08.53.22l3.9 3.9"
                        "c.14.14.22.33.22.53v13.85c0 .41-.34.75-.75.75"
                        "h-11c-.41 0-.75-.34-.75-.75V3.5c0-.41.34-.75.75-.75Z"
                        "M13.5 3v4.75h4.75M8.75 11.1h4.35M8.75 14.15h2.75"
                    ),
                },
                {
                    "color": "#2e7d32",
                    "d": (
                        "M18.7 12.2c-3.9.28-6.45 1.52-7.68 3.7"
                        "-.63 1.12-.57 2.45.13 3.28.78.93 2.2 1.12 3.5.49"
                        "1.74-.85 3.05-2.8 3.92-5.83M12.2 19.25"
                        "c1.05-1.72 2.5-3.08 4.48-4.18"
                    ),
                },
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
    paths = icon.get("paths")

    if paths is None:
        paths = (
            {
                "color": icon["color"],
                "d": icon["path"],
            },
        )
    svg_paths = "".join(
        (
            f'<path d="{path["d"]}" '
            f'style="color: {path.get("color", icon["color"])};" />'
        )
        for path in paths
    )

    return (
        f'<span class="material-link-icon material-link-icon-{escape(icon_name)}" '
        f'aria-label="{escape(icon["label"])}" title="{escape(icon["label"])}">'
        '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" '
        'focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: -0.2em;">'
        f'{svg_paths}'
        '</svg>'
        '</span>'
    )
