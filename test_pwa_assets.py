import json
from pathlib import Path

from utils.pwa import (
    APPLE_TOUCH_ICON_URL,
    DATA_URI_IMAGE_TYPE,
    DATA_URI_MANIFEST_TYPE,
    FAVICON_URL,
    ICON_192_URL,
    ICON_512_URL,
    KNAUF_BLUE,
    MANIFEST_METADATA,
    MANIFEST_URL,
    build_pwa_head_tags,
)


def test_manifest_metadata_uses_knauf_fireboard_pwa_values():
    manifest = json.loads(Path("static/manifest.webmanifest").read_text())

    assert manifest["name"] == "Knauf Fireboard"
    assert manifest["short_name"] == "Fireboard"
    assert manifest["display"] == "browser"
    assert manifest["theme_color"] == KNAUF_BLUE
    assert manifest["background_color"] == "#ffffff"
    assert manifest["orientation"] == "any"
    assert "_comment" not in manifest


def test_manifest_uses_static_relative_icon_paths():
    manifest = json.loads(Path("static/manifest.webmanifest").read_text())

    assert manifest["icons"] == [
        {
            "src": "icons/icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable",
        },
        {
            "src": "icons/icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable",
        },
    ]
    assert all(not icon["src"].startswith("/") for icon in manifest["icons"])
    assert Path("static/icons/icon-192.png").exists()
    assert Path("static/icons/icon-512.png").exists()


def test_streamlit_static_serving_is_enabled_for_repository_static_folder():
    config_content = Path(".streamlit/config.toml").read_text()

    assert "[server]" in config_content
    assert "enableStaticServing = true" in config_content


def test_pwa_head_links_use_inline_data_uris_instead_of_streamlit_static_paths():
    assert MANIFEST_URL.startswith(f"data:{DATA_URI_MANIFEST_TYPE};base64,")
    assert APPLE_TOUCH_ICON_URL.startswith(f"data:{DATA_URI_IMAGE_TYPE};base64,")
    assert FAVICON_URL.startswith(f"data:{DATA_URI_IMAGE_TYPE};base64,")
    assert ICON_192_URL.startswith(f"data:{DATA_URI_IMAGE_TYPE};base64,")
    assert ICON_512_URL.startswith(f"data:{DATA_URI_IMAGE_TYPE};base64,")
    assert not any(
        "/app/static" in url or "/static" in url
        for url in (
            MANIFEST_URL,
            APPLE_TOUCH_ICON_URL,
            FAVICON_URL,
            ICON_192_URL,
            ICON_512_URL,
        )
    )


def test_inline_manifest_uses_data_uri_icons():
    assert MANIFEST_METADATA["icons"] == [
        {
            "src": ICON_192_URL,
            "sizes": "192x192",
            "type": DATA_URI_IMAGE_TYPE,
            "purpose": "any maskable",
        },
        {
            "src": ICON_512_URL,
            "sizes": "512x512",
            "type": DATA_URI_IMAGE_TYPE,
            "purpose": "any maskable",
        },
    ]


def test_generated_pwa_head_tags_include_ipad_and_manifest_metadata():
    head_tags = build_pwa_head_tags()

    assert f'<link rel="manifest" href="{MANIFEST_URL}">' in head_tags
    assert f'<link rel="apple-touch-icon" href="{APPLE_TOUCH_ICON_URL}">' in head_tags
    assert f'<link rel="icon" type="image/png" href="{FAVICON_URL}">' in head_tags
    assert f'sizes="192x192" href="{FAVICON_URL}"' not in head_tags
    assert 'name="apple-mobile-web-app-capable"' not in head_tags
    assert '<meta name="apple-mobile-web-app-title" content="Knauf Fireboard">' in head_tags
    assert 'name="apple-mobile-web-app-status-bar-style"' not in head_tags
    assert f'<meta name="theme-color" content="{KNAUF_BLUE}">' in head_tags
    assert "viewport-fit=cover" in head_tags
    assert "width=device-width" in head_tags


def test_pwa_favicon_uses_original_asset_without_javascript_override():
    pwa_content = Path("utils/pwa.py").read_text()

    assert 'FAVICON_URL = _png_data_uri("favicon.png")' in pwa_content
    assert 'ICON_192_URL = _png_data_uri("icon-192.png")' in pwa_content
    assert "build_favicon_override_injection_html" not in pwa_content
    assert "data-fireboard-favicon" not in pwa_content
    assert "querySelectorAll('link[rel=\"icon\"]" not in pwa_content
    assert FAVICON_URL != ICON_192_URL


def test_generated_pwa_head_tags_do_not_enable_fullscreen_standalone_mode():
    head_tags = build_pwa_head_tags()

    assert 'name="apple-mobile-web-app-capable"' not in head_tags
    assert '<meta name="apple-mobile-web-app-title" content="Knauf Fireboard">' in head_tags
    assert 'name="apple-mobile-web-app-status-bar-style"' not in head_tags
    assert '<meta name="mobile-web-app-capable" content="yes">' not in head_tags
    assert '<meta name="mobile-web-app-capable" content="no">' in head_tags


def test_streamlit_starts_with_original_favicon_and_expanded_sidebar_on_desktop():
    app_content = Path("app.py").read_text()

    assert "st.set_page_config(" in app_content
    assert 'page_icon="static/icons/favicon.png"' in app_content
    assert "FIREBOARD_FAVICON_PATH" not in app_content
    assert 'initial_sidebar_state="expanded"' in app_content


def test_fireboard_project_menu_replaces_tablet_sidebar_hint():
    app_content = Path("app.py").read_text()
    translations_content = Path("translations.py").read_text()

    assert '"project_menu_button"' in app_content
    assert 'class="fireboard-project-menu-button"' in app_content
    assert "@media (max-width: 1180px)" in app_content
    assert "components.html(" in app_content
    assert "findStreamlitSidebarToggle" in app_content
    assert "Streamlit-internal sidebar toggle controls" in app_content
    assert "stSidebarCollapsedControl" in app_content
    assert "stSidebarCollapseButton" in app_content
    assert "button::after" not in app_content

    assert "☰ Projekt" in translations_content
    assert "☰ Project" in translations_content
    assert "tablet_sidebar_header_hint" not in app_content
    assert "tablet-sidebar-header-hint" not in app_content
    assert "tablet_sidebar_header_hint" not in translations_content
    assert "‹‹ Åbn/luk projektmenu" not in translations_content
    assert "‹‹ Open/close project menu" not in translations_content
