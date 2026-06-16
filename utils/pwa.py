"""Helpers for Fireboard iPad home-screen / PWA metadata.

For iPad installation, users should open the site in Safari and choose
"Føj til hjemmeskærm" / "Add to Home Screen". The manifest deliberately
uses browser display mode because PDF/Excel downloads on iPad need normal
browser navigation so users can return to the app after Safari previews a file.
"""

from __future__ import annotations

import base64
import json
from html import escape
from pathlib import Path
from typing import Iterable

KNAUF_BLUE = "#003b7a"
PWA_INJECTION_MARKER_ID = "fireboard-pwa-head-tags"
FAVICON_OVERRIDE_MARKER_ID = "fireboard-favicon-override"
IPAD_VIEWPORT = (
    "width=device-width, initial-scale=1, viewport-fit=cover, "
    "minimum-scale=1"
)
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
STATIC_ICON_DIR = REPOSITORY_ROOT / "static" / "icons"
DATA_URI_IMAGE_TYPE = "image/png"
DATA_URI_MANIFEST_TYPE = "application/manifest+json"


def _png_data_uri(filename: str) -> str:
    """Return a PNG icon as an inline data URI.

    Streamlit Cloud static serving is not always reachable from the public app
    URL before the Streamlit frontend has booted. Inlining keeps the PWA icon
    links independent of Streamlit's `/app/static/...` route so Safari/Chrome
    can resolve them directly from the injected head tags.
    """

    encoded_icon = base64.b64encode((STATIC_ICON_DIR / filename).read_bytes()).decode(
        "ascii"
    )
    return f"data:{DATA_URI_IMAGE_TYPE};base64,{encoded_icon}"


APPLE_TOUCH_ICON_URL = _png_data_uri("apple-touch-icon.png")
FAVICON_URL = _png_data_uri("icon-192.png")
ICON_192_URL = FAVICON_URL
ICON_512_URL = _png_data_uri("icon-512.png")

MANIFEST_METADATA: dict[str, object] = {
    "name": "Knauf Fireboard",
    "short_name": "Fireboard",
    "display": "browser",
    "theme_color": KNAUF_BLUE,
    "background_color": "#ffffff",
    "orientation": "any",
    "icons": [
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
    ],
}
MANIFEST_URL = (
    f"data:{DATA_URI_MANIFEST_TYPE};base64,"
    + base64.b64encode(
        json.dumps(MANIFEST_METADATA, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
)

PWA_META_TAGS: tuple[dict[str, str], ...] = (
    # Do not add Apple standalone/fullscreen metadata here. iPad users need
    # normal Safari navigation after PDF/Excel downloads so they can return to
    # the app after Safari previews a file. Keeping only standard browser/PWA
    # metadata preserves Add to Home Screen compatibility as far as iOS allows.
    {"name": "mobile-web-app-capable", "content": "no"},
    {"name": "apple-mobile-web-app-title", "content": "Knauf Fireboard"},
    {"name": "theme-color", "content": KNAUF_BLUE},
    {"name": "viewport", "content": IPAD_VIEWPORT},
)

PWA_LINK_TAGS: tuple[dict[str, str], ...] = (
    {"rel": "manifest", "href": MANIFEST_URL},
    {"rel": "apple-touch-icon", "href": APPLE_TOUCH_ICON_URL},
    {
        "rel": "icon",
        "type": DATA_URI_IMAGE_TYPE,
        "sizes": "192x192",
        "href": FAVICON_URL,
    },
)


def _format_attrs(attributes: dict[str, str]) -> str:
    return " ".join(
        f'{escape(key, quote=True)}="{escape(value, quote=True)}"'
        for key, value in attributes.items()
    )


def build_pwa_head_tags(
    meta_tags: Iterable[dict[str, str]] = PWA_META_TAGS,
    link_tags: Iterable[dict[str, str]] = PWA_LINK_TAGS,
) -> str:
    """Build the manifest and Apple/mobile metadata tags for the page head."""

    links = [f"<link {_format_attrs(attributes)}>" for attributes in link_tags]
    metas = [f"<meta {_format_attrs(attributes)}>" for attributes in meta_tags]
    return "\n".join([*links, *metas])


def build_pwa_head_injection_html() -> str:
    """Return a small script that idempotently appends PWA tags to Streamlit's head."""

    head_tags = build_pwa_head_tags().replace("`", "\\`").replace("</script", "<\\/script")
    return f"""
<div id=\"{PWA_INJECTION_MARKER_ID}\"></div>
<script>
(function () {{
  const markerId = "{PWA_INJECTION_MARKER_ID}";
  const doc = window.parent && window.parent.document ? window.parent.document : document;
  if (doc.head.querySelector(`meta[data-fireboard-pwa="${{markerId}}"]`)) {{
    return;
  }}

  const template = doc.createElement("template");
  template.innerHTML = `{head_tags}`;
  template.content.querySelectorAll("meta, link").forEach((node) => {{
    node.setAttribute("data-fireboard-pwa", markerId);
    doc.head.appendChild(node);
  }});
}})();
</script>
""".strip()


def build_favicon_override_injection_html() -> str:
    """Return a script that re-applies the Fireboard favicon after Streamlit loads."""

    favicon_url = (
        FAVICON_URL.replace('\\', '\\\\')
        .replace('"', '\\"')
        .replace('</script', '<\\/script')
    )
    return f"""
<div id=\"{FAVICON_OVERRIDE_MARKER_ID}\"></div>
<script>
(function () {{
  const faviconHref = "{favicon_url}";
  const markerId = "{FAVICON_OVERRIDE_MARKER_ID}";
  const doc = window.parent && window.parent.document ? window.parent.document : document;

  function applyFireboardFavicon() {{
    doc.head.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]').forEach((node) => {{
      node.remove();
    }});

    const icon = doc.createElement("link");
    icon.setAttribute("rel", "icon");
    icon.setAttribute("type", "image/png");
    icon.setAttribute("sizes", "192x192");
    icon.setAttribute("href", faviconHref);
    icon.setAttribute("data-fireboard-favicon", markerId);
    doc.head.appendChild(icon);

    const shortcutIcon = doc.createElement("link");
    shortcutIcon.setAttribute("rel", "shortcut icon");
    shortcutIcon.setAttribute("type", "image/png");
    shortcutIcon.setAttribute("href", faviconHref);
    shortcutIcon.setAttribute("data-fireboard-favicon", markerId);
    doc.head.appendChild(shortcutIcon);
  }}

  applyFireboardFavicon();
  [250, 1000, 2500].forEach((delay) => window.setTimeout(applyFireboardFavicon, delay));
}})();
</script>
""".strip()


def render_pwa_head_tags() -> None:
    """Inject Fireboard iPad home-screen tags without fullscreen standalone launch."""

    import streamlit.components.v1 as components

    components.html(build_pwa_head_injection_html(), height=0, width=0)
    components.html(build_favicon_override_injection_html(), height=0, width=0)
