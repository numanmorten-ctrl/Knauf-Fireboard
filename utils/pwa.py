"""Helpers for Fireboard iPad home-screen / PWA metadata.

For iPad installation, users should open the site in Safari and choose
"Føj til hjemmeskærm" / "Add to Home Screen".
"""

from __future__ import annotations

from html import escape
from typing import Iterable

KNAUF_BLUE = "#003b7a"
MANIFEST_URL = "/app/static/manifest.webmanifest"
PWA_INJECTION_MARKER_ID = "fireboard-pwa-head-tags"
IPAD_VIEWPORT = (
    "width=device-width, initial-scale=1, viewport-fit=cover, "
    "minimum-scale=1"
)

PWA_META_TAGS: tuple[dict[str, str], ...] = (
    {"name": "apple-mobile-web-app-capable", "content": "yes"},
    {"name": "apple-mobile-web-app-title", "content": "Fireboard"},
    {"name": "apple-mobile-web-app-status-bar-style", "content": "default"},
    {"name": "mobile-web-app-capable", "content": "yes"},
    {"name": "theme-color", "content": KNAUF_BLUE},
    {"name": "viewport", "content": IPAD_VIEWPORT},
)

PWA_LINK_TAGS: tuple[dict[str, str], ...] = (
    {"rel": "manifest", "href": MANIFEST_URL},
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


def render_pwa_head_tags() -> None:
    """Inject Fireboard PWA tags for iPad Safari and standalone home-screen use."""

    import streamlit.components.v1 as components

    components.html(build_pwa_head_injection_html(), height=0, width=0)
