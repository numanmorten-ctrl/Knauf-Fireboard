import ast
import base64
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace


APP_SOURCE = Path(__file__).with_name("app.py").read_text()


def load_download_helpers():
    module = ast.parse(APP_SOURCE)
    helper_defs = [
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef)
        and node.name in {"ensure_bytes", "trigger_browser_download"}
    ]
    helper_module = ast.Module(body=helper_defs, type_ignores=[])
    ast.fix_missing_locations(helper_module)

    html_calls = []
    namespace = {
        "base64": base64,
        "BytesIO": BytesIO,
        "json": __import__("json"),
        "components": SimpleNamespace(
            html=lambda *args, **kwargs: html_calls.append((args, kwargs))
        ),
    }
    exec(compile(helper_module, filename="app.py", mode="exec"), namespace)
    namespace["html_calls"] = html_calls
    return namespace


def test_project_package_uses_component_auto_download():
    assert "import streamlit.components.v1 as components" in APP_SOURCE
    assert "def trigger_browser_download" in APP_SOURCE
    assert "base64.b64encode" in APP_SOURCE
    assert "components.html(" in APP_SOURCE
    assert "anchor.click()" in APP_SOURCE
    assert "data:{mime};base64" in APP_SOURCE
    assert "project_package_filename(st.session_state.language)" in APP_SOURCE
    assert "mime=PROJECT_PACKAGE_MIME" in APP_SOURCE


def test_project_package_keeps_lazy_generation_behind_normal_button():
    assert 'label=t("download_project_package")' in APP_SOURCE
    assert 'key="download_project_package"' in APP_SOURCE
    assert 'if st.button(' in APP_SOURCE
    assert 'with st.spinner(t("preparing_project_package_status"))' in APP_SOURCE
    assert "create_project_package_zip(" in APP_SOURCE


def test_project_package_second_button_removed_without_affecting_normal_downloads():
    assert 'label=t("get_project_package")' not in APP_SOURCE
    assert 'key="get_project_package"' not in APP_SOURCE

    normal_download_keys = [
        "download_all_calculations",
        "download_combined_material_list",
        "download_material_list_per_calculation",
    ]

    for key in normal_download_keys:
        assert f'key="{key}"' in APP_SOURCE

    assert APP_SOURCE.count("st.download_button(") >= len(normal_download_keys)


def test_ensure_bytes_returns_bytesio_value_without_moving_cursor():
    helpers = load_download_helpers()
    package = BytesIO(b"project-package")
    package.seek(7)

    assert helpers["ensure_bytes"](package) == b"project-package"
    assert package.tell() == 7


def test_trigger_browser_download_accepts_bytesio_project_package_data():
    helpers = load_download_helpers()

    helpers["trigger_browser_download"](
        data=BytesIO(b"project-package"),
        file_name="project.zip",
        mime="application/zip",
    )

    assert helpers["html_calls"]
    html = helpers["html_calls"][0][0][0]
    assert "data:application/zip;base64,cHJvamVjdC1wYWNrYWdl" in html
    assert "project.zip" in html
