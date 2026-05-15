import base64
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

import streamlit as st
import pandas as pd
import requests

import streamlit as st
import pandas as pd
import requests

from translations import translations

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Image

# ---------------------------------------------------
# KNAUF THEME
# ---------------------------------------------------

st.markdown("""
<style>

/* ---------------------------------------------------
MAIN LAYOUT
--------------------------------------------------- */

.stApp {

    background-color: #f3f5f7;
}

.block-container {

    max-width: 1400px;

    padding-top: 4.2rem !important;

    padding-left: 1.5rem;

    padding-right: 1.5rem;

    padding-bottom: 1rem;
}

/* ---------------------------------------------------
TYPOGRAPHY
--------------------------------------------------- */

h1, h2, h3 {

    color: #2d343c !important;

    font-weight: 700 !important;
}
h1 {

    color: #2d343c !important;

    font-weight: 700 !important;

    font-size: 38px !important;
}

/* INPUT LABELS */

label {

    color: #3e4650 !important;

    font-size: 15px !important;

    font-weight: 500 !important;
}
/* CUSTOM MARKDOWN LABELS */

div[data-testid="stMarkdownContainer"] p {

    color: #3e4650 !important;

    font-size: 15px !important;

    font-weight: 500 !important;

    margin-bottom: 0.3rem !important;
}
/* ---------------------------------------------------
BUTTONS
--------------------------------------------------- */

div.stButton > button,
div.stDownloadButton > button {

    width: 100%;

    min-height: 32px;

    border-radius: 0 !important;

    border: 1px solid #b8c2cc !important;

    font-size: 14px;

    font-weight: 600;

    transition: all 0.15s ease;

    box-shadow: none !important;

    outline: none !important;
}

/* NORMAL BUTTON TEKST */

div.stButton > button:not([kind="primary"]),
div.stDownloadButton > button {

    color: #003b7a !important;
}

/* ---------------------------------------------------
BUTTON HOVER
--------------------------------------------------- */

div.stButton > button:hover,
div.stDownloadButton > button:hover {

    border-color: #009fe3 !important;

    background-color: #f5fbff !important;

    color: #003b7a !important;
}

/* ---------------------------------------------------
PRIMARY BUTTON
--------------------------------------------------- */

button[kind="primary"] {

    background-color: #009fe3 !important;

    border-color: #009fe3 !important;

    color: white !important;
}

/* ---------------------------------------------------
PRIMARY BUTTON HOVER
--------------------------------------------------- */

button[kind="primary"]:hover {

    background-color: #0089c7 !important;

    border-color: #0089c7 !important;

    color: white !important;
}

/* ---------------------------------------------------
ACTIVE SIDEBAR CALCULATION
--------------------------------------------------- */

section[data-testid="stSidebar"] button[kind="primary"] {

    background:#003b7a !important;

    border:1px solid #003b7a !important;

    color:white !important;

    font-weight:700 !important;

    box-shadow:none !important;
}

/* ---------------------------------------------------
INPUTS
--------------------------------------------------- */

.stTextInput > div > div,
.stTextArea > div > div,
.stNumberInput > div > div,
.stSelectbox > div > div,
div[data-baseweb="select"] > div,
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="textarea"] {

    background: white !important;

    border: 1px solid #b8c2cc !important;

    border-radius: 0 !important;

    box-shadow: none !important;

    outline: none !important;

    min-height: 44px !important;
}

/* ---------------------------------------------------
INPUT INNER
--------------------------------------------------- */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {

    background: white !important;

    color: #2d343c !important;

    -webkit-text-fill-color: #2d343c !important;

    caret-color: #003b7a !important;

    border: none !important;

    outline: none !important;

    box-shadow: none !important;

    appearance: none !important;

    -webkit-appearance: none !important;

    -moz-appearance: none !important;
}

/* ---------------------------------------------------
INPUT FOCUS
--------------------------------------------------- */

.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within,
.stNumberInput > div > div:focus-within,
.stSelectbox > div > div:focus-within,
div[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"]:focus-within,
[data-baseweb="base-input"]:focus-within,
[data-baseweb="textarea"]:focus-within {

    border: 1px solid #009fe3 !important;

    box-shadow: none !important;

    outline: none !important;
}

/* ---------------------------------------------------
REMOVE RED INVALID STATE
--------------------------------------------------- */

input:invalid,
textarea:invalid {

    box-shadow: none !important;
}

/* ---------------------------------------------------
HIDE NUMBER BUTTONS
--------------------------------------------------- */

.stNumberInput button {

    display: none !important;
}

/* ---------------------------------------------------
SELECTBOX DROPDOWN
--------------------------------------------------- */

/* Main select container */

div[data-baseweb="select"] > div {

    background: white !important;

    color: #2d343c !important;
}

/* Selected value */

div[data-baseweb="select"] span {

    color: #2d343c !important;

    opacity: 1 !important;
}

/* Input field inside select */

div[data-baseweb="select"] input {

    color: #2d343c !important;

    caret-color: #003b7a !important;

    background: transparent !important;
}

/* Dropdown popup */

div[data-baseweb="popover"] {

    background: white !important;

    border: 1px solid #b8c2cc !important;

    border-radius: 0 !important;

    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
}

/* Dropdown list */

ul {

    background: white !important;
}

/* Dropdown items */

li {

    background: white !important;

    color: #2d343c !important;
}

/* Hover */

li:hover {

    background: #eef7fd !important;

    color: #003b7a !important;
}
/* ---------------------------------------------------
INFO / SUCCESS BOXES
--------------------------------------------------- */

div[data-baseweb="notification"] {

    border: 1px solid #b8c2cc !important;

    border-radius: 0 !important;

    box-shadow: none !important;
}

/* ---------------------------------------------------
DIVIDERS
--------------------------------------------------- */

hr {

    border-color: #d9dde3 !important;
}

/* ---------------------------------------------------
STREAMLIT HEADER
--------------------------------------------------- */

header[data-testid="stHeader"] {

    position: fixed !important;

    top: 0 !important;

    left: 0 !important;

    right: 0 !important;

    height: 4.05rem !important;

    background: white !important;

    border-bottom: 1px solid #cfd6dd !important;

    box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;

    z-index: 999999 !important;
}

/* Toolbar */

div[data-testid="stToolbar"] {

    background: transparent !important;
}

/* Header shadow layer */

header[data-testid="stHeader"]::after {

    content: "";

    position: absolute;

    left: 0;

    right: 0;

    bottom: -6px;

    height: 6px;

    background: linear-gradient(
        to bottom,
        rgba(0,0,0,0.10),
        rgba(0,0,0,0)
    );

    pointer-events: none;
}

/* ---------------------------------------------------
SIDEBAR
--------------------------------------------------- */

section[data-testid="stSidebar"] {

    background-color: white;

    border-right: 1px solid #d9dde3;

    margin-top: 4.05rem !important;

    z-index: 0 !important;

    position: relative !important;
}

/* ---------------------------------------------------
UNIFY ALL BORDERS
--------------------------------------------------- */

.stButton > button,
.stDownloadButton > button,
.stTextInput > div > div,
.stTextArea > div > div,
.stNumberInput > div > div,
.stSelectbox > div > div,
div[data-baseweb="select"] > div,
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="textarea"] {

    border: 1px solid #b8c2cc !important;

    border-radius: 0 !important;

    box-shadow: none !important;

    outline: none !important;

    background: white !important;

    box-sizing: border-box !important;
}

/* FORCE SAME VISUAL THICKNESS */

.stTextInput,
.stTextArea,
.stNumberInput,
.stSelectbox,
.stButton,
.stDownloadButton {

    box-sizing: border-box !important;
}

/* REMOVE EXTRA INNER BORDERS */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {

    border: none !important;

    box-shadow: none !important;

    background: transparent !important;
}

/* REMOVE BASEWEB SHADOW LAYERS */

[data-baseweb="input"]::before,
[data-baseweb="base-input"]::before,
[data-baseweb="textarea"]::before,
[data-baseweb="select"]::before {

    display: none !important;
}
/* ---------------------------------------------------
FINAL BASEWEB INPUT FIX
--------------------------------------------------- */

.stTextInput > div,
.stNumberInput > div,
.stTextArea > div {

    border: none !important;

    background: transparent !important;

    box-shadow: none !important;
}

.stTextInput > div > div,
.stNumberInput > div > div,
.stTextArea > div > div {

    margin: 0 !important;

    padding: 0 !important;

    border: 1px solid #b8c2cc !important;

    background: white !important;

    box-shadow: none !important;
}
/* ---------------------------------------------------
AKTIV SIDEBAR BEREGNING
--------------------------------------------------- */

section[data-testid="stSidebar"] button[kind="primary"] {

    background-color: #003b7a !important;

    border: 1px solid #003b7a !important;

    box-shadow: none !important;
}

/* SELVE LABEL-CONTAINEREN */

section[data-testid="stSidebar"] button[kind="primary"] p {

    color: #ffffff !important;

    font-weight: 700 !important;

    opacity: 1 !important;

    margin: 0 !important;
}

/* STREAMLIT LABEL WRAPPER */

section[data-testid="stSidebar"] button[kind="primary"] div[data-testid="stMarkdownContainer"] {

    color: #ffffff !important;
}

/* ALT INDHOLD */

section[data-testid="stSidebar"] button[kind="primary"] * {

    color: #ffffff !important;

    -webkit-text-fill-color: #ffffff !important;
}

/* HOVER */

section[data-testid="stSidebar"] button[kind="primary"]:hover {

    background-color: #002e5f !important;

    border: 1px solid #002e5f !important;
}
/* ---------------------------------------------------
DIVIDER SPACING
--------------------------------------------------- */

hr {

    border-color: #d9dde3 !important;

    margin-top: 0rem !important;

    margin-bottom: 0.9rem !important;
}

/* Mindre afstand efter headers */

h1, {

    margin-top: -4rem !important;

    margin-bottom: 0.2rem !important;

    padding-bottom: 0rem !important;
}

h2, h3 {

    margin-top: 0rem !important;

    margin-bottom: 0.2rem !important;

    padding-bottom: 0rem !important;
}
/* Mindre afstand mellem elementer */

div[data-testid="stVerticalBlock"] {

    gap: 0.8rem !important;
}

/* Mindre afstand før/efter subheaders */

div[data-testid="stHeading"] {

    margin-bottom: 0.2rem !important;
}

/* Mindre afstand ved buttons */

div.stButton {

    margin-top: 0rem !important;

    margin-bottom: 0rem !important;
}

/* Mindre spacing omkring markdown/html blocks */

.element-container {

    margin-bottom: 0.5rem !important;
}
/* ---------------------------------------------------
APV METHOD ACTIVE BUTTONS
--------------------------------------------------- */

div.stButton > button[kind="primary"] {

    background-color: #003b7a !important;

    border: 1px solid #003b7a !important;

    color: white !important;

    font-weight: 700 !important;
}

div.stButton > button[kind="primary"] * {

    color: white !important;

    -webkit-text-fill-color: white !important;
}
/* ---------------------------------------------------
ALIGN CALCULATE BUTTON HEIGHT
--------------------------------------------------- */

div.stButton > button {

    min-height: 44px !important;

    margin-top: 0px !important;
}
/* ---------------------------------------------------
SELECTBOX DROPDOWN TRIANGLE
--------------------------------------------------- */

/* skjul standard ikon */

div[data-baseweb="select"] svg {

    display: none !important;
}

/* select container */

div[data-baseweb="select"] > div {

    position: relative !important;
}

/* custom trekant */

div[data-baseweb="select"] > div::after {

    content: "";

    position: absolute;

    right: 18px;

    top: 50%;

    transform: translateY(-35%);

    width: 0;
    height: 0;

    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #7f7f7f;

    pointer-events: none;
}

/* ---------------------------------------------------
LANGUAGE ICON COLUMN
--------------------------------------------------- */

div[data-testid="column"]:nth-last-child(2) {

    display: flex !important;

    align-items: flex-end !important;
}

/* ---------------------------------------------------
FJERN STREAMLIT SPACING I COL4
--------------------------------------------------- */

div[data-testid="column"]:nth-last-child(2)
div[data-testid="stMarkdownContainer"] {

    margin-bottom: 0 !important;

    padding-bottom: 0 !important;
}

/* ---------------------------------------------------
LANGUAGE ICON BUTTON
--------------------------------------------------- */

div[data-testid="stButton"] button:disabled {

    height: 44px !important;

    min-height: 44px !important;

    width: 34px !important;

    min-width: 34px !important;

    padding-left: 0 !important;

    padding-right: 0 !important;

    border: 1px solid #b8c2cc !important;

    border-right: none !important;

    background: white !important;

    opacity: 1 !important;

    color: #7f7f7f !important;

    filter: grayscale(100%) !important;

    font-size: 16px !important;

    cursor: default !important;

    margin-right: 0px !important;
}
/* ---------------------------------------------------
LANGUAGE ICON BUTTON
--------------------------------------------------- */

div[data-testid="stButton"] button:disabled {

    position: relative !important;

    z-index: 3 !important;
}
/* ---------------------------------------------------
LANGUAGE SELECTBOX
--------------------------------------------------- */

div[data-testid="stSelectbox"] {

    margin-top: -8px !important;

    margin-left: -8px !important;

    position: relative !important;

    z-index: 1 !important;
}
/* ---------------------------------------------------
FJERN VENSTRE BORDER
KUN LANGUAGE DROPDOWN
--------------------------------------------------- */

div[data-testid="stSelectbox"]:has(#language_select)
div[data-baseweb="select"] > div {

    border-left: none !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# CUSTOM HEADER BRANDING
# ---------------------------------------------------

header_html = """
<style>

.knauf-header {

    position: fixed;

    top: 0;

    left: 2.6rem;

    height: 4.05rem;

    display: flex;

    align-items: center;

    gap: 10px;

    padding-top: 2px;
    padding-top: 1px;

    z-index: 9999999;

    pointer-events: none;
}

.knauf-logo {

    height: 57px;
    height: 60px;

    width: auto;

    display: block;
}

.knauf-fireboard {

    font-size: 28px;

    font-weight: 600;

    font-style: italic;

    font-stretch: condensed;

    color: #979797;

    letter-spacing: 1,5px;

    line-height: 1;

    margin-top: -1px;

    font-family:
        "Arial Narrow",
        "Helvetica Neue",
        Arial,
        sans-serif;

    transform: scaleX(0.8) skewX(-4deg);

    transform-origin: left center;

    -webkit-font-smoothing: antialiased;

    text-rendering: geometricPrecision;
}
</style>

<div class="knauf-header">
<img class="knauf-logo" src="https://knauf.com/api/download-center/v1/assets/8355fec5-8cb9-42fe-b5d7-4e7258bf446a?download=true">
<div class="knauf-fireboard">Fireboard</div>
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)
# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

defaults = {

    "language": "DA",

    "category": None,
    "profile_type": None,
    "selected_profile": None,

    "montage": None,
    "sides": None,

    "calculations": [],

    "edit_index": None,
    "editing": False,

    "project_name": "",
    "company": "",
    "prepared_by": "",
    "description": "",

    "last_updated": datetime.now(),

    "custom_apv": None,
    "custom_profile_name": "",

    "surface_area": "",
    "steel_area": "",
    "apv_method": "Direkte",
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ---------------------------------------------------
# TRANSLATION HELPER
# ---------------------------------------------------

def t(key):

    return translations[
        st.session_state.language
    ][key]


# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

apv_df = pd.read_csv(
    "data/apv.csv",
    sep=";"
)

# ---------------------------------------------------
# FIREBOARD TABLES
# ---------------------------------------------------

def load_fireboard(path):

    df = pd.read_csv(
        path,
        sep=";"
    )

    df = df.dropna(how="all")

    df.rename(
        columns={
            df.columns[0]: "temperature"
        },
        inplace=True
    )

    df["temperature"] = (
        df["temperature"]
        .astype(str)
        .str.strip()
    )

    df["temperature"] = pd.to_numeric(
        df["temperature"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["temperature"]
    )

    df["temperature"] = (
        df["temperature"]
        .astype(int)
    )

    df.set_index(
        "temperature",
        inplace=True
    )

    df.columns = (
        pd.Series(df.columns)
        .astype(str)
        .str.strip()
    )

    df.columns = pd.to_numeric(
        df.columns,
        errors="coerce"
    )

    df = df.loc[
        :,
        df.columns.notna()
    ]

    df.columns = (
        df.columns.astype(int)
    )

    return df

fire_tables = {

    30: load_fireboard(
        "data/fireboard_30.csv"
    ),

    60: load_fireboard(
        "data/fireboard_60.csv"
    ),

    90: load_fireboard(
        "data/fireboard_90.csv"
    ),

    120: load_fireboard(
        "data/fireboard_120.csv"
    )
}

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(
    [6, 2, 2, 0.24, 1.12],
    gap="small",
    vertical_alignment="bottom"
)

with col1:

    st.title(
        t("title")
    )

# ---------------------------------------------------
# NY BEREGNING
# ---------------------------------------------------

with col2:

    st.write("")
    st.write("")

    if st.button(
        f"🔄 {t('new_calculation')}",
        use_container_width=True
    ):

        reset_keys = [

            "category",
            "profile_type",
            "montage",
            "sides",
            "selected_profile",
            "fire_time",
            "temperature"
        ]

        for key in reset_keys:

            st.session_state[key] = None

        # ---------------------------------------------------
        # VIGTIGT
        # ---------------------------------------------------

        st.session_state.editing = False

        st.session_state.edit_index = None

        st.session_state.current_step = 0

        st.rerun()

# ---------------------------------------------------
# NYT PROJEKT
# ---------------------------------------------------

with col3:

    st.write("")
    st.write("")

    if st.button(
        f"🗑️ {t('new_project')}",
        use_container_width=True
    ):

        st.session_state.clear()

        st.rerun()

# ---------------------------------------------------
# LANGUAGE ICON
# ---------------------------------------------------

with col4:

    st.button(
        "🌐",
        disabled=True,
        use_container_width=True
    )

# ---------------------------------------------------
# LANGUAGE SELECT
# ---------------------------------------------------

with col5:

    selected_language = st.selectbox(
        "",
        options=["Dansk", "English"],
        index=0 if st.session_state.language == "DA" else 1,
        label_visibility="collapsed",
        key="language_select"
    )

    new_lang = (
        "DA"
        if selected_language == "Dansk"
        else "EN"
    )

    if new_lang != st.session_state.language:

        st.session_state.language = new_lang

        st.rerun()
# ---------------------------------------------------
# PDF COORDINATES
# ---------------------------------------------------

# PROJECT INFO

PROJECT_X = 197
PROJECT_Y = 562
PROJECT_LINE_HEIGHT = 20

# DESCRIPTION

DESCRIPTION_Y = 482
DESCRIPTION_MAX_CHARS = 72

# CALCULATION

CALC_X = 197
CALC_Y = 418.5
CALC_LINE_HEIGHT = 19

# RESULT

RESULT_X = 287
RESULT_Y = 220.5

# PAGE NUMBER

PAGE_X = 283
PAGE_Y = 22

# PROFILE IMAGE

PROFILE_IMAGE_X = 430
PROFILE_IMAGE_Y = 730
PROFILE_IMAGE_WIDTH = 110
PROFILE_IMAGE_HEIGHT = 110

PROFILE_TEXT_X = 485
PROFILE_TEXT_Y = 720
PROFILE_TEXT_Y = 730
PROFILE_TEXT_FONT = 11

# FONT SIZES

PROJECT_FONT = 9
DESCRIPTION_FONT = 9
CALC_FONT = 9
RESULT_FONT = 14
PAGE_FONT = 10


# ---------------------------------------------------
# PROFILE IMAGE MAP
# ---------------------------------------------------

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
# GENERATE COMPLETE PDF
# ---------------------------------------------------

def generate_complete_pdf():

    output = PdfWriter()

    template_path = "PDF_template.pdf"

    for page_number, calc in enumerate(
        st.session_state.calculations,
        start=1
    ):

        packet = BytesIO()

        can = canvas.Canvas(
            packet,
            pagesize=A4
        )

        # ---------------------------------------------------
        # PROJECT INFO
        # ---------------------------------------------------

        can.setFont(
            "Helvetica",
            PROJECT_FONT
        )

        can.drawString(
            PROJECT_X,
            PROJECT_Y,
            str(st.session_state.project_name)
        )

        can.drawString(
            PROJECT_X,
            PROJECT_Y - PROJECT_LINE_HEIGHT,
            str(st.session_state.prepared_by)
        )

        can.drawString(
            PROJECT_X,
            PROJECT_Y - (PROJECT_LINE_HEIGHT * 2),
            str(st.session_state.company)
        )

        can.drawString(
            PROJECT_X,
            PROJECT_Y - (PROJECT_LINE_HEIGHT * 3),
            datetime.now().strftime("%d-%m-%Y")
        )

        can.drawString(
            PROJECT_X,
            PROJECT_Y - (PROJECT_LINE_HEIGHT * 4),
            str(st.session_state.description)
        )

        # ---------------------------------------------------
        # CALCULATION
        # ---------------------------------------------------

        can.setFont(
            "Helvetica",
            CALC_FONT
        )

        can.drawString(
            CALC_X,
            CALC_Y,
            str(calc["category"])
        )

        can.drawString(
            CALC_X,
            CALC_Y - CALC_LINE_HEIGHT,
            str(calc["profile"])
        )

        can.drawString(
            CALC_X,
            CALC_Y - (CALC_LINE_HEIGHT * 2),
            f"{calc['sides']} sider"
        )

        can.drawString(
            CALC_X,
            CALC_Y - (CALC_LINE_HEIGHT * 3),
            str(calc["montage"])
        )

        can.drawString(
            CALC_X,
            CALC_Y - (CALC_LINE_HEIGHT * 4),
            f"{calc['fire_time']} minutter"
        )

        can.drawString(
            CALC_X,
            CALC_Y - (CALC_LINE_HEIGHT * 5),
            f"{calc['temperature']} °C"
        )

        can.drawString(
            CALC_X,
            CALC_Y - (CALC_LINE_HEIGHT * 6),
            f"{calc['apv']} m²/m³"
        )

        # ---------------------------------------------------
        # PROFILE IMAGE
        # ---------------------------------------------------

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

            can.setFont(
                "Helvetica-Bold",
                PROFILE_TEXT_FONT
            )

            can.drawCentredString(
                PROFILE_TEXT_X,
                PROFILE_TEXT_Y,
                str(calc["profile"])
            )

        # ---------------------------------------------------
        # RESULT
        # ---------------------------------------------------

        can.setFillColorRGB(
            1,
            1,
            1
        )

        can.setFont(
            "Helvetica-Bold",
            RESULT_FONT
        )

        can.drawCentredString(
            RESULT_X,
            RESULT_Y,
            (
                f"Profil skal inddækkes med "
                f"{int(calc['thickness'])} mm "
                f"Knauf Fireboard"
            )
        )

        # ---------------------------------------------------
        # PAGE NUMBER
        # ---------------------------------------------------

        can.setFillColorRGB(
            0,
            0.62,
            0.89
        )

        can.setFont(
            "Helvetica",
            PAGE_FONT
        )

        can.drawString(
            PAGE_X,
            PAGE_Y,
            str(page_number)
        )

        can.save()

        # ---------------------------------------------------
        # MERGE TEMPLATE
        # ---------------------------------------------------

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

    # ---------------------------------------------------
    # OUTPUT
    # ---------------------------------------------------

    output_stream = BytesIO()

    output.write(output_stream)

    output_stream.seek(0)

    return output_stream


# ---------------------------------------------------
# GENERATE SINGLE PDF
# ---------------------------------------------------

def generate_single_pdf(calc):

    output = PdfWriter()

    template_path = "PDF_template.pdf"

    packet = BytesIO()

    can = canvas.Canvas(
        packet,
        pagesize=A4
    )

    # ---------------------------------------------------
    # PROJECT INFO
    # ---------------------------------------------------

    can.setFont(
        "Helvetica",
        PROJECT_FONT
    )

    can.drawString(
        PROJECT_X,
        PROJECT_Y,
        str(st.session_state.project_name)
    )

    can.drawString(
        PROJECT_X,
        PROJECT_Y - PROJECT_LINE_HEIGHT,
        str(st.session_state.prepared_by)
    )

    can.drawString(
        PROJECT_X,
        PROJECT_Y - (PROJECT_LINE_HEIGHT * 2),
        str(st.session_state.company)
    )

    can.drawString(
        PROJECT_X,
        PROJECT_Y - (PROJECT_LINE_HEIGHT * 3),
        datetime.now().strftime("%d-%m-%Y")
    )

    can.drawString(
        PROJECT_X,
        PROJECT_Y - (PROJECT_LINE_HEIGHT * 4),
        str(st.session_state.description)
    )

    # ---------------------------------------------------
    # CALCULATION
    # ---------------------------------------------------

    can.setFont(
        "Helvetica",
        CALC_FONT
    )

    can.drawString(
        CALC_X,
        CALC_Y,
        str(calc["category"])
    )

    can.drawString(
        CALC_X,
        CALC_Y - CALC_LINE_HEIGHT,
        str(calc["profile"])
    )

    can.drawString(
        CALC_X,
        CALC_Y - (CALC_LINE_HEIGHT * 2),
        f"{calc['sides']} sider"
    )

    can.drawString(
        CALC_X,
        CALC_Y - (CALC_LINE_HEIGHT * 3),
        str(calc["montage"])
    )

    can.drawString(
        CALC_X,
        CALC_Y - (CALC_LINE_HEIGHT * 4),
        f"{calc['fire_time']} minutter"
    )

    can.drawString(
        CALC_X,
        CALC_Y - (CALC_LINE_HEIGHT * 5),
        f"{calc['temperature']} °C"
    )

    can.drawString(
        CALC_X,
        CALC_Y - (CALC_LINE_HEIGHT * 6),
        f"{calc['apv']} m²/m³"
    )

    # ---------------------------------------------------
    # PROFILE IMAGE
    # ---------------------------------------------------

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

        can.setFont(
            "Helvetica-Bold",
            PROFILE_TEXT_FONT
        )

        can.drawCentredString(
            PROFILE_TEXT_X,
            PROFILE_TEXT_Y,
            str(calc["profile"])
        )

    # ---------------------------------------------------
    # RESULT
    # ---------------------------------------------------

    can.setFillColorRGB(
        1,
        1,
        1
    )

    can.setFont(
        "Helvetica-Bold",
        RESULT_FONT
    )

    can.drawCentredString(
        RESULT_X,
        RESULT_Y,
        (
            f"Profil skal inddækkes med "
            f"{int(calc['thickness'])} mm "
            f"Knauf Fireboard"
        )
    )

    # ---------------------------------------------------
    # PAGE NUMBER
    # ---------------------------------------------------

    can.setFillColorRGB(
        0,
        0.62,
        0.89
    )

    can.setFont(
        "Helvetica",
        PAGE_FONT
    )

    can.drawString(
        PAGE_X,
        PAGE_Y,
        "1"
    )

    can.save()

    # ---------------------------------------------------
    # MERGE TEMPLATE
    # ---------------------------------------------------

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

    # ---------------------------------------------------
    # OUTPUT
    # ---------------------------------------------------

    output_stream = BytesIO()

    output.write(output_stream)

    output_stream.seek(0)

    return output_stream

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.title("📚 Beregninger")

    # ---------------------------------------------------
    # CUSTOM STYLE
    # ---------------------------------------------------

    st.markdown("""
    <style>

    /* ---------------------------------------------------
    AKTIV SIDEBAR BEREGNING
    --------------------------------------------------- */

    div[data-testid="stSidebar"] button[kind="primary"] {

        background: #003b7a !important;

        border: 1px solid #003b7a !important;

        color: white !important;

        font-weight: 700 !important;

        box-shadow: none !important;
    }

    div[data-testid="stSidebar"] button[kind="primary"] p,
    div[data-testid="stSidebar"] button[kind="primary"] span,
    div[data-testid="stSidebar"] button[kind="primary"] div {

        color: white !important;

        -webkit-text-fill-color: white !important;

        font-weight: 700 !important;

        opacity: 1 !important;
    }

    /* HOVER */

    div[data-testid="stSidebar"] button[kind="primary"]:hover {

        background: #002e5f !important;

        border: 1px solid #002e5f !important;

        color: white !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------
    # NY BEREGNING
    # ---------------------------------------------------

    if st.button(
        "➕ Ny beregning",
        use_container_width=True
    ):

        reset_keys = [

            "category",
            "profile_type",
            "montage",
            "sides",
            "selected_profile",
            "fire_time",
            "temperature"
        ]

        for key in reset_keys:

            st.session_state[key] = None

        st.session_state.editing = False

        st.session_state.edit_index = None

        st.session_state.current_step = 0

        st.rerun()

    st.divider()

    # ---------------------------------------------------
    # BEREGNINGER
    # ---------------------------------------------------

    if st.session_state.calculations:

        for idx, calc in enumerate(
            st.session_state.calculations
        ):

            is_active = (
                st.session_state.edit_index == idx
            )

            col1, col2 = st.columns([5, 1])

            label = (
                f"{calc['profile']} • "
                f"R{calc['fire_time']} • "
                f"{calc['temperature']}°C • "
                f"{int(calc['thickness'])} mm"
            )

            # ---------------------------------------------------
            # LOAD CALCULATION
            # ---------------------------------------------------

            with col1:

                if st.button(
                    label,
                    key=f"sidebar_calc_{idx}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True
                ):

                    st.session_state.category = (
                        calc["category"]
                    )

                    st.session_state.montage = (
                        calc["montage"]
                    )

                    st.session_state.sides = (
                        calc["sides"]
                    )

                    st.session_state.fire_time = (
                        calc["fire_time"]
                    )

                    st.session_state.temperature = (
                        calc["temperature"]
                    )

                    st.session_state.selected_profile = (
                        calc["profile"]
                    )

                    st.session_state.apv_method = calc.get(
                        "apv_method",
                        "Direkte"
                    )

                    st.session_state.custom_apv = calc.get(
                        "custom_apv"
                    )

                    st.session_state.surface_area = calc.get(
                        "surface_area",
                        ""
                    )

                    st.session_state.steel_area = calc.get(
                        "steel_area",
                        ""
                    )

                    st.session_state.edit_index = idx

                    st.session_state.editing = True

                    st.session_state.current_step = 0

                    st.rerun()

            # ---------------------------------------------------
            # DELETE
            # ---------------------------------------------------

            with col2:

                if st.button(
                    "🗑️",
                    key=f"delete_sidebar_{idx}"
                ):

                    st.session_state.calculations.pop(
                        idx
                    )

                    if (
                        st.session_state.edit_index
                        == idx
                    ):

                        st.session_state.edit_index = None

                        st.session_state.editing = False

                    st.rerun()

    # ---------------------------------------------------
    # DOWNLOAD ALL CALCULATIONS
    # ---------------------------------------------------

    if st.session_state.calculations:

        st.divider()

        complete_pdf = generate_complete_pdf()

        st.download_button(
            label="📚 Download alle beregninger",
            data=complete_pdf,
            file_name="Knauf_Fireboard_Rapport.pdf",
            mime="application/pdf",
            use_container_width=True
        )
# ---------------------------------------------------
# CARD FUNCTIONS
# ---------------------------------------------------

def get_base64_image(image_path):

    with open(image_path, "rb") as img_file:

        return base64.b64encode(
            img_file.read()
        ).decode()


def card(
    label,
    image_path,
    state_key
):

    selected = (
        st.session_state[state_key]
        == label
    )

    background = (
        "#eef7fd"
        if selected
        else "white"
    )

    border = (
        "2px solid #003b7a"
        if selected
        else "1px solid #d9dde3"
    )

    image_base64 = get_base64_image(
        image_path
    )

    html = f"""
    <html>
    <body style="
        margin:0;
        padding:0;
    ">
    <div style="
        border:{border};
        background-color:{background};
        border-radius:0px;
        padding:10px;
        width:calc(100% - 2px);
        text-align:center;
        height:170px;
        width:100%;
        box-sizing:border-box;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        transition: all 0.15s ease;
    ">

        <img src="data:image/png;base64,{image_base64}"
        style="
            width:120px;
            height:120px;
            object-fit:contain;
            margin-bottom:8px;
        "/>

        <div style="
            font-size:17px;
            font-weight:700;
            color:#2d343c;
            text-align:center;
            line-height:1.25;
        ">
            {label}
        </div>

    </div>
    </body>
    </html>
    """

    st.components.v1.html(
        html,
        height=170
    )

    if st.button(
        "Vælg",
        key=f"{state_key}_{label}",
        use_container_width=True
    ):

        st.session_state[state_key] = label

        if (
            label == "Cirkulære rør middelsvære"
            or
            label == "Cirkulære rør svære"
        ):

            st.session_state["sides"] = "4"

        st.rerun()


def disabled_card(
    label,
    image_path
):

    image_base64 = get_base64_image(
        image_path
    )

    html = f"""
    <html>
    <body style="
        margin:0;
        padding:0;
    ">
    <div style="
        border:1px solid #d9dde3;
        background:white;
        opacity:0.45;
        border-radius:0px;
        padding:10px;
        width:calc(100% - 2px);
        text-align:center;
        height:170px;
        width:100%;
        box-sizing:border-box;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
    ">

        <img src="data:image/png;base64,{image_base64}"
        style="
            width:120px;
            height:120px;
            object-fit:contain;
            margin-bottom:12px;
        "/>

        <div style="
            font-size:17px;
            font-weight:700;
            color:#999999;
            text-align:center;
            line-height:1.25;
        ">
            {label}
        </div>

    </div>
    </body>
    </html>
    """

    st.components.v1.html(
        html,
        height=170
    )

# ---------------------------------------------------
# STEP NAVIGATION
# ---------------------------------------------------

steps = [
    "Profil",
    "Inddækning",
    "Brand",
    "Resultat"
]

if "current_step" not in st.session_state:

    st.session_state.current_step = 0

current_step = st.session_state.current_step

# ---------------------------------------------------
# DEFAULT VALUES
# ---------------------------------------------------

category = st.session_state.get(
    "category"
)

montage = st.session_state.get(
    "montage"
)

sides = st.session_state.get(
    "sides"
)

fire_time = st.session_state.get(
    "fire_time"
)

temperature = st.session_state.get(
    "temperature",
    450
)

selected_profile = st.session_state.get(
    "selected_profile"
)

apv = None
thickness = None

# ---------------------------------------------------
# STEP HEADER
# ---------------------------------------------------

cols = st.columns(len(steps))

for idx, step in enumerate(steps):

    with cols[idx]:

        active = idx == current_step

        if active:

            st.markdown(f"""
            <div style="
                background-color:#003b7a;
                color:white;
                padding:8px;
                border-radius:0px;
                text-align:center;
                font-weight:700;
                border:1px solid #003b7a;
            ">
                {idx+1}. {step}
            </div>
            """, unsafe_allow_html=True)

        else:

            if st.button(
                f"{idx+1}. {step}",
                use_container_width=True,
                key=f"step_{idx}"
            ):

                st.session_state.current_step = idx

                st.rerun()

# ---------------------------------------------------
# TAB 1 - PROFIL
# ---------------------------------------------------

if current_step == 0:

    st.subheader(
        "Vælg profilkategori"
    )

    categories = [

        ("H-profiler", "images/h_profiles.png"),
        ("I-profiler", "images/i_profiles.png"),
        ("U-profiler", "images/u_profiles.png"),

        ("Kvadratiske rør varmvalsede", "images/shs_hot.png"),
        ("Kvadratiske rør koldvalsede", "images/shs_cold.png"),

        ("Rektangulære rør varmvalsede", "images/rhs_hot.png"),
        ("Rektangulære rør koldvalsede", "images/rhs_cold.png"),

        ("Cirkulære rør middelsvære", "images/chs_medium.png"),
        ("Cirkulære rør svære", "images/chs_heavy.png"),

        ("Andre profiler", "images/other_profiles.png"),
    ]

    for i in range(0, len(categories), 5):

        cols = st.columns(5)

        for col, (label, image) in zip(
            cols,
            categories[i:i+5]
        ):

            with col:

                card(
                    label,
                    image,
                    "category"
                )

    category = st.session_state.category

    if not category:

        st.stop()

    st.divider()

    # ---------------------------------------------------
    # STANDARD PROFILER
    # ---------------------------------------------------

    if category != "Andre profiler":

        # ---------------------------------------------------
        # PROFILTYPER
        # ---------------------------------------------------

        profile_options = []

        # ---------------------------------------------------
        # RESET PROFILE TYPE FOR OTHER CATEGORIES
        # ---------------------------------------------------

        if category not in [
            "H-profiler",
            "I-profiler",
            "U-profiler"
        ]:

            st.session_state.profile_type = None

        # ---------------------------------------------------
        # DEFAULT PROFILE TYPE
        # ---------------------------------------------------

        if category == "H-profiler":

            valid_types = ["HEB", "HEA", "HEM"]

            if (
                st.session_state.get("profile_type")
                not in valid_types
            ):

                st.session_state.profile_type = "HEB"

        elif category == "I-profiler":

            valid_types = ["IPE", "INP"]

            if (
                st.session_state.get("profile_type")
                not in valid_types
            ):

                st.session_state.profile_type = "IPE"

        elif category == "U-profiler":

            st.session_state.profile_type = "UNP"

        else:

            st.session_state.profile_type = None
        # ---------------------------------------------------
        # H-PROFILER
        # ---------------------------------------------------

        if category == "H-profiler":

            profile_options = [
                "HEB",
                "HEA",
                "HEM"
            ]

        # ---------------------------------------------------
        # I-PROFILER
        # ---------------------------------------------------

        elif category == "I-profiler":

            profile_options = [
                "IPE",
                "INP"
            ]

        # ---------------------------------------------------
        # U-PROFILER
        # ---------------------------------------------------

        elif category == "U-profiler":

            profile_options = [
                "UNP"
            ]

        # ---------------------------------------------------
        # TYPEVALG
        # ---------------------------------------------------

        if profile_options:

            st.markdown("""
            <div style="
                font-size:15px;
                font-weight:500;
                color:#3e4650;
                margin-bottom:0.3rem;
            ">
                Vælg profiltype
            </div>
            """, unsafe_allow_html=True)

            cols = st.columns(
                len(profile_options)
            )

            for idx, option in enumerate(
                profile_options
            ):

                with cols[idx]:

                    selected = (
                        st.session_state.get(
                            "profile_type"
                        )
                        == option
                    )

                    if st.button(
                        option,
                        key=f"profile_type_{option}",
                        use_container_width=True,
                        type=(
                            "primary"
                            if selected
                            else "secondary"
                        )
                    ):

                        st.session_state.profile_type = (
                            option
                        )

                        st.session_state.selected_profile = None

                        st.rerun()

            st.divider()

        # ---------------------------------------------------
        # FILTER DATA
        # ---------------------------------------------------

        filtered_df = apv_df[
            apv_df["profile_category"]
            == category
        ]

        selected_type = (
            st.session_state.get(
                "profile_type"
            )
        )

        if selected_type:

            filtered_df = filtered_df[
                filtered_df["profile"]
                .astype(str)
                .str.startswith(selected_type)
            ]

        profiles = (
            filtered_df["profile"]
            .unique()
        )

        profiles = sorted(profiles)

        if len(profiles) == 0:

            st.error("Ingen profiler fundet")

            st.stop()

        # ---------------------------------------------------
        # PROFILVALG
        # ---------------------------------------------------

        selected_profile = st.selectbox(
            "Vælg profilstørrelse",
            profiles,
            index=(
                list(profiles).index(
                    st.session_state.selected_profile
                )
                if (
                    st.session_state.selected_profile
                    in profiles
                )
                else 0
            )
        )

        st.session_state.selected_profile = (
            selected_profile
        )

    # ---------------------------------------------------
    # ANDRE PROFILER
    # ---------------------------------------------------

    else:

        custom_profile_name = st.text_input(
            "Profilnavn (vaglfri)",
            value=st.session_state.custom_profile_name
        )

        st.session_state.custom_profile_name = (
            custom_profile_name
        )

        st.divider()

        # ---------------------------------------------------
        # METODEVALG
        # ---------------------------------------------------

        st.markdown("""
        <div style="
            font-size:15px;
            font-weight:500;
            color:#3e4650;
            margin-bottom:0.3rem;
        ">
            Vælg metode
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:

            direkte_selected = (
                st.session_state.apv_method
                == "Direkte"
            )

            if st.button(
                "Indtast Ap/V",
                use_container_width=True,
                type=(
                    "primary"
                    if direkte_selected
                    else "secondary"
                )
            ):

                st.session_state.apv_method = (
                    "Direkte"
                )

                st.rerun()

        with col2:

            beregn_selected = (
                st.session_state.apv_method
                == "Beregn"
            )

            if st.button(
                "Beregn Ap/V",
                use_container_width=True,
                type=(
                    "primary"
                    if beregn_selected
                    else "secondary"
                )
            ):

                st.session_state.apv_method = (
                    "Beregn"
                )

                st.rerun()

        st.divider()

        # ---------------------------------------------------
        # DIREKTE AP/V
        # ---------------------------------------------------

        if (
            st.session_state.get(
                "apv_method",
                "Direkte"
            )
            == "Direkte"
        ):

            custom_apv = st.text_input(
                "Indtast Ap/V forhold (m²/m³)",
                value=(
                    str(st.session_state.custom_apv)
                    if st.session_state.custom_apv
                    else ""
                )
            )

            try:

                custom_apv = int(
                    float(
                        custom_apv.replace(",", ".")
                    )
                )

                st.session_state.custom_apv = (
                    custom_apv
                )

            except:

                st.error(
                    "Indtast gyldig Ap/V værdi"
                )

        # ---------------------------------------------------
        # BEREGN AP/V
        # ---------------------------------------------------

        else:

            ap_input = st.text_input(
                "Indtast indvendig omkreds (mm)",
                value=st.session_state.surface_area
            )

            st.markdown(
                "Indtast stålets Tværsnitsareal (mm²)"
            )

            col1, col2 = st.columns([5, 1], vertical_alignment="bottom")

            with col1:

                v_input = st.text_input(
                    label="",
                    value=st.session_state.steel_area,
                    label_visibility="collapsed"
                )

            with col2:

                calculate_clicked = st.button(
                    "Beregn",
                    use_container_width=True
                )

            if calculate_clicked:

                try:

                    ap = float(
                        ap_input.replace(",", ".")
                    )

                    v = float(
                        v_input.replace(",", ".")
                    )

                    calculated_apv = round(
                        (ap * 1000) / v
                    )

                    st.session_state.surface_area = (
                        ap_input
                    )

                    st.session_state.steel_area = (
                        v_input
                    )

                    st.session_state.custom_apv = (
                        calculated_apv
                    )

                except:

                    st.error(
                        "Indtast gyldige tal"
                    )

            if st.session_state.custom_apv:

                st.info(
                    f"Beregnet Ap/V: "
                    f"{st.session_state.custom_apv} m²/m³"
                )

    # ---------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------

    st.divider()

    col1, col2 = st.columns([1,1])

    with col2:

        if st.button(
            "Næste →",
            use_container_width=True
        ):

            st.session_state.current_step = 1

            st.rerun()
# ---------------------------------------------------
# TAB 2 - INDDÆKNING
# ---------------------------------------------------

if current_step == 1:

    st.subheader(
        "Vælg inddækningstype"
    )

    col1, col2 = st.columns(2)

    with col1:

        card(
            "Klammeløsning",
            "images/klamme.png",
            "montage"
        )

    with col2:

        card(
            "Bjælkeprofil eller PDP profil",
            "images/bjaelke.png",
            "montage"
        )

    montage = st.session_state.montage

    if not montage:

        st.stop()

    st.divider()

    st.subheader(
        "Vælg antal sider med inddækning"
    )

    is_circular = (

        category
        == "Cirkulære rør middelsvære"

        or

        category
        == "Cirkulære rør svære"
    )

    col1, col2, col3, col4 = st.columns(4)

    if is_circular:

        with col1:

            disabled_card(
                "1 side ikke muligt",
                "images/side1.png"
            )

        with col2:

            disabled_card(
                "2 sider ikke muligt",
                "images/side2.png"
            )

        with col3:

            disabled_card(
                "3 sider ikke muligt",
                "images/side3.png"
            )

        with col4:

            card(
                "4",
                "images/side4.png",
                "sides"
            )

    else:

        with col1:

            card(
                "1",
                "images/side1.png",
                "sides"
            )

        with col2:

            card(
                "2",
                "images/side2.png",
                "sides"
            )

        with col3:

            card(
                "3",
                "images/side3.png",
                "sides"
            )

        with col4:

            card(
                "4",
                "images/side4.png",
                "sides"
            )

    sides = st.session_state.sides

    if not sides:

        st.stop()

    sides = int(sides)

    # ---------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------

    st.divider()

    col1, col2 = st.columns([1,1])

    with col1:

        if st.button(
            "← Forrige",
            use_container_width=True
        ):

            st.session_state.current_step = 0

            st.rerun()

    with col2:

        if st.button(
            "Næste →",
            use_container_width=True
        ):

            st.session_state.current_step = 2

            st.rerun()
# ---------------------------------------------------
# TAB 3 - BRAND
# ---------------------------------------------------

if current_step == 2:

    st.subheader(
        "Brandkrav"
    )

    st.divider()

    fire_options = [30, 60, 90, 120]

    saved_fire_time = st.session_state.get(
    "fire_time"
    )

    if saved_fire_time not in fire_options:
        saved_fire_time = 30

    fire_time = st.selectbox(
        "Vælg brandbeskyttelsestid",
        fire_options,
        index=fire_options.index(saved_fire_time)
    )

    st.divider()

    # ---------------------------------------------------
    # STÅLTEMPERATUR
    # ---------------------------------------------------

    temperature = st.text_input(
        "Indtast dimensionerende ståltemperatur (°C)",
        value=str(
            st.session_state.get("temperature") or 450
        )
    )

    # ---------------------------------------------------
    # VALIDERING
    # ---------------------------------------------------

    try:

        temperature = int(temperature)

    except:

        st.error(
            "Temperatur skal være et helt tal"
        )

        st.stop()

    if temperature < 350 or temperature > 750:

        st.error(
            "Temperatur skal være mellem 350 og 750 °C"
        )

        st.stop()

    st.session_state.fire_time = fire_time
    st.session_state.temperature = temperature

    # ---------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------

    st.divider()

    col1, col2 = st.columns([1,1])

    with col1:

        if st.button(
            "← Forrige",
            use_container_width=True
        ):

            st.session_state.current_step = 1

            st.rerun()

    with col2:

        if st.button(
            "Næste →",
            use_container_width=True
        ):

            st.session_state.current_step = 3

            st.rerun()
# ---------------------------------------------------
# FIND AP/V + TYKKELSE
# ---------------------------------------------------

if (
    (
        selected_profile
        or category == "Andre profiler"
    )
    and montage
    and sides
    and fire_time
    and temperature
):

    # ---------------------------------------------------
    # STANDARD PROFILER
    # ---------------------------------------------------

    if category != "Andre profiler":

        row = apv_df[
            (
                apv_df["profile"]
                == selected_profile
            )
            &
            (
                apv_df["montage"]
                == montage
            )
            &
            (
                apv_df["sides"]
                == int(sides)
            )
        ]

        if row.empty:

            st.error(
                "Denne kombination er ikke mulig"
            )

            st.stop()

        apv = int(
            row.iloc[0]["apv"]
        )

    # ---------------------------------------------------
    # ANDRE PROFILER
    # ---------------------------------------------------

    else:

        apv = int(
            st.session_state.custom_apv
        )

        selected_profile = (

            st.session_state.custom_profile_name

            if st.session_state.custom_profile_name
            else "Specialprofil"
        )

    # ---------------------------------------------------
    # FIND TYKKELSE
    # ---------------------------------------------------

    table = fire_tables[fire_time]

    if apv not in table.columns:

        st.error(
            "Profilforholdet (Ap/V) overstiger 380 m²/m³, vælg et andet eller større profil"
        )

        st.stop()

    if int(temperature) not in table.index:

        st.error(
            "Temperaturen findes ikke"
        )

        st.stop()

    thickness = table.loc[
        int(temperature),
        apv
    ]

# --------------------------------------------------
# TAB 4 - RESULTAT
# ---------------------------------------------------

if current_step == 3:

    st.subheader(
        "Resultat"
    )

    st.divider()

    # ---------------------------------------------------
    # RESULTAT
    # ---------------------------------------------------

    if apv is not None and thickness is not None:

        st.markdown(f"""
        <div style="
            border:1px solid #003b7a;
            background:#003b7a;
            border-radius:0px;
            padding:18px;
            margin-bottom:12px;
            color:white;
            font-weight:700;
        ">
            <b>Beregnet profilforhold Ap/V:</b>
            {apv} m²/m³
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            border:1px solid #003b7a;
            background:#003b7a;
            border-radius:0px;
            padding:18px;
            margin-bottom:12px;
            color:white;
            font-weight:700;
        ">
            <b>Profil skal inddækkes med:</b>
            {int(thickness)} mm Knauf Fireboard
        </div>
        """, unsafe_allow_html=True)

    else:

        st.info(
            "Udfyld alle trin for at se resultat"
        )

        st.stop()

    # ---------------------------------------------------
    # BEREGNINGSDATA
    # ---------------------------------------------------

    calculation_data = {

        "category": category,
        "profile": selected_profile,
        "montage": montage,
        "sides": sides,

        "fire_time": fire_time,
        "temperature": temperature,

        "apv": apv,
        "thickness": thickness,

         # ANDRE PROFILER
        "apv_method": st.session_state.get("apv_method"),
        "custom_apv": st.session_state.get("custom_apv"),
        "surface_area": st.session_state.get("surface_area"),
        "steel_area": st.session_state.get("steel_area"),
    }

    # ---------------------------------------------------
    # DOWNLOAD DENNE BEREGNING
    # ---------------------------------------------------

    single_calc_pdf = generate_single_pdf(
        calculation_data
    )

    st.download_button(
        label="📄 Download denne beregning",
        data=single_calc_pdf,
        file_name=(
            f"{selected_profile}_"
            f"R{fire_time}.pdf"
        ),
        mime="application/pdf",
        use_container_width=True
    )

    # ---------------------------------------------------
    # PROJEKTOPLYSNINGER
    # ---------------------------------------------------

    st.divider()

    st.header(
        "Projektoplysninger"
    )

    col1, col2 = st.columns(2)

    with col1:

        project_name = st.text_input(
            "Projekt",
            value=st.session_state.project_name
        )

        prepared_by = st.text_input(
            "Udarbejdet af",
            value=st.session_state.prepared_by
        )

    with col2:

        company = st.text_input(
            "Firma",
            value=st.session_state.company
        )

        report_date = st.text_input(
            "Dato",
            value=datetime.now().strftime("%d-%m-%Y")
        )

    description = st.text_area(
        "Beskrivelse",
        value=st.session_state.description,
        height=120
    )

    st.session_state.project_name = project_name
    st.session_state.company = company
    st.session_state.prepared_by = prepared_by
    st.session_state.description = description

    # ---------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------

    st.divider()

    col1, col2 = st.columns([1,1])

    with col1:

        if st.button(
            "← Forrige",
            use_container_width=True
        ):

            st.session_state.current_step = 2

            st.rerun()

    with col2:

        button_text = (
            "🔄 Opdater beregning"
            if st.session_state.edit_index is not None
            else "➕ Tilføj beregning"
        )

        if st.button(
            button_text,
            use_container_width=True
        ):

            if st.session_state.edit_index is not None:

                st.session_state.calculations[
                    st.session_state.edit_index
                ] = calculation_data

                st.session_state.edit_index = None

                st.session_state.editing = False

            else:

                st.session_state.calculations.append(
                    calculation_data
                )

            st.session_state.last_updated = datetime.now()

            st.success(
                "Beregning gemt"
            )

            st.rerun()
