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
    "download_fireboard_documentation": ":material/description:",
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
    "downloads": (
        '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" '
        'focusable="false" fill="none" stroke="#6b7280" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: -0.22em; margin-right: 0.25rem;">'
        '<path d="M4.75 6.25h5.05l1.55 1.75h7.9v8.75" />'
        '<path d="M4.75 6.25v11.5h14.5" />'
        '<path d="M12 10.75v4.75" />'
        '<path d="M9.8 13.35 12 15.55l2.2-2.2" />'
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
    """Return an inline icon for HTML material-link columns."""

    icons = {
        "epd": {
            "label": "EPD",
            "color": "#2e7d32",
            "material_symbol": "eco",
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

    if "material_symbol" in icon:
        symbol = escape(icon["material_symbol"])
        return (
            f'<span class="material-link-icon material-link-icon-{escape(icon_name)}" '
            f'aria-label="{escape(icon["label"])}" title="{escape(icon["label"])}">'
            '<span class="material-symbols-rounded" aria-hidden="true" '
            f'style="color: {icon["color"]}; font-family: '
            "'Material Symbols Rounded', 'Material Symbols Outlined'; "
            'font-weight: normal; font-style: normal; font-size: 18px; '
            'line-height: 18px; letter-spacing: normal; text-transform: none; '
            'display: inline-flex; align-items: center; justify-content: center; '
            'width: 18px; height: 18px; white-space: nowrap; word-wrap: normal; '
            "direction: ltr; -webkit-font-feature-settings: \'liga\'; "
            "-webkit-font-smoothing: antialiased; font-feature-settings: \'liga\'; "
            'vertical-align: -0.2em;">'
            f'{symbol}'
            '</span>'
            '</span>'
        )

    svg_path = (
        f'<path d="{icon["path"]}" '
        f'style="color: {icon["color"]};" />'
    )

    return (
        f'<span class="material-link-icon material-link-icon-{escape(icon_name)}" '
        f'aria-label="{escape(icon["label"])}" title="{escape(icon["label"])}">'
        '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" '
        'focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: -0.2em;">'
        f'{svg_path}'
        '</svg>'
        '</span>'
    )
