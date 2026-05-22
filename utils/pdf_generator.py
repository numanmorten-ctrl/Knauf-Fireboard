from io import BytesIO
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

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

# ---------------------------------------------------
# PDF COORDINATES
# ---------------------------------------------------

# PROJECT INFO

PROJECT_X = 197
PROJECT_Y = 570
PROJECT_LINE_HEIGHT = 20

# DESCRIPTION

DESCRIPTION_Y = 482
DESCRIPTION_MAX_CHARS = 72

# CALCULATION

CALC_X = 197
CALC_Y = 436
CALC_LINE_HEIGHT = 19

# RESULT

RESULT_X = 287
RESULT_Y = 238

# PAGE NUMBER

PAGE_X = 292
PAGE_Y = 20.4

# PROFILE IMAGE

PROFILE_IMAGE_X = 430
PROFILE_IMAGE_Y = 730
PROFILE_IMAGE_WIDTH = 110
PROFILE_IMAGE_HEIGHT = 110

PROFILE_TEXT_X = 485
PROFILE_CATEGORY_TEXT_Y = 720
PROFILE_TEXT_Y = 708
PROFILE_CATEGORY_FONT = 9
PROFILE_TEXT_FONT = 11

# FONT SIZES

PROJECT_FONT = 9
DESCRIPTION_FONT = 9
CALC_FONT = 9
RESULT_FONT = 14
PAGE_FONT = 10

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

    if language == "EN":
        PROJECT_Y_LOCAL = 538.9
        CALC_Y_LOCAL = CALC_Y
        RESULT_Y_LOCAL = 187.8
        PAGE_Y_LOCAL = 20.4
    else:
        PROJECT_Y_LOCAL = 560.7
        CALC_Y_LOCAL = 418.5
        RESULT_Y_LOCAL = 225.3
        PAGE_Y_LOCAL = 20.4

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
        datetime.now().strftime("%d-%m-%Y")
    )

    can.drawString(
        PROJECT_X,
        PROJECT_Y_LOCAL - (PROJECT_LINE_HEIGHT * 4),
        str(session_state.description)
    )

    can.setFont(*PROJECT_FONT)

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL,
        get_translated_category(calc["category"])
    )

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL - CALC_LINE_HEIGHT,
        str(calc["profile"])
    )

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 2),
        str(get_display_text(calc["montage"]))
    )

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 3),
        format_sides_display(calc['sides'])
    )

    can.drawString(
        CALC_X,
        CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 4),
        f"{calc['fire_time']} min"
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
            calc["category"]
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

    can.setFont(*PROJECT_FONT)

    try:
        thickness_val = int(
            float(calc.get("thickness", 0))
        )
    except Exception:
        thickness_val = 0

    result_text = (
        f"Profile must be clad with "
        f"{thickness_val} mm "
        f"Knauf Fireboard"
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

    base_page = template_pdf.pages[0]

    base_page.merge_page(
        overlay_pdf.pages[0]
    )

    output.add_page(base_page)

    output_stream = BytesIO()

    output.write(output_stream)

    output_stream.seek(0)

    return output_stream

def get_translated_category(category):
    return category


def get_display_text(value):
    return value


def format_sides_display(value):
    return str(value)
    
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

        if language == "EN":
            PROJECT_Y_LOCAL = 538.9
            CALC_Y_LOCAL = CALC_Y
            RESULT_Y_LOCAL = 187.8
            PAGE_Y_LOCAL = 20.4
        else:
            PROJECT_Y_LOCAL = 560.7
            CALC_Y_LOCAL = 418.5
            RESULT_Y_LOCAL = 225.3
            PAGE_Y_LOCAL = 20.4

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
            datetime.now().strftime("%d-%m-%Y")
        )

        can.drawString(
            PROJECT_X,
            PROJECT_Y_LOCAL - (PROJECT_LINE_HEIGHT * 4),
            str(session_state.description)
        )

        # CALCULATION

        can.setFont(*PROJECT_FONT)

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL,
            get_translated_category(calc["category"])
        )

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL - CALC_LINE_HEIGHT,
            str(calc["profile"])
        )

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 2),
            str(get_display_text(calc["montage"]))
        )

        can.drawString(
            CALC_X,
            CALC_Y_LOCAL - (CALC_LINE_HEIGHT * 3),
            format_sides_display(calc['sides'])
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
                calc["category"]
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

        can.setFont(*PROJECT_FONT)

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

        base_page = template_pdf.pages[0]

        base_page.merge_page(
            overlay_pdf.pages[0]
        )

        output.add_page(base_page)

    output_stream = BytesIO()

    output.write(output_stream)

    output_stream.seek(0)

    return output_stream
