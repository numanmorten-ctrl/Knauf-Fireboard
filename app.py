import base64
from io import BytesIO
from datetime import datetime
from pathlib import Path
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

import streamlit as st
import pandas as pd
import requests

from translations import translations
from utils.data_loader import clean_text, clean_numeric, load_and_clean_csv
from utils.render_helpers import render_materials_table
from utils.export_helpers import create_materials_excel
from utils.ui_helpers import (
    card,
    disabled_card
)
from utils.validation_helpers import (
    validate_temperature,
    validate_fireboard_lookup,
    reset_calculation_state
)
from utils.pdf_generator import (
    PROFILE_IMAGE_MAP,
    generate_single_pdf,
    generate_complete_pdf,
)

from utils.constants import (
    PROJECT_X,
    PROJECT_Y,
    PROJECT_LINE_HEIGHT,

    DESCRIPTION_Y,
    DESCRIPTION_MAX_CHARS,

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
    DESCRIPTION_FONT,
    CALC_FONT,
    RESULT_FONT,
    PAGE_FONT
)

from utils.material_helpers import (
    resolve_screw_clamp_by_layer,
    lookup_material_by_code,
    lookup_material_info,
    deduplicate_materials,
    format_number,
    format_db_nr,
    format_art_nr,
    build_material_row,
    build_materials_dataframe,
    get_material_label,
    resolve_beam_text,
    resolve_angle_material,
    resolve_screw_material,
    resolve_staple_material,
    resolve_beam_material,
    generate_fastener_materials,
    generate_fireboard_materials,
    generate_layer_fastener_materials,
    generate_materials,
    build_variant_label
)

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

    background-color: #f7f8f9 !important;
}

.block-container {

    max-width: 1600px;

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
INPUT FIELDS
--------------------------------------------------- */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {

    background: white !important;

    border: 1px solid #c5cbd3 !important;

    border-radius: 0px !important;

    color: #364650 !important;

    -webkit-text-fill-color: #364650 !important;

    caret-color: #00549f !important;

    padding: 0.5rem !important;

    box-shadow: none !important;

    outline: none !important;

    appearance: none !important;

    -webkit-appearance: none !important;

    -moz-appearance: none !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {

    border-color: #00549f !important;

    box-shadow: none !important;

    outline: none !important;
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

    background-color: #ffffff !important;

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
.stSelectbox,
.stButton,
.stDownloadButton {

    box-sizing: border-box !important;
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
.stTextArea > div {

    border: none !important;

    background: transparent !important;

    box-shadow: none !important;
}

.stTextInput > div > div,
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

    width: 38px !important;

    min-width: 38px !important;

    padding-left: 20px !important;

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

    margin-left: -0px !important;

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
/* DATAFRAME BG */

[data-testid="stDataFrame"] {

    background: white !important;
}

/* HIDE +/- BUTTONS */

[data-testid="stNumberInput"] button {

    display: none !important;
}
/* ---------------------------------------------------
TABLE
--------------------------------------------------- */

table {

    width: 100% !important;

    border-collapse: collapse !important;

    border-spacing: 0 !important;

    background: white !important;

    border: none !important;

    box-shadow: none !important;

    outline: none !important;
}

/* ---------------------------------------------------
HEADER
--------------------------------------------------- */

table thead th {

    background: #f2f2f2 !important;

    color: #364650 !important;

    font-weight: 700 !important;

    font-size: 15px !important;

    text-transform: uppercase !important;

    text-align: left !important;

    padding: 6px 24px !important;

    border: none !important;

    border-bottom: 1px solid #dfe3e8 !important;

    vertical-align: middle !important;

    letter-spacing: 0.02em !important;
}

/* ---------------------------------------------------
BODY
--------------------------------------------------- */

table tbody td {

    background: white !important;

    color: #364650 !important;

    font-size: 14px !important;

    padding: 18px 24px !important;

    border: none !important;

    border-bottom: 1px solid #e3e6ea !important;

    vertical-align: middle !important;
}

/* ---------------------------------------------------
REMOVE SIDE BORDERS
--------------------------------------------------- */

table,
table tr,
table td,
table th {

    border-left: none !important;

    border-right: none !important;

    border-radius: 0 !important;

    box-shadow: none !important;

    outline: none !important;
}

/* ---------------------------------------------------
HOVER
--------------------------------------------------- */

table tbody tr:hover td {

    background: #fafafa !important;
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

    "combined_materials": {},

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
# PROFILE CATEGORY MAPPING
# ---------------------------------------------------

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


# ---------------------------------------------------
# DISPLAY VALUE TRANSLATION MAPPING
# Map internal (stored) values to translation keys for labels shown in PDFs
# ---------------------------------------------------
DISPLAY_VALUE_TO_TRANSLATION_KEY = {
    "Klammeløsning": "clamping_solution",
    "Bjælkeprofil eller PHL profil": "beam_or_phl_profile",
}


def get_display_text(value):
    """Return a translated display string for an internal value when available.

    Preserves the original internal value for logic/filtering; only used for
    rendering text in the PDF.
    """
    if value is None:
        return ""

    key = DISPLAY_VALUE_TO_TRANSLATION_KEY.get(value)

    if key:
        return translations[st.session_state.language].get(key, value)

    return value


def get_translated_category(category):
    """Get the translated category name based on current language."""
    key = CATEGORY_TO_TRANSLATION_KEY.get(category)
    if key:
        return t(key)
    return category


def format_profile_display(category, profile):
    """Format profile display with category and size on separate lines."""
    translated_category = get_translated_category(category)
    return f"{translated_category}\n{profile}"


def format_sides_display(value):
    """Return a cleaned sides label for PDF output without duplicated text."""
    if value is None:
        return ""

    text = str(value).strip()
    if not text:
        return ""

    translated_sides = t("sides")
    if translated_sides and translated_sides.lower() in text.lower():
        return text

    return f"{text} {translated_sides}"


def display_value(value):
    if value is None:
        return ""

    if isinstance(value, float) and pd.isna(value):
        return ""

    text = str(value).strip()
    if not text:
        return ""

    if text.lower() in {"none", "nan"}:
        return ""

    return text


# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

DATA_DIR = Path("data")

apv_df = load_and_clean_csv(
    "data/apv.csv",
    sep=";"
)

layer_logic_df = pd.read_csv(
    DATA_DIR / "layer_logic.csv",
    sep=";"
)

screw_clamp_logic_df = pd.read_csv(
    DATA_DIR / "screw_clamp_logic.csv",
    sep=";"
)

angle_profile_logic_df = pd.read_csv(
    DATA_DIR / "angle_profile_logic.csv",
    sep=";"
)

beam_profile_logic_df = pd.read_csv(
    DATA_DIR / "beam_profile_logic.csv",
    sep=";"
)

materials_df = pd.read_csv(
    DATA_DIR / "materials.csv",
    sep=";"
)

# Robustly load CSV_3.csv: handle cases where the file was read
# as a single column containing comma-separated values (e.g.
# header like "profile,bj_profile,color"). Read the raw text,
# parse with the csv module and ensure column names are split
# and stripped.
beam_path = DATA_DIR / "CSV_3.csv"
try:
    raw_text = beam_path.read_text(encoding="utf-8-sig")
except Exception:
    raw_text = beam_path.read_text(encoding="utf-8", errors="replace")

import csv

lines = [ln for ln in raw_text.splitlines() if ln.strip() != ""]
if not lines:
    beam_df = pd.DataFrame()
else:
    reader = csv.reader(lines, delimiter=',')
    rows = list(reader)
    if not rows:
        beam_df = pd.DataFrame()
    else:
        header = rows[0]
        data_rows = rows[1:]

        # If header was parsed as a single field containing commas,
        # split it manually and do the same for data rows.
        if len(header) == 1 and ',' in header[0]:
            header = [h.strip() for h in header[0].split(',')]
            fixed_data = []
            for r in data_rows:
                if len(r) == 1 and ',' in r[0]:
                    fixed_data.append([c.strip() for c in r[0].split(',')])
                else:
                    fixed_data.append(r)
            data_rows = fixed_data

        header = [h.strip() for h in header]
        beam_df = pd.DataFrame(data_rows, columns=header)

materials_lookup_path = DATA_DIR / "materials.csv"
if materials_lookup_path.exists():
    materials_lookup_df = pd.read_csv(
        materials_lookup_path,
        sep=";"
    )
else:
    materials_lookup_df = pd.DataFrame()

materials_by_artnr = {}
materials_by_dbnr = {}
materials_by_description = {}
materials_lookup_records = []
if not materials_lookup_df.empty:
    for row in materials_lookup_df.to_dict("records"):
        art_nr = str(row.get("ART.NR.", "") or "").strip()
        db_nr = str(row.get("DB_NR.", "") or "").strip()
        description = str(row.get("BESKRIVELSE_DK", "") or "").strip()
        description_lower = description.lower()

        if art_nr:
            materials_by_artnr[art_nr] = row
        if db_nr:
            materials_by_dbnr[db_nr] = row
        if description_lower and description_lower not in materials_by_description:
            materials_by_description[description_lower] = row

        materials_lookup_records.append(row)

# ---------------------------------------------------
# CLEAN APV DATA
# ---------------------------------------------------

apv_df.columns = (
    apv_df.columns
    .str.strip()
)

# FIX UTF8 / ANSI ISSUES
# Centralized cleaning is handled by load_and_clean_csv and the shared clean_text helper.

# tekst kolonner

text_cols = [
    "profile",
    "montage",
    "profile_category"
]

for col in text_cols:

    if col in apv_df.columns:

        apv_df[col] = apv_df[col].map(clean_text)

# numeriske kolonner

numeric_cols = [
    "sides",
    "apv"
]

for col in numeric_cols:

    if col in apv_df.columns:

        apv_df[col] = apv_df[col].map(clean_numeric)

# ---------------------------------------------------
# FIREBOARD TABLES
# ---------------------------------------------------

@st.cache_data
def load_fireboard(path):

    df = load_and_clean_csv(
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

    df["temperature"] = df["temperature"].map(clean_numeric)
    df = df.dropna(subset=["temperature"])
    df["temperature"] = df["temperature"].astype(int)

    df.set_index(
        "temperature",
        inplace=True
    )

    df.columns = [clean_text(column) for column in df.columns]
    df.columns = pd.to_numeric(
        df.columns,
        errors="coerce"
    )

    df = df.loc[
        :,
        df.columns.notna()
    ]

    df.columns = df.columns.astype(int)

    df = df.apply(lambda column: column.map(clean_numeric))
    df = df.apply(pd.to_numeric, errors="coerce")

    if not df.empty:
        df = df.round(0).astype("Int64")

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

        reset_calculation_state(
            st.session_state
        )

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
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.title(f"📚 {t('calculations')}")

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
        f"➕ {t('new_calculation')}",
        use_container_width=True
    ):

        reset_calculation_state(
            st.session_state
        )

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

                    # RESET STREAMLIT WIDGET STATES

                    widget_keys = [
                        "profile_selectbox",
                        "language_select"
                    ]

                    for key in widget_keys:

                        if key in st.session_state:
                            del st.session_state[key]

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

                    profile_name = str(calc["profile"])

                    if profile_name.startswith("HEB"):
                        st.session_state.profile_type = "HEB"

                    elif profile_name.startswith("HEA"):
                        st.session_state.profile_type = "HEA"

                    elif profile_name.startswith("HEM"):
                        st.session_state.profile_type = "HEM"

                    elif profile_name.startswith("IPE"):
                        st.session_state.profile_type = "IPE"

                    elif profile_name.startswith("INP"):
                        st.session_state.profile_type = "INP"

                    elif profile_name.startswith("UNP"):
                        st.session_state.profile_type = "UNP"

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

        complete_pdf = generate_complete_pdf(
            calculations=st.session_state.calculations,
            language=st.session_state.language,
            session_state=st.session_state,
            t=t,

            PROFILE_IMAGE_MAP=PROFILE_IMAGE_MAP,

            PROJECT_X=PROJECT_X,
            PROJECT_Y=PROJECT_Y,
            PROJECT_LINE_HEIGHT=PROJECT_LINE_HEIGHT,

            CALC_X=CALC_X,
            CALC_Y=CALC_Y,
            CALC_LINE_HEIGHT=CALC_LINE_HEIGHT,

            RESULT_X=RESULT_X,
            RESULT_Y=RESULT_Y,

            PAGE_X=PAGE_X,
            PAGE_Y=PAGE_Y,

            PROFILE_IMAGE_X=PROFILE_IMAGE_X,
            PROFILE_IMAGE_Y=PROFILE_IMAGE_Y,
            PROFILE_IMAGE_WIDTH=PROFILE_IMAGE_WIDTH,
            PROFILE_IMAGE_HEIGHT=PROFILE_IMAGE_HEIGHT,

            PROFILE_TEXT_X=PROFILE_TEXT_X,
            PROFILE_CATEGORY_TEXT_Y=PROFILE_CATEGORY_TEXT_Y,
            PROFILE_TEXT_Y=PROFILE_TEXT_Y,
            PROFILE_CATEGORY_FONT=PROFILE_CATEGORY_FONT,
            PROFILE_TEXT_FONT=PROFILE_TEXT_FONT,

            PROJECT_FONT=PROJECT_FONT,
            CALC_FONT=CALC_FONT,
            RESULT_FONT=RESULT_FONT,
            PAGE_FONT=PAGE_FONT
        )

        st.download_button(
            label=f"📚 {t('download_all_calculations')}",
            data=complete_pdf,
            file_name="Knauf_Fireboard_Rapport.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        # ---------------------------------------------------
        # DOWNLOAD COMBINED MATERIAL LIST
        # ---------------------------------------------------

        if st.session_state.combined_materials:

            st.divider()

            combined_df = pd.concat(

                st.session_state.combined_materials.values(),

                ignore_index=True
            )

            material_sort_order = {
                "Fireboard": 1,
                "spartelmasse": 2,
                "Fugestrimler": 3,
                "Skrue": 4,
                "Vinkelprofil": 5,
                "Bjælkeprofil": 6,
                "PHL profil": 7,
                "Stålklamme": 99
            }

            combined_df["SORT_ORDER"] = 999

            for text, order in material_sort_order.items():

                combined_df.loc[
                    combined_df["BESKRIVELSE"]
                    .astype(str)
                    .str.contains(text, case=False, na=False),
                    "SORT_ORDER"
                ] = order

            combined_df = combined_df.sort_values(
            by="SORT_ORDER",
            kind="stable"
            )

            # ---------------------------------------------------
            # CONVERT NUMBER COLUMNS
            # ---------------------------------------------------

            for col in [
                "FORBRUG PR. LBM",
                "SAMLET MÆNGDE"
            ]:

                if col in combined_df.columns:

                    combined_df[col] = pd.to_numeric(
                        combined_df[col]
                        .astype(str)
                        .str.replace(",", ".", regex=False),
                        errors="coerce"
                    ).fillna(0)

            combined_df["GROUP_KEY"] = (
                combined_df["ART.NR."]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            combined_df["GROUP_KEY"] = combined_df["GROUP_KEY"].replace(
                "",
                pd.NA
            )

            combined_df["GROUP_KEY"] = combined_df["GROUP_KEY"].fillna(
                combined_df["BESKRIVELSE"]
            )

            combined_df["GROUP_KEY"] = combined_df["GROUP_KEY"].fillna(
                "FREMMED_MATERIALE"
            )

            combined_df = combined_df.sort_values(
                by="SORT_ORDER",
                kind="stable"
            )

            total_materials_df = (
                combined_df
                .groupby(
                    [
                        "GROUP_KEY"
                    ],
                    dropna=False,
                    as_index=False,
                    sort=False
                )
                .agg({
                    "SORT_ORDER": "first",
                    "ART.NR.": "first",
                    "DB NR": "first",
                    "PRODUCENT": "first",
                    "BESKRIVELSE": "first",
                    "ENHED": "first",
                    "FORBRUG PR. LBM": "sum",
                    "SAMLET MÆNGDE": "sum"
                })
                .drop(columns=["GROUP_KEY"])
            )

            total_materials_df = total_materials_df.sort_values(
                by=["SORT_ORDER", "BESKRIVELSE"],
                kind="stable"
            )

            combined_export_df = combined_df.drop(
                columns=["SORT_ORDER", "GROUP_KEY"],
                errors="ignore"
            )

            combined_excel = create_materials_excel(
                combined_export_df
            )

            total_export_df = total_materials_df.drop(
                columns=["SORT_ORDER"],
                errors="ignore"
            )

            total_excel = create_materials_excel(
                total_export_df
            )

            st.download_button(
                label="🛒 Download samlet materialeliste",
                data=total_excel,
                file_name="samlet_materialeliste.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )

            st.download_button(
                label="📦 Download materialeliste pr. beregning",
                data=combined_excel,
                file_name="samlet_materialeliste.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )

# ---------------------------------------------------
# STEP NAVIGATION
# ---------------------------------------------------

steps = [

    t("tab_profile"),

    t("tab_cladding"),

    t("tab_fire"),

    t("tab_result")
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
        t("select_profile_category")
    )

    categories = [

        ("H-profiler", t("h_profiles"), "images/h_profiles.png"),
        ("I-profiler", t("i_profiles"), "images/i_profiles.png"),
        ("U-profiler", t("u_profiles"), "images/u_profiles.png"),

        ("Kvadratiske rør varmvalsede", t("shs_hot"), "images/shs_hot.png"),
        ("Kvadratiske rør koldvalsede", t("shs_cold"), "images/shs_cold.png"),

        ("Rektangulære rør varmvalsede", t("rhs_hot"), "images/rhs_hot.png"),
        ("Rektangulære rør koldvalsede", t("rhs_cold"), "images/rhs_cold.png"),

        ("Cirkulære rør middelsvære", t("chs_medium"), "images/chs_medium.png"),
        ("Cirkulære rør svære", t("chs_heavy"), "images/chs_heavy.png"),

        ("Andre profiler", t("other_profiles"), "images/other_profiles.png"),
    ]

    for i in range(0, len(categories), 5):

        cols = st.columns(5)

        for col, (value, label, image) in zip(
            cols,
            categories[i:i+5]
        ):

            with col:

                card(
                    label,
                    image,
                    "category",
                    st.session_state,
                    t,
                    value
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

            st.markdown(f"""
            <div style="
                font-size:15px;
                font-weight:500;
                color:#3e4650;
                margin-bottom:0.3rem;
            ">
                {t("select_profile_type")}
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

                        if "profile_selectbox" in st.session_state:
                            del st.session_state["profile_selectbox"]

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
                .str.startswith(selected_type)
            ]

        profiles = (
            filtered_df["profile"]
            .unique()
        )

        profiles = sorted(
            profiles,
            key=lambda x: [
                clean_numeric(v) or 0
                for v in (
                    x.replace("HEB", "")
                     .replace("HEA", "")
                     .replace("HEM", "")
                     .replace("IPE", "")
                     .replace("INP", "")
                     .replace("UNP", "")
                     .split("x")
                )
            ]
        )

        if len(profiles) == 0:

            st.error(
                t("no_profiles_found")
            )

            st.stop()

        # ---------------------------------------------------
        # PROFILVALG
        # ---------------------------------------------------

        selected_profile = st.selectbox(
            t("select_profile_size"),
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
            t("profile_name_optional"),
            value=st.session_state.custom_profile_name
        )

        st.session_state.custom_profile_name = (
            custom_profile_name
        )

        st.divider()

        # ---------------------------------------------------
        # METODEVALG
        # ---------------------------------------------------

        st.markdown(f"""
        <div style="
            font-size:15px;
            font-weight:500;
            color:#3e4650;
            margin-bottom:0.3rem;
        ">
            {t("select_method")}
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            direkte_selected = (
                st.session_state.apv_method
                == "Direkte"
            )

            if st.button(
                t("enter_apv"),
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
                t("calculate_apv"),
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
               t("enter_apv_ratio"),
                value=(
                    str(st.session_state.custom_apv)
                    if st.session_state.custom_apv
                    else ""
                )
            )

            numeric_apv = clean_numeric(custom_apv)
            st.session_state.custom_apv = (
                int(numeric_apv)
                if numeric_apv is not None
                else None
            )

        # ---------------------------------------------------
        # BEREGN AP/V
        # ---------------------------------------------------

        else:

            ap_input = st.text_input(
                t("enter_perimeter"),
                value=st.session_state.surface_area
            )

            st.markdown(
                t("enter_area")
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
                    t("calculate"),
                    use_container_width=True
                )

            if calculate_clicked:

                ap = clean_numeric(ap_input)
                v = clean_numeric(v_input)

                if ap is None or v is None or v == 0:

                    st.error(
                        t("invalid_numbers")
                    )

                else:

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

            if st.session_state.custom_apv:

                st.info(
                    f"{t('calculated_apv')}: "
                    f"{st.session_state.custom_apv} m²/m³"
                )

    # ---------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------

    st.divider()

    col1, col2 = st.columns([1,1])

    with col2:

        if st.button(
            t("next"),
            use_container_width=True
        ):

            st.session_state.current_step = 1

            st.rerun()
# ---------------------------------------------------
# TAB 2 - INDDÆKNING
# ---------------------------------------------------

if current_step == 1:

    st.subheader(
        t("select_cladding_type")
    )

    col1, col2 = st.columns(2)

    with col1:

        card(
            t("clamping_solution"),
            "images/klamme.png",
            "montage",
            st.session_state,
            t,
            "Klammeløsning"
        )

    with col2:

        card(
            t("beam_or_phl_profile"),
            "images/bjaelke.png",
            "montage",
            st.session_state,
            t,
            "Bjælkeprofil eller PHL profil"
        )

    montage = st.session_state.montage

    if not montage:

        st.stop()

    st.divider()

    st.subheader(
        t("select_cladding_sides")
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
                t("one_side_not_possible"),
                "images/side1.png"
            )

        with col2:

            disabled_card(
                t("two_sides_not_possible"),
                "images/side2.png"
            )

        with col3:

            disabled_card(
                t("three_sides_not_possible"),
                "images/side3.png"
            )

        with col4:

            card(
                "4",
                "images/side4.png",
                "sides",
                st.session_state,
                t
            )

    else:

        with col1:

            card(
                "1",
                "images/side1.png",
                "sides",
                st.session_state,
                t
            )

        with col2:

            card(
                "2",
                "images/side2.png",
                "sides",
                st.session_state,
                t
            )

        with col3:

            card(
                "3",
                "images/side3.png",
                "sides",
                st.session_state,
                t
            )

        with col4:

            card(
                "4",
                "images/side4.png",
                "sides",
                st.session_state,
                t
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
            t("previous"),
            use_container_width=True
        ):

            st.session_state.current_step = 0

            st.rerun()

    with col2:

        if st.button(
            t("next"),
            use_container_width=True
        ):

            st.session_state.current_step = 2

            st.rerun()
# ---------------------------------------------------
# TAB 3 - BRAND
# ---------------------------------------------------

if current_step == 2:

    st.subheader(
        t("fire_requirements")
    )

    st.divider()

    fire_options = [30, 60, 90, 120]

    saved_fire_time = st.session_state.get(
        "fire_time"
    )

    if saved_fire_time not in fire_options:
        saved_fire_time = 30

    fire_time = st.selectbox(
        t("select_fire_protection_time"),
        fire_options,
        index=fire_options.index(saved_fire_time)
    )

    st.divider()

    # ---------------------------------------------------
    # STÅLTEMPERATUR
    # ---------------------------------------------------

    temperature = st.text_input(
        t("enter_design_steel_temperature"),
        value=str(
            st.session_state.get("temperature") or 450
        )
    )

    # ---------------------------------------------------
    # VALIDERING
    # ---------------------------------------------------

    validation_message = validate_temperature(
        temperature,
        t
    )

    if validation_message:

        st.error(validation_message)

        st.stop()

    temperature = int(temperature)

    st.session_state.fire_time = fire_time
    st.session_state.temperature = temperature

    # ---------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------

    st.divider()

    col1, col2 = st.columns([1,1])

    with col1:

        if st.button(
            t("previous"),
            use_container_width=True
        ):

            st.session_state.current_step = 1

            st.rerun()

    with col2:

        if st.button(
            t("next"),
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
    # CLEAN APV DATA
    # ---------------------------------------------------

    apv_df.columns = (
        apv_df.columns
        .str.strip()
    )

    text_cols = [
        "profile",
        "montage",
        "profile_category"
    ]

    for col in text_cols:

        if col in apv_df.columns:

            apv_df[col] = (
                apv_df[col]
                .astype(str)
                .str.strip()
            )

    numeric_cols = [
        "sides",
        "apv"
    ]

    for col in numeric_cols:

        if col in apv_df.columns:

            apv_df[col] = pd.to_numeric(
                apv_df[col],
                errors="coerce"
            )

    # ---------------------------------------------------
    # STANDARD PROFILER
    # ---------------------------------------------------

    if category != "Andre profiler":

        row = apv_df[
            (
                apv_df["profile"]
                .astype(str)
                .str.strip()
                ==
                str(selected_profile).strip()
            )
            &
            (
                apv_df["montage"]
                .astype(str)
                .str.strip()
                ==
                str(montage).strip()
            )
            &
            (
                apv_df["sides"]
                .astype(int)
                ==
                int(sides)
            )
        ]

        if row.empty:

            st.error(
                "Denne kombination er ikke mulig"
            )

            st.write("DEBUG")

            st.write(
                "selected_profile:",
                selected_profile
            )

            st.write(
                "montage:",
                montage
            )

            st.write(
                "sides:",
                sides
            )

            st.write(
                "Profiler i CSV:"
            )

            st.write(
                apv_df["profile"]
                .unique()
            )

            st.write(
                "Montage i CSV:"
            )

            st.write(
                apv_df["montage"]
                .unique()
            )

            st.write(
                "Sides i CSV:"
            )

            st.write(
                apv_df["sides"]
                .unique()
            )

            st.stop()

        apv = int(
            row.iloc[0]["apv"]
        )

    # ---------------------------------------------------
    # ANDRE PROFILER
    # ---------------------------------------------------

    else:

        if st.session_state.custom_apv is None:

            st.error(
                "Indtast gyldig Ap/V værdi"
            )

            st.stop()

        apv = int(
            st.session_state.custom_apv
        )

        selected_profile = (

            st.session_state.custom_profile_name

            if st.session_state.custom_profile_name
            else t("special_profile")
        )

    table = fire_tables[fire_time]

    # ---------------------------------------------------
    # FIND TYKKELSE
    # ---------------------------------------------------

    validation_message = validate_fireboard_lookup(
        table,
        apv,
        temperature
    )

    if validation_message:

        st.error(validation_message)

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
        t("tab_result")
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
            <b>{t("calculated_profile_ratio_label")}:</b>
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
            <b>{t("profile_must_be_clad_with")}:</b>
            {int(thickness)} mm Knauf Fireboard
        </div>
        """, unsafe_allow_html=True)

    else:

        st.info(
            t("fill_all_steps_to_see_result")
        )

        st.stop()

    # Systemopbygning and Materialeforbrug moved below inside collapsed expanders

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
    # PROJEKTOPLYSNINGER
    # ---------------------------------------------------

    st.divider()

    st.header(
        t("project_information")
    )

    col1, col2 = st.columns(2)

    with col1:

        project_name = st.text_input(
            t("project"),
            value=st.session_state.project_name
        )

        prepared_by = st.text_input(
            t("prepared_by"),
            value=st.session_state.prepared_by
        )

    with col2:

        company = st.text_input(
            t("company"),
            value=st.session_state.company
        )

        report_date = st.text_input(
            t("date"),
            value=datetime.now().strftime("%d-%m-%Y")
        )

    description = st.text_area(
        t("description"),
        value=st.session_state.description,
        height=120
    )

    st.session_state.project_name = project_name
    st.session_state.company = company
    st.session_state.prepared_by = prepared_by
    st.session_state.description = description

    # ---------------------------------------------------
    # DOWNLOAD DENNE BEREGNING
    # ---------------------------------------------------

    single_calc_pdf = generate_single_pdf(
        calc=calculation_data,
        language=st.session_state.language,
        translations=translations,
        session_state=st.session_state,
        PROFILE_IMAGE_MAP=PROFILE_IMAGE_MAP,

        PROJECT_X=PROJECT_X,
        PROJECT_Y=PROJECT_Y,
        PROJECT_LINE_HEIGHT=PROJECT_LINE_HEIGHT,

        CALC_X=CALC_X,
        CALC_Y=CALC_Y,
        CALC_LINE_HEIGHT=CALC_LINE_HEIGHT,

        RESULT_X=RESULT_X,
        RESULT_Y=RESULT_Y,

        PAGE_X=PAGE_X,
        PAGE_Y=PAGE_Y,

        PROFILE_IMAGE_X=PROFILE_IMAGE_X,
        PROFILE_IMAGE_Y=PROFILE_IMAGE_Y,
        PROFILE_IMAGE_WIDTH=PROFILE_IMAGE_WIDTH,
        PROFILE_IMAGE_HEIGHT=PROFILE_IMAGE_HEIGHT,

        PROFILE_TEXT_X=PROFILE_TEXT_X,
        PROFILE_CATEGORY_TEXT_Y=PROFILE_CATEGORY_TEXT_Y,
        PROFILE_TEXT_Y=PROFILE_TEXT_Y,
        PROFILE_CATEGORY_FONT=PROFILE_CATEGORY_FONT,
        PROFILE_TEXT_FONT=PROFILE_TEXT_FONT,

        PROJECT_FONT=PROJECT_FONT,
        CALC_FONT=CALC_FONT,
        RESULT_FONT=RESULT_FONT,
        PAGE_FONT=PAGE_FONT
    )

    st.download_button(
        label=t("download_this_calculation"),
        data=single_calc_pdf,
        file_name=(
            f"{selected_profile}_"
            f"R{fire_time}.pdf"
        ),
        mime="application/pdf",
        use_container_width=True
    )

    # ---------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------

    st.divider()

    col1, col2 = st.columns([1,1])

    with col1:

        if st.button(
            t("previous"),
            use_container_width=True
        ):

            st.session_state.current_step = 2

            st.rerun()

    with col2:

        button_text = (
            t("update_calculation")
            if st.session_state.edit_index is not None
            else t("add_calculation")
        )

        if st.button(
            button_text,
            use_container_width=True,
            key="save_calculation_button"
        ):

            if st.session_state.edit_index is not None:

                st.session_state.calculations[
                    st.session_state.edit_index
                ] = calculation_data

                st.session_state.edit_index = None

                st.session_state.editing = False

            else:

                if not (
                    st.session_state.calculations
                    and st.session_state.calculations[-1]
                    == calculation_data
                ):
                
                    st.session_state.calculations.append(
                        calculation_data
                    )

            st.session_state.last_updated = datetime.now()

            st.rerun()

    # ---------------------------------------------------
    # MATERIALERFORBRUG
    # ---------------------------------------------------

    if category == "Andre profiler":

        st.info(
            f"**{t('material_consumption_unavailable_title')}**\n\n"
            f"{t('material_consumption_unavailable_text')}"
        )

        st.stop()

    st.header(t("materials_header"))

    col1, col2 = st.columns(2)

    with col1:

        profile_length = st.text_input(
            t("profile_length"),
            value="6,0"
        )

        profile_length = clean_numeric(profile_length)

        if profile_length is None:
            profile_length = 0

    with col2:

        waste_percent = st.text_input(
            t("waste_percent"),
            value="10"
        )

        waste_percent = clean_numeric(waste_percent)

        if waste_percent is None:
            waste_percent = 0

    amount_row = apv_df[
        (
            apv_df["profile"]
            .map(clean_text)
            ==
            clean_text(selected_profile)
        )
        &
        (
            apv_df["montage"]
            .map(clean_text)
            ==
            clean_text(montage)
        )
        &
        (
            apv_df["sides"]
            .map(clean_numeric)
            .fillna(0)
            .astype(int)
            ==
            int(sides)
        )
    ]

    if not amount_row.empty:

        amount_row = amount_row.iloc[0]

        fireboard_rate = (
            clean_numeric(
                amount_row[
                    "Antal m² fireboard pr. m profil"
                ]
            ) or 0
        )

        beam_rate = (
            clean_numeric(
                amount_row[
                    "Antal bjælkeprofiler/PHL pr. m profil"
                ]
            ) or 0
        )

        angle_rate = (
            clean_numeric(
                amount_row[
                    "Antal vinkelprofil pr. m profil"
                ]
            ) or 0
        )

        screw_rate = (
            clean_numeric(
                amount_row[
                    "Antal skruer pr. m profil"
                ]
            ) or 0
        )

        staple_rate = (
            clean_numeric(
                amount_row[
                    "Antal klammer pr. m profil"
                ]
            ) or 0
        )

        beam_text = resolve_beam_text(
            beam_profile_logic_df,
            selected_profile,
            clean_text
        )

        materials = []

        current_thickness = clean_numeric(thickness) or 0
        layer_rows = layer_logic_df[
            layer_logic_df["total_mm"]
            .map(clean_numeric)
            .fillna(0)
            ==
            current_thickness
        ]

        if "variant" in layer_rows.columns:
            available_variants = layer_rows["variant"].dropna().unique().tolist()
            if len(available_variants) > 1:
                variant_labels = {
                    variant: build_variant_label(
                        layer_rows[layer_rows["variant"] == variant],
                        clean_numeric
                    )
                    for variant in available_variants
                }
                selected_variant = st.selectbox(
                    t("select_layer_build_up"),
                    available_variants,
                    format_func=lambda variant: variant_labels.get(variant, variant),
                )
                layer_rows = layer_rows[layer_rows["variant"] == selected_variant]
            elif len(available_variants) == 1:
                layer_rows = layer_rows[layer_rows["variant"] == available_variants[0]]

        angle_lookup = angle_profile_logic_df[
            angle_profile_logic_df["sides"]
            .map(clean_numeric)
            .fillna(0)
            ==
            int(sides)
        ]

        materials.extend(
            generate_materials(
                fireboard_rate,
                layer_rows,
                thickness,
                screw_rate,
                staple_rate,
                angle_rate,
                angle_lookup,
                beam_rate,
                beam_text,
                screw_clamp_logic_df,
                materials_lookup_df,
                materials_by_artnr,
                materials_by_dbnr,
                get_material_label,
                clean_numeric,
                clean_text
            )
        )

        materials_table_df = build_materials_dataframe(
            materials,
            profile_length,
            waste_percent,
            fireboard_rate,
            materials_by_artnr,
            materials_by_dbnr,
            materials_by_description
        )

        if st.session_state.language == "EN":

            materials_table_df["PRODUCENT"] = (
                materials_table_df["PRODUCENT"]
                .astype(str)
                .str.strip()
                .replace({
                    "Fremmed materiale": "Foreign material"
                })
            )

            materials_table_df["BESKRIVELSE"] = (
                materials_table_df["BESKRIVELSE"]
                .astype(str)
                .str.strip()
                .replace({
                    "Skrue": "Screw",
                    "Stålklamme": "Steel clamp",
                    "Vinkelprofil": "Angle profile",
                    "Bjælkeprofil": "Beam profile",
                    "Fugestrimler glasfiber": "Fiberglass joint tape",
                    "rød": "red",
                    "gul": "yellow",
                    "grøn": "green",
                    "brun": "brown",
                    "blå": "blue",
                    "hvid": "white",
                    "sort": "black",
                    "orange": "orange",
                    "PHL profil": "PHL Profile"
                }, regex=True)
            )

        materials_table_df.columns = [
            t("material_artnr"),
            t("material_dbnr"),
            t("material_manufacturer"),
            t("material_description"),
            t("material_consumption"),
            t("material_unit"),
            t("material_total"),
            t("material_co2"),
            t("material_epd"),
            t("material_datasheet")
        ]

        render_materials_table(materials_table_df)

        # ---------------------------------------------------
        # SAVE MATERIAL LIST
        # ---------------------------------------------------

        export_df = materials_table_df.iloc[:, :-3].copy()

        calculation_key = (
            f"{selected_profile}_"
            f"R{fire_time}_"
            f"{temperature}"
        )

        export_df["SYSTEM"] = calculation_key
        
        st.session_state.combined_materials[
            calculation_key
        ] = export_df

        st.markdown(
            f"""
            <div style="
                font-size: 0.85rem;
                color: #666666;
                margin-top: -1rem;
                margin-bottom: 1rem;
            ">
                {t("co2_note")}
            </div>
            """,
            unsafe_allow_html=True
        )

        co2_values = pd.to_numeric(

            materials_table_df[
                t("material_co2")
            ]
            .astype(str)
            .str.replace(",", ".", regex=False),

            errors="coerce"
        )

        total_co2 = co2_values.sum()

        st.markdown(
            f"""
            <div style="
                text-align: left;
                color: #444444;
                font-size: 1.5rem;
                font-weight: 700;
                margin-top: -1rem;
                margin-bottom: 1rem;
            ">
                {t("total_co2_footprint")}: {format_number(total_co2)} kg CO2e
            </div>
            """,
            unsafe_allow_html=True
        )

        excel_export_df = materials_table_df.iloc[:, :-3]

        excel_file = create_materials_excel(
            excel_export_df
        )

        st.download_button(
            label="📥 Download Excel",
            data=excel_file,
            file_name="materialeliste.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )


