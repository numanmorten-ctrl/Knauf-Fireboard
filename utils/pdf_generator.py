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
