from pathlib import Path


APP_SOURCE = Path(__file__).with_name("app.py").read_text()
TRANSLATIONS_SOURCE = Path(__file__).with_name("translations.py").read_text()


def test_project_package_browser_auto_download_helper_removed():
    assert "import streamlit.components.v1 as components" not in APP_SOURCE
    assert "def trigger_browser_download" not in APP_SOURCE
    assert "base64.b64encode" not in APP_SOURCE
    assert "components.html(" not in APP_SOURCE
    assert "anchor.click()" not in APP_SOURCE
    assert "data:{mime};base64" not in APP_SOURCE


def test_project_package_generate_button_is_lazy_when_cache_missing_or_stale():
    assert 'label=t("generate_project_package")' in APP_SOURCE
    assert 'key="generate_project_package"' in APP_SOURCE
    assert 'if project_package is None:' in APP_SOURCE
    assert 'if st.button(' in APP_SOURCE
    assert 'with st.spinner(t("preparing_project_package_status"))' in APP_SOURCE
    assert "create_project_package_zip(" in APP_SOURCE

    generate_button_index = APP_SOURCE.index('key="generate_project_package"')
    package_build_index = APP_SOURCE.index("create_project_package_zip(")
    assert generate_button_index < package_build_index


def test_project_package_download_button_appears_when_cache_is_valid():
    assert 'else:\n            st.download_button(' in APP_SOURCE
    assert 'label=t("download_project_package")' in APP_SOURCE
    assert 'data=project_package' in APP_SOURCE
    assert "file_name=project_package_filename(st.session_state.language)" in APP_SOURCE
    assert "mime=PROJECT_PACKAGE_MIME" in APP_SOURCE
    assert 'key="download_project_package"' in APP_SOURCE


def test_project_package_cache_invalidates_when_signature_changes():
    assert "if st.session_state.project_package_cache and not get_cached_project_download(" in APP_SOURCE
    assert "st.session_state.project_package_cache = {}" in APP_SOURCE
    assert '"signature": project_download_signature' in APP_SOURCE
    assert '"data": project_package' in APP_SOURCE
    assert "st.rerun()" in APP_SOURCE


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

    assert APP_SOURCE.count("st.download_button(") >= len(normal_download_keys) + 1


def test_project_package_generate_translations_exist_and_download_labels_stay():
    assert '"generate_project_package":\n            "Generer projektpakke"' in TRANSLATIONS_SOURCE
    assert '"generate_project_package":\n            "Generate project package"' in TRANSLATIONS_SOURCE
    assert '"download_project_package":\n            "Download projektpakke"' in TRANSLATIONS_SOURCE
    assert '"download_project_package":\n            "Download project package"' in TRANSLATIONS_SOURCE
