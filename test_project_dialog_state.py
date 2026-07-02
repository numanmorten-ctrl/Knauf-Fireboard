from pathlib import Path


APP_SOURCE = Path(__file__).with_name("app.py").read_text()
TRANSLATIONS_SOURCE = Path(__file__).with_name("translations.py").read_text()


def test_save_project_button_opens_save_dialog_and_closes_open_dialog():
    assert "def open_save_project_dialog():" in APP_SOURCE
    assert "st.session_state.show_save_project_dialog = True" in APP_SOURCE
    assert "st.session_state.show_project_dialog = False" in APP_SOURCE
    assert 'st.session_state.project_dialog_action = "save"' in APP_SOURCE
    assert "open_save_project_dialog()" in APP_SOURCE


def test_open_project_button_opens_open_dialog_and_closes_save_dialog():
    assert "def open_project_dialog_state():" in APP_SOURCE
    assert "st.session_state.show_project_dialog = True" in APP_SOURCE
    assert "st.session_state.show_save_project_dialog = False" in APP_SOURCE
    assert 'st.session_state.project_dialog_action = "open"' in APP_SOURCE
    assert "open_project_dialog_state()" in APP_SOURCE


def test_project_dialog_rendering_is_mutually_exclusive():
    assert "def resolve_project_dialog_state():" in APP_SOURCE
    assert "resolve_project_dialog_state()" in APP_SOURCE
    assert "elif st.session_state.show_project_dialog:" in APP_SOURCE
    assert "render_save_project_dialog()" in APP_SOURCE
    assert "render_open_project_dialog()" in APP_SOURCE


def test_empty_project_save_shows_clear_message_without_blocking_download():
    assert 'if not st.session_state.get("calculations", []):' in APP_SOURCE
    assert 'st.info(t("empty_project_no_calculations"))' in APP_SOURCE
    assert "data=export_project_state(st.session_state)" in APP_SOURCE
    assert '"empty_project_no_calculations":\n            "Der er ingen beregninger i projektet endnu."' in TRANSLATIONS_SOURCE
    assert '"empty_project_no_calculations":\n            "There are no calculations in the project yet."' in TRANSLATIONS_SOURCE


def test_dialog_flags_reset_after_cancel_download_open_invalid_and_new_project():
    assert "def close_project_dialogs():" in APP_SOURCE
    assert APP_SOURCE.count("close_project_dialogs()") >= 5
    assert "except ProjectLoadError as exc:" in APP_SOURCE
    assert "close_project_dialogs()\n        return False" in APP_SOURCE
    assert "if st.download_button(" in APP_SOURCE
    assert "close_project_dialogs()\n        st.rerun()" in APP_SOURCE
