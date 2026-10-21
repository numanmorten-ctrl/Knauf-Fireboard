import base64
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image
from streamlit.testing.v1 import AppTest

from translations import translations


REPOSITORY_ROOT = Path(__file__).resolve().parent


@pytest.mark.parametrize(
    ("language", "filename"),
    [("DA", "apv_geometry_da.png"), ("EN", "apv_geometry_en.png")],
)
def test_apv_geometry_guide_renders_inline_png_and_can_be_closed(language, filename):
    app = AppTest.from_file(str(REPOSITORY_ROOT / "app.py"), default_timeout=20)
    app.session_state["language"] = language
    app.run()
    assert not app.exception

    category_key = f"category_{translations[language]['other_profiles']}"
    app.button(key=category_key).click().run()
    app.button(key="custom_profile_method_geometry").click().run()
    assert not app.exception
    assert app.session_state["show_apv_geometry_help"] is True
    assert any(
        item.value == f"### {translations[language]['apv_geometry_guide_title']}"
        for item in app.markdown
    )

    images = app.get("imgs")
    assert len(images) == 1
    assert len(images[0].proto.imgs) == 1
    image_uri = images[0].proto.imgs[0].url
    prefix = "data:image/png;base64,"
    assert image_uri.startswith(prefix)

    png_bytes = base64.b64decode(image_uri[len(prefix):], validate=True)
    assert png_bytes == (REPOSITORY_ROOT / "static" / "images" / filename).read_bytes()
    with Image.open(BytesIO(png_bytes)) as image:
        assert image.format == "PNG"
        image.verify()

    close_button = app.button(key="close_apv_geometry_guide")
    assert close_button.label == translations[language]["close_apv_geometry_guide"]
    close_button.click().run()
    assert not app.exception
    assert app.session_state["show_apv_geometry_help"] is False
    assert not app.get("imgs")
