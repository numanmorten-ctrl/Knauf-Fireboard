"""Exercise real PDF outputs, including their text coordinates and templates."""

import ast
import inspect
from copy import deepcopy
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from pypdf import PdfReader
from reportlab.pdfbase.pdfmetrics import getAscentDescent, stringWidth

from translations import translations
from utils import constants, pdf_generator as pdf
from utils.documentation_urls import FIREBOARD_INSTALLATION_SECTION_URL
from utils.project_package import build_project_download_signature, get_cached_project_download


ROOT = Path(__file__).resolve().parent
CALCULATION = dict(
    category="H-profiler", profile="HEB100", montage="Klammeløsning", sides=3,
    fire_time=60, temperature=550, apv=116, thickness=20,
)


@pytest.fixture(params=[("DA", "single"), ("EN", "single"), ("DA", "combined"), ("EN", "combined")])
def report(request):
    language, kind = request.param
    function = pdf.generate_single_pdf if kind == "single" else pdf.generate_complete_pdf

    def generate(description="Description", instant="2026-11-04T12:00:00+00:00"):
        state = SimpleNamespace(
            project_name="Project marker", prepared_by="Author marker",
            company="Company marker", description=description, report_date="01-01-1900",
        )
        before = deepcopy(vars(state))
        calculations = [dict(CALCULATION), dict(CALCULATION, profile="HEB200")]
        supplied = dict(
            calc=calculations[0], calculations=calculations, language=language,
            session_state=state, translations=translations,
            PROFILE_IMAGE_MAP=pdf.PROFILE_IMAGE_MAP, t=translations[language].get,
        )
        kwargs = {
            name: supplied[name] if name in supplied else getattr(constants, name)
            for name in inspect.signature(function).parameters
        }
        local_times = []

        def now(tz):
            assert tz.key == "Europe/Copenhagen"
            value = datetime.fromisoformat(instant).astimezone(tz)
            # A second call would cross a date boundary. Combined reports must
            # capture one timestamp, regardless of how long later pages take.
            if local_times:
                value += timedelta(days=len(local_times))
            local_times.append(value)
            return value

        with patch.object(pdf, "datetime") as clock:
            clock.now.side_effect = now
            result = function(**kwargs).getvalue()
        assert clock.now.call_count == 1
        assert vars(state) == before
        assert calculations == [CALCULATION, dict(CALCULATION, profile="HEB200")]
        return PdfReader(BytesIO(result)), result, local_times[0]

    return language, kind, generate


def text_positions(page):
    positions = []

    def visit(text, cm, tm, font, size):
        if text.strip():
            x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
            y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
            positions.append((text.rstrip("\n"), x, y, size))

    page.extract_text(visitor_text=visit)
    return positions


def link_details(page):
    links = []
    for reference in page.get("/Annots", []):
        annotation = reference.get_object()
        if annotation.get("/Subtype") == "/Link":
            action = annotation["/A"]
            links.append((str(action["/URI"]), list(annotation["/Rect"]), action["/S"]))
    return links


@pytest.mark.filterwarnings("error::DeprecationWarning:pypdf.*")
def test_template_merge_preserves_content_links_and_images(report):
    """Exercise real merging: pypdf 7 rejects reader-owned destination pages."""
    language, kind, generate = report
    template = PdfReader(ROOT / ("PDF_template_EN.pdf" if language == "EN" else "PDF_template.pdf")).pages[0]
    expected_links = [
        (FIREBOARD_INSTALLATION_SECTION_URL if uri.startswith("https://knauf.com/api/download-center/v1/assets/") else uri, rect, action)
        for uri, rect, action in link_details(template)
    ]
    assert expected_links
    assert any(uri == FIREBOARD_INSTALLATION_SECTION_URL for uri, _, _ in expected_links)
    template_images = [image.data for image in template.images]
    template_positions = text_positions(template)

    # Repeat generation to catch template mutation or overlays leaking between
    # pages/reports. Reopen the serialized PDFs to verify their actual contents.
    for _ in range(2):
        reader, _, _ = generate("First line\nSecond line")
        assert len(reader.pages) == (1 if kind == "single" else 2)
        for number, page in enumerate(reader.pages, 1):
            assert link_details(page) == expected_links
            assert text_positions(page)[:len(template_positions)] == template_positions
            assert list(page.mediabox) == list(template.mediabox)
            assert list(page.cropbox) == list(template.cropbox)
            assert page.rotation == template.rotation
            images = [image.data for image in page.images]
            assert all(image in images for image in template_images)
            assert len(images) == len(template_images) + 1  # Profile illustration.
            text = page.extract_text()
            assert text.count("Project marker") == 1
            profile, other = ("HEB100", "HEB200") if number == 1 else ("HEB200", "HEB100")
            assert text.count(profile) == 2  # Calculation field and image caption.
            assert other not in text
            t = translations[language].get
            for value in (
                pdf.get_translated_category(CALCULATION["category"], language),
                pdf.get_display_text(CALCULATION["montage"], t),
                pdf.format_sides_display(CALCULATION["sides"], t),
                f"60 {t('minutes')}",
                f"{t('profile_must_be_clad_with')} 20 {t('mm')} {t('knauf_fireboard')}",
            ):
                assert value in text


@pytest.mark.parametrize("instant,date,hour,offset", [
    ("2026-01-01T23:30:00+00:00", "02-01-2026", 0, 1),
    ("2026-07-01T22:30:00+00:00", "02-07-2026", 0, 2),
    ("2026-03-28T23:30:00+00:00", "29-03-2026", 0, 1),
    ("2026-03-29T00:30:00+00:00", "29-03-2026", 1, 1),
    ("2026-03-29T01:30:00+00:00", "29-03-2026", 3, 2),
    ("2026-10-24T22:30:00+00:00", "25-10-2026", 0, 2),
    ("2026-10-25T00:30:00+00:00", "25-10-2026", 2, 2),
    ("2026-10-25T01:30:00+00:00", "25-10-2026", 2, 1),
])
def test_copenhagen_generation_date_on_every_page(report, instant, date, hour, offset):
    _, kind, generate = report
    reader, _, local_time = generate(instant=instant)
    assert local_time.hour == hour
    assert local_time.utcoffset() == timedelta(hours=offset)
    assert len(reader.pages) == (1 if kind == "single" else 2)
    for page in reader.pages:
        assert (date, 197, 508, 9) in text_positions(page)
        assert "01-01-1900" not in page.extract_text()


@pytest.mark.parametrize("description,line_count,overflow", [
    ("", 0, False),
    ("Short description", 1, False),
    ("ÆØÅ æøå <steel> & beams > plates", 1, False),
    ("Alpha " * 18, 2, False),
    ("Alpha " * 60, 2, True),
    ("First\nSecond", 2, False),
    ("First\r\nSecond", 2, False),
    ("Første <stålrør> & bjælker\nAnden > række", 2, False),
    ("First\nSecond\nThird", 2, True),
    ("W" * 50, 2, False),
    ("W" * 100, 2, True),
    ("https://example.com/" + "identifier" * 30, 2, True),
])
def test_description_layout_in_both_templates(report, description, line_count, overflow):
    language, kind, generate = report
    reader, _, _ = generate(description)
    template = PdfReader(ROOT / ("PDF_template_EN.pdf" if language == "EN" else "PDF_template.pdf")).pages[0]
    # Verify the actual template still has the expected description value cell.
    cells = []

    def rectangle(op, args, cm, tm):
        if op == b"re" and len(args) == 4:
            x, y, width, height = map(float, args)
            if abs(x - 192.65) < 0.01 and 482 <= y < 483 and height > 19:
                cells.append((x, y, width, height))

    template.extract_text(visitor_operand_before=rectangle)
    assert cells
    cell_x, cell_y, cell_width, cell_height = cells[0]
    ascent, descent = getAscentDescent("Helvetica", 9)
    for number, page in enumerate(reader.pages, 1):
        positions = text_positions(page)
        lines = [(text, x, y, size) for text, x, y, size in positions if x == 197 and 482 <= y <= 502]
        assert len(lines) == line_count
        assert [y for _, _, y, _ in lines] == ({0: [], 1: [488], 2: [494.5, 485.5]}[line_count])
        for text, x, y, size in lines:
            assert size == 9
            assert stringWidth(text, "Helvetica", size) <= 332
            assert cell_x < x and x + stringWidth(text, "Helvetica", size) < cell_x + cell_width
            assert cell_y < y + descent < y + ascent < cell_y + cell_height
            assert "■" not in text
        if overflow:
            assert lines[-1][0].endswith("…")
        elif line_count:
            assert not lines[-1][0].endswith("…")
            if "\n" in description:
                assert [line[0] for line in lines] == description.replace("\r\n", "\n").split("\n")
            elif " " not in description:
                assert "".join(line[0] for line in lines) == description
            else:
                assert " ".join(line[0] for line in lines).split() == description.split()
        # Surrounding project/calculation fields and page numbering retain
        # their existing positions, font sizes, and contents.
        profile = "HEB100" if number == 1 else "HEB200"
        for field in [
            ("Project marker", 197, 568, 9), ("Author marker", 197, 548, 9),
            ("Company marker", 197, 528, 9), ("04-11-2026", 197, 508, 9),
            (profile, 197, 417, 9), ("550 °C", 197, 341, 9),
            ("116 m²/m³", 197, 322, 9), (str(number), 285, 22, 9),
        ]:
            assert field in positions
        assert any("20 mm Knauf Fireboard" in text and y == 238 and size == 18 for text, _, y, size in positions)
        assert list(page.mediabox) == list(template.mediabox)
    assert len(reader.pages) == (1 if kind == "single" else 2)


@pytest.mark.parametrize("text,expected", [
    ("First\n\nThird", ["First", "…"]),
    ("\nSecond", ["", "Second"]),
    ("First\rSecond", ["First", "Second"]),
    (" Short literal <>& æøå ", [" Short literal <>& æøå "]),
])
def test_explicit_blank_lines_and_literal_text(text, expected):
    can = Mock()
    pdf.draw_project_description(can, text)
    assert [call.args[2] for call in can.drawString.call_args_list] == expected
    can.setFont.assert_called_once_with("Helvetica", 9)
    can.saveState.assert_called_once()
    can.restoreState.assert_called_once()


def test_cached_report_retains_its_generation_date(report):
    language, _, generate = report
    _, original, _ = generate(instant="2026-01-01T12:00:00+00:00")
    project = dict(calculations=[CALCULATION], combined_materials={}, language=language,
                   project_details={"description": "Description"})
    signature = build_project_download_signature(**project)
    cache = dict(signature=signature, data=original)
    with patch.object(pdf, "datetime") as clock:
        clock.now.return_value = datetime(2026, 1, 2)
        cached = get_cached_project_download(cache, build_project_download_signature(**project))
        clock.now.assert_not_called()
    assert cached is original
    for page in PdfReader(BytesIO(cached)).pages:
        assert ("01-01-2026", 197, 508, 9) in text_positions(page)


def test_result_date_input_removed_without_removing_other_project_inputs():
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    labels = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"text_input", "text_area"} and node.args:
            label = node.args[0]
            if isinstance(label, ast.Call) and isinstance(label.func, ast.Name) and label.func.id == "t":
                labels.add(ast.literal_eval(label.args[0]))
    assert "date" not in labels
    assert {"project", "prepared_by", "company", "description"} <= labels
