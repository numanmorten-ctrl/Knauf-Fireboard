from io import BytesIO
from datetime import datetime
from itertools import islice
from zoneinfo import ZoneInfo

from translations import translations

from utils.constants import *

from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from utils.documentation_urls import FIREBOARD_INSTALLATION_SECTION_URL


def draw_project_description(can, description):
    """Fit literal project text into the description cell shared by both templates."""

    font_name, font_size = DESCRIPTION_FONT
    max_width = 332

    def width(text):
        return stringWidth(text, font_name, font_size)

    def wrapped_lines():
        text = str(description).replace("\r\n", "\n").replace("\r", "\n")
        for line in text.split("\n"):
            while width(line) > max_width:
                # Find the longest fitting prefix, including for unbroken URLs
                # and identifiers. Prefer a word boundary when one is available.
                low, high = 1, len(line)
                while low < high:
                    middle = (low + high + 1) // 2
                    if width(line[:middle]) <= max_width:
                        low = middle
                    else:
                        high = middle - 1
                split_at = line.rfind(" ", 0, low + 1)
                if split_at <= 0:
                    split_at = low
                yield line[:split_at]
                line = line[split_at:].lstrip(" ")
            yield line

    # A third line is enough to establish overflow; do not lay out the rest.
    lines = list(islice(wrapped_lines(), 3))
    if len(lines) > 2:
        last_line = lines[1].rstrip()
        while width(last_line + "…") > max_width:
            last_line = last_line[:-1].rstrip()
        lines = [lines[0], last_line + "…"]

    baselines = (488,) if len(lines) == 1 else (494.5, 485.5)
    can.saveState()
    can.setFont(font_name, font_size)
    for line, baseline in zip(lines, baselines):
        can.drawString(197, baseline, line)
    can.restoreState()


def apply_fireboard_installation_section_url(page):
    """Keep the PDF template installation-section link aligned with the shared URL."""

    for annotation_reference in page.get("/Annots", []):
        annotation = annotation_reference.get_object()
        action = annotation.get("/A")

        if action is None:
            continue

        uri = str(action.get("/URI", ""))

        if uri.startswith("https://knauf.com/api/download-center/v1/assets/"):
            action[NameObject("/URI")] = TextStringObject(
                FIREBOARD_INSTALLATION_SECTION_URL
            )

    return page


PROFILE_IMAGE_MAP = {

    "H-profiler": "images/h_profiles.png",
    "I-profiler": "images/i_profiles.png",
    "U-profiler": "images/u_profiles.png",

    "Kvadratiske rør varmvalsede": "images/shs_hot.png",
    "Kvadratiske rør koldvalsede": "images/shs_cold.png",

    "Rektangulære rør varmvalsede": "images/rhs_hot.png",
    "Rektangulære rør koldvalsede": "images/rhs_cold.png",

    "Cirkulære rør middelsvære": "images/chs_medium.png",
    "Cirkulære rør svære": "images/chs_heavy.png",

    "Andre profiler": "images/other_profiles.png",
}

def generate_single_pdf(
    calc,
    language,
    translations,
    session_state,
    PROFILE_IMAGE_MAP,

    PROJECT_X,
    PROJECT_Y,
    PROJECT_LINE_HEIGHT,

    CALC_X,
    CALC_Y,
    CALC_LINE_HEIGHT,

    RESULT_X,
    RESULT_Y,

    PAGE_X,
    PAGE_Y,

    PROFILE_IMAGE_X,
    PROFILE_IMAGE_Y,
    PROFILE_IMAGE_WIDTH,
    PROFILE_IMAGE_HEIGHT,

    PROFILE_TEXT_X,
    PROFILE_CATEGORY_TEXT_Y,
    PROFILE_TEXT_Y,
    PROFILE_CATEGORY_FONT,
    PROFILE_TEXT_FONT,

    PROJECT_FONT,
    CALC_FONT,
    RESULT_FONT,
    PAGE_FONT
):

    generation_date = datetime.now(ZoneInfo("Europe/Copenhagen")).strftime("%d-%m-%Y")
    output = PdfWriter()

    if language == "EN":
        template_path = "PDF_template_EN.pdf"
    else:
        template_path = "PDF_template.pdf"

    packet = BytesIO()

    can = canvas.Canvas(
        packet,
        pagesize=A4
    )

    PROJECT_Y_LOCAL = PROJECT_Y
    CALC_Y_LOCAL = CALC_Y
    RESULT_Y_LOCAL = RESULT_Y
    PAGE_Y_LOCAL = PAGE_Y

    def t(key):
        return translations[language].get(key, key)

    can.setFont(*PROJECT_FONT)

    can.drawString(
        PROJECT_X,
        PROJECT_Y_LOCAL,
        str(session_state.project_name)
    )

    can.drawString(
        PROJECT_X,
        PROJECT_Y_LOCAL - PROJECT_LINE_HEIGHT,
        str(session_state.prepared_by)
    )

    can.drawString(
        PROJECT_X,
        PROJECT_Y_LOCAL - (PROJECT_LINE_HEIGHT * 2),
        str(session_state.company)
    )

    can.drawString(
        PROJECT_X,
        PROJECT_Y_LOCAL - (PROJECT_LINE_HEIGHT * 3),
        generation_date
    )

    draw_project_description(can, session_state.description)

    can.setFont(*PROJECT_FONT)

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL,
        get_translated_category(calc["category"], language)
    )

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL - CALC_LINE_HEIGHT,
        str(calc["profile"])
    )

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 2),
        str(get_display_text(calc["montage"], t))
    )

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 3),
        format_sides_display(calc['sides'], t)
    )

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 4),
        f"{calc['fire_time']} {t('minutes')}"
    )

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 5),
        f"{calc['temperature']} °C"
    )

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 6),
        f"{calc['apv']} m²/m³"
    )

    image_path = PROFILE_IMAGE_MAP.get(
        calc["category"]
    )

    if image_path:

        can.drawImage(
            image_path,
            PROFILE_IMAGE_X,
            PROFILE_IMAGE_Y,
            width=PROFILE_IMAGE_WIDTH,
            height=PROFILE_IMAGE_HEIGHT,
            preserveAspectRatio=True,
            mask='auto'
        )

        can.setFillColor(
            colors.HexColor("#2d343c")
        )

        translated_category = get_translated_category(
            calc["category"],
            language
        )

        can.setFont(*PROJECT_FONT)

        can.drawCentredString(
            PROFILE_TEXT_X,
            PROFILE_CATEGORY_TEXT_Y,
            translated_category
        )

        can.setFont(*PROJECT_FONT)

        can.drawCentredString(
            PROFILE_TEXT_X,
            PROFILE_TEXT_Y,
            str(calc["profile"])
        )

    can.setFillColorRGB(
        1,
        1,
        1
    )

    can.setFont(*RESULT_FONT)

    try:
        thickness_val = int(
            float(calc.get("thickness", 0))
        )
    except Exception:
        thickness_val = 0

    result_text = (
    f"{t('profile_must_be_clad_with')} "
    f"{thickness_val} {t('mm')} "
    f"{t('knauf_fireboard')}"
)

    can.drawCentredString(
        RESULT_X,
        RESULT_Y_LOCAL,
        result_text
    )

    can.setFillColorRGB(
        0,
        0.62,
        0.89
    )

    can.setFont(*PROJECT_FONT)

    can.drawString(
        PAGE_X,
        PAGE_Y_LOCAL,
        "1"
    )

    can.save()

    packet.seek(0)

    overlay_pdf = PdfReader(packet)

    template_pdf = PdfReader(
        open(template_path, "rb")
    )

    base_page = apply_fireboard_installation_section_url(
        template_pdf.pages[0]
    )

    base_page.merge_page(
        overlay_pdf.pages[0]
    )

    output.add_page(base_page)

    output_stream = BytesIO()

    output.write(output_stream)

    output_stream.seek(0)

    return output_stream

CATEGORY_TO_TRANSLATION_KEY = {
    "H-profiler": "h_profiles",
    "I-profiler": "i_profiles",
    "U-profiler": "u_profiles",
    "Kvadratiske rør varmvalsede": "shs_hot",
    "Kvadratiske rør koldvalsede": "shs_cold",
    "Rektangulære rør varmvalsede": "rhs_hot",
    "Rektangulære rør koldvalsede": "rhs_cold",
    "Cirkulære rør middelsvære": "chs_medium",
    "Cirkulære rør svære": "chs_heavy",
    "Andre profiler": "other_profiles",
}

def get_translated_category(category, language):
    key = CATEGORY_TO_TRANSLATION_KEY.get(category)
    if key:
        return translations[language].get(key, category)
    return category


def get_display_text(value, t):

    mapping = {
        "Klammeløsning": "clamping_solution",
        "Bjælkeprofil eller PHL profil": "beam_or_phl_profile"
    }

    translation_key = mapping.get(value)

    if translation_key:
        return t(translation_key)

    return value

def format_sides_display(value, t):
    if value is None:
        return ""

    text = str(value).strip()
    if not text:
        return ""

    translated_sides = t("sides")
    if translated_sides and translated_sides.lower() in text.lower():
        return text

    return f"{text} {translated_sides}"
    
def generate_complete_pdf(
    calculations,
    language,
    session_state,
    t,

    PROFILE_IMAGE_MAP,

    PROJECT_X,
    PROJECT_Y,
    PROJECT_LINE_HEIGHT,

    CALC_X,
    CALC_Y,
    CALC_LINE_HEIGHT,

    RESULT_X,
    RESULT_Y,

    PAGE_X,
    PAGE_Y,

    PROFILE_IMAGE_X,
    PROFILE_IMAGE_Y,
    PROFILE_IMAGE_WIDTH,
    PROFILE_IMAGE_HEIGHT,

    PROFILE_TEXT_X,
    PROFILE_CATEGORY_TEXT_Y,
    PROFILE_TEXT_Y,
    PROFILE_CATEGORY_FONT,
    PROFILE_TEXT_FONT,

    PROJECT_FONT,
    CALC_FONT,
    RESULT_FONT,
    PAGE_FONT
):

    generation_date = datetime.now(ZoneInfo("Europe/Copenhagen")).strftime("%d-%m-%Y")
    output = PdfWriter()

    if language == "EN":
        template_path = "PDF_template_EN.pdf"
    else:
        template_path = "PDF_template.pdf"

    for page_number, calc in enumerate(
        calculations,
        start=1
    ):

        packet = BytesIO()

        can = canvas.Canvas(
            packet,
            pagesize=A4
        )

        PROJECT_Y_LOCAL = PROJECT_Y
        CALC_Y_LOCAL = CALC_Y
        RESULT_Y_LOCAL = RESULT_Y
        PAGE_Y_LOCAL = PAGE_Y

        def t(key):
            return translations[language].get(key, key)

        # PROJECT INFO

        can.setFont(*PROJECT_FONT)

        can.drawString(
            PROJECT_X,
            PROJECT_Y_LOCAL,
            str(session_state.project_name)
        )

        can.drawString(
            PROJECT_X,
            PROJECT_Y_LOCAL - PROJECT_LINE_HEIGHT,
            str(session_state.prepared_by)
        )

        can.drawString(
            PROJECT_X,
            PROJECT_Y_LOCAL - (PROJECT_LINE_HEIGHT * 2),
            str(session_state.company)
        )

        can.drawString(
            PROJECT_X,
            PROJECT_Y_LOCAL - (PROJECT_LINE_HEIGHT * 3),
            generation_date
        )

        draw_project_description(can, session_state.description)

        # CALCULATION

        can.setFont(*PROJECT_FONT)

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL,
            get_translated_category(calc["category"], language)
        )

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL - CALC_LINE_HEIGHT,
            str(calc["profile"])
        )

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 2),
            str(get_display_text(calc["montage"], t))
        )

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 3),
            format_sides_display(calc['sides'], t)
        )

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 4),
            f"{calc['fire_time']} {t('minutes')}"
        )

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 5),
            f"{calc['temperature']} °C"
        )

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 6),
            f"{calc['apv']} m²/m³"
        )

        # PROFILE IMAGE

        image_path = PROFILE_IMAGE_MAP.get(
            calc["category"]
        )

        if image_path:

            can.drawImage(
                image_path,
                PROFILE_IMAGE_X,
                PROFILE_IMAGE_Y,
                width=PROFILE_IMAGE_WIDTH,
                height=PROFILE_IMAGE_HEIGHT,
                preserveAspectRatio=True,
                mask='auto'
            )

            can.setFillColor(
                colors.HexColor("#2d343c")
            )

            translated_category = get_translated_category(
                calc["category"],
                language
            )

            can.setFont(*PROJECT_FONT)

            can.drawCentredString(
                PROFILE_TEXT_X,
                PROFILE_CATEGORY_TEXT_Y,
                translated_category
            )

            can.setFont(*PROJECT_FONT)

            can.drawCentredString(
                PROFILE_TEXT_X,
                PROFILE_TEXT_Y,
                str(calc["profile"])
            )

        # RESULT

        can.setFillColorRGB(
            1,
            1,
            1
        )

        can.setFont(*RESULT_FONT)

        try:
            thickness_val = int(
                float(calc.get("thickness", 0))
            )
        except Exception:
            thickness_val = 0

        result_text = (
            f"{t('profile_must_be_clad_with')} "
            f"{thickness_val} {t('mm')} "
            f"{t('knauf_fireboard')}"
        )

        can.drawCentredString(
            RESULT_X,
            RESULT_Y_LOCAL,
            result_text
        )

        # PAGE NUMBER

        can.setFillColorRGB(
            0,
            0.62,
            0.89
        )

        can.setFont(*PROJECT_FONT)

        can.drawString(
            PAGE_X,
            PAGE_Y_LOCAL,
            f"{page_number}"
        )

        can.save()

        # MERGE TEMPLATE

        packet.seek(0)

        overlay_pdf = PdfReader(packet)

        template_pdf = PdfReader(
            open(template_path, "rb")
        )

        base_page = apply_fireboard_installation_section_url(
            template_pdf.pages[0]
        )

        base_page.merge_page(
            overlay_pdf.pages[0]
        )

        output.add_page(base_page)

    output_stream = BytesIO()

    output.write(output_stream)

    output_stream.seek(0)

    return output_stream
