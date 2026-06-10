from pathlib import Path


APP_SOURCE = Path(__file__).with_name("app.py").read_text()


def test_project_downloads_use_streamlit_native_download_buttons():
    project_download_keys = [
        "download_all_calculations",
        "download_combined_material_list",
        "download_material_list_per_calculation",
        "get_project_package",
    ]

    for key in project_download_keys:
        assert f'key="{key}"' in APP_SOURCE

    assert APP_SOURCE.count("st.download_button(") >= len(project_download_keys)
    assert "trigger_browser_download" not in APP_SOURCE
    assert "streamlit.components" not in APP_SOURCE


def test_project_package_keeps_lazy_generation_behind_normal_button():
    assert 'label=t("download_project_package")' in APP_SOURCE
    assert 'key="download_project_package"' in APP_SOURCE
    assert 'if st.button(' in APP_SOURCE
    assert 'label=t("get_project_package")' in APP_SOURCE
    assert 'key="get_project_package"' in APP_SOURCE
