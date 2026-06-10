from pathlib import Path


APP_SOURCE = Path(__file__).with_name("app.py").read_text()


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
