from io import BytesIO
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from pypdf import PdfReader, PdfWriter

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
