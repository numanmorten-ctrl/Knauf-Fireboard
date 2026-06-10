from utils.icons import INLINE_ICONS, material_link_icon


def test_epd_icon_uses_green_material_symbol_eco():
    icon_html = material_link_icon("epd")

    assert "material-symbols-rounded" in icon_html
    assert ">eco<" in icon_html
    assert "#2e7d32" in icon_html
    assert "width: 18px" in icon_html
    assert "height: 18px" in icon_html


def test_datasheet_icon_remains_grey_svg_document():
    icon_html = material_link_icon("datasheet")

    assert "<svg" in icon_html
    assert "#6b7280" in icon_html
    assert "material-symbols-rounded" not in icon_html
    assert ">eco<" not in icon_html


def test_downloads_inline_icon_matches_neutral_sidebar_heading_style():
    icon_html = INLINE_ICONS["downloads"]

    assert "<svg" in icon_html
    assert 'stroke="#6b7280"' in icon_html
    assert 'width="20"' in icon_html
    assert 'height="20"' in icon_html
    assert "material-symbols-rounded" not in icon_html
