import json
from pathlib import Path

from utils.pwa import KNAUF_BLUE, MANIFEST_URL, build_pwa_head_tags


def test_manifest_metadata_uses_knauf_fireboard_pwa_values():
    manifest = json.loads(Path("static/manifest.webmanifest").read_text())

    assert manifest["name"] == "Knauf Fireboard"
    assert manifest["short_name"] == "Fireboard"
    assert manifest["display"] == "browser"
    assert manifest["theme_color"] == KNAUF_BLUE
    assert manifest["background_color"] == "#ffffff"
    assert manifest["orientation"] == "any"
    assert "manual" in manifest["_comment"]


def test_manifest_uses_placeholder_icon_paths_without_requiring_binary_assets():
    manifest = json.loads(Path("static/manifest.webmanifest").read_text())

    assert manifest["icons"] == [
        {
            "_comment": "Placeholder only: upload this PNG file manually later.",
            "src": "/app/static/icons/icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable",
        },
        {
            "_comment": "Placeholder only: upload this PNG file manually later.",
            "src": "/app/static/icons/icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable",
        },
    ]
    assert not Path("static/icons/icon-192.png").exists()
    assert not Path("static/icons/icon-512.png").exists()


def test_generated_pwa_head_tags_include_ipad_and_manifest_metadata():
    head_tags = build_pwa_head_tags()

    assert f'<link rel="manifest" href="{MANIFEST_URL}">' in head_tags
    assert 'name="apple-mobile-web-app-capable"' not in head_tags
    assert 'name="apple-mobile-web-app-title"' not in head_tags
    assert 'name="apple-mobile-web-app-status-bar-style"' not in head_tags
    assert f'<meta name="theme-color" content="{KNAUF_BLUE}">' in head_tags
    assert "viewport-fit=cover" in head_tags
    assert "width=device-width" in head_tags


def test_generated_pwa_head_tags_do_not_enable_fullscreen_standalone_mode():
    head_tags = build_pwa_head_tags()

    assert 'name="apple-mobile-web-app-capable"' not in head_tags
    assert 'name="apple-mobile-web-app-title"' not in head_tags
    assert 'name="apple-mobile-web-app-status-bar-style"' not in head_tags
    assert '<meta name="mobile-web-app-capable" content="yes">' not in head_tags
    assert '<meta name="mobile-web-app-capable" content="no">' in head_tags


def test_streamlit_starts_with_collapsed_sidebar():
    app_content = Path("app.py").read_text()

    assert "st.set_page_config(" in app_content
    assert 'initial_sidebar_state="collapsed"' in app_content


def test_tablet_project_menu_labels_are_available_to_generated_css():
    app_content = Path("app.py").read_text()
    translations_content = Path("translations.py").read_text()

    assert 't("tablet_project_menu_label")' in app_content
    assert '[data-testid="stSidebarCollapsedControl"] button::after' in app_content
    assert "@media (max-width: 1180px)" in app_content
    assert "☰ Projekt" in translations_content
    assert "☰ Project" in translations_content
