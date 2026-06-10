import json
from pathlib import Path

from utils.pwa import KNAUF_BLUE, MANIFEST_URL, build_pwa_head_tags


def test_manifest_metadata_uses_knauf_fireboard_pwa_values():
    manifest = json.loads(Path("static/manifest.webmanifest").read_text())

    assert manifest["name"] == "Knauf Fireboard"
    assert manifest["short_name"] == "Fireboard"
    assert manifest["display"] == "standalone"
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
    assert '<meta name="apple-mobile-web-app-capable" content="yes">' in head_tags
    assert '<meta name="apple-mobile-web-app-title" content="Fireboard">' in head_tags
    assert '<meta name="apple-mobile-web-app-status-bar-style" content="default">' in head_tags
    assert '<meta name="mobile-web-app-capable" content="yes">' in head_tags
    assert f'<meta name="theme-color" content="{KNAUF_BLUE}">' in head_tags
    assert "viewport-fit=cover" in head_tags
    assert "width=device-width" in head_tags
