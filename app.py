import base64
from io import BytesIO
from datetime import datetime

import streamlit as st
import pandas as pd

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

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

p,
label {

    color: #3e4650;
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

    background-color: white !important;

    color: #003b7a !important;

    font-size: 14px;

    font-weight: 600;

    transition: all 0.15s ease;

    box-shadow: none !important;

    outline: none !important;
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

    background-color: #009fe3 !important;

    border-color: #009fe3 !important;

    color: white !important;

    font-weight: 700 !important;
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
SIDEBAR ACTIVE CALCULATION
--------------------------------------------------- */

section[data-testid="stSidebar"] button[kind="primary"] {

    background:#009fe3 !important;

    border:1px solid #009fe3 !important;

    color:white !important;

    font-weight:700 !important;

    box-shadow:none !important;
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

h1, h2, h3 {

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

    "category": None,
    "montage": None,
    "sides": None,

    "calculations": [],

    "edit_index": None,
    "editing": False,

    "project_name": "",
    "company": "",
    "prepared_by": "",
    "description": "",

    "last_updated": datetime.now()
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value

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

col1, col2, col3 = st.columns([6, 2, 2])

with col1:

    st.title(
        "Brandbeskyttelse af stålkonstruktioner"
    )

# ---------------------------------------------------
# NY BEREGNING
# ---------------------------------------------------

with col2:

    st.write("")
    st.write("")

    if st.button(
        "🔄 Ny beregning",
        use_container_width=True
    ):

        reset_keys = [

            "category",
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
        "🗑️ Nyt projekt",
        use_container_width=True
    ):

        st.session_state.clear()

        st.rerun()

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

    div[data-testid="stSidebar"] button[kind="primary"] {

        border: 2px solid #00c853 !important;

        background: linear-gradient(
            135deg,
            rgba(0,200,83,0.35),
            rgba(0,120,50,0.50)
        ) !important;

        color: white !important;

        font-weight: 700 !important;

        box-shadow: 0 0 12px rgba(0,200,83,0.35);
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

            col1, col2 = st.columns([5,1])

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

                button_type = (
                    "primary"
                    if is_active
                    else "secondary"
                )

                if st.button(
                    label,
                    key=f"sidebar_calc_{idx}",
                    type=button_type,
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
    <div style="
        border:{border};
        background-color:{background};
        border-radius:4px;
        padding:10px;
        text-align:center;
        min-height:135px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        transition: all 0.15s ease;
    ">

        <img src="data:image/png;base64,{image_base64}"
        style="
            width:72px;
            height:72px;
            object-fit:contain;
            margin-bottom:8px;
        "/>

        <div style="
            font-size:16px;
            font-weight:700;
            color:#2d343c;
            text-align:center;
            line-height:1.25;
        ">
            {label}
        </div>

    </div>
    """

    st.components.v1.html(
        html,
        height=190
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
    <div style="
        border:1px solid #d9dde3;
        background:white;
        opacity:0.45;
        border-radius:4px;
        padding:14px;
        text-align:center;
        min-height:160px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
    ">

        <img src="data:image/png;base64,{image_base64}"
        style="
            width:90px;
            height:90px;
            object-fit:contain;
            margin-bottom:12px;
        "/>

        <div style="
            font-size:16px;
            font-weight:700;
            color:#999999;
            text-align:center;
            line-height:1.25;
        ">
            {label}
        </div>

    </div>
    """

    st.components.v1.html(
        html,
        height=190
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
                border-radius:4px;
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

    filtered_df = apv_df[
        apv_df["profile_category"]
        == category
    ]

    profiles = filtered_df[
        "profile"
    ].unique()

    selected_profile = st.selectbox(
        "Vælg profilstørrelse",
        profiles
    )

    st.session_state.selected_profile = (
    selected_profile
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

    fire_time = st.selectbox(
        "Vælg brandbeskyttelsestid",
        [30, 60, 90, 120]
    )

    st.divider()

    # ---------------------------------------------------
    # STÅLTEMPERATUR
    # ---------------------------------------------------

    temperature = st.text_input(
        "Indtast dimensionerende ståltemperatur (°C)",
        value=str(
            st.session_state.get(
                "temperature",
                450
            )
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

apv = None
thickness = None

if (
    selected_profile
    and montage
    and sides
    and fire_time
    and temperature
):

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
    # FIND TYKKELSE
    # ---------------------------------------------------

    table = fire_tables[fire_time]

    if apv not in table.columns:

        st.error(
            "Der findes ingen løsning"
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

# ---------------------------------------------------
# PDF FUNCTION
# ---------------------------------------------------

def generate_pdf():

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    elements = []

    # ---------------------------------------------------
    # TITLE
    # ---------------------------------------------------

    title = Paragraph(
        "Brandbeskyttelse af stålkonstruktioner med Knauf Fireboard",
        styles['Title']
    )

    elements.append(title)

    elements.append(
        Spacer(1, 25)
    )

    # ---------------------------------------------------
    # PROJEKTOPLYSNINGER
    # ---------------------------------------------------

    project_data = [

        ["Projekt", st.session_state.project_name],
        ["Udarbejdet af", st.session_state.prepared_by],
        ["Firma", st.session_state.company],
        ["Dato", datetime.now().strftime("%d-%m-%Y")],
        ["Beskrivelse", st.session_state.description],
    ]

    project_table = Table(
        project_data,
        colWidths=[180, 300]
    )

    project_table.setStyle(

        TableStyle([

            ('GRID', (0,0), (-1,-1), 1, colors.black),

            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),

            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),

            ('FONTSIZE', (0,0), (-1,-1), 10),

            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ])
    )

    elements.append(project_table)

    elements.append(
        Spacer(1, 25)
    )

    # ---------------------------------------------------
    # INPUT DATA
    # ---------------------------------------------------

    input_data = [

        ["Profilkategori", category],
        ["Profil", str(selected_profile)],
        ["Inddækning", f"{sides} sider"],
        ["Montage", montage],
        ["Brandtid", f"{fire_time} minutter"],
        ["Temperatur", f"{temperature} °C"],
        ["Ap/V", f"{apv} m²/m³"],
    ]

    input_table = Table(
        input_data,
        colWidths=[180, 300]
    )

    input_table.setStyle(

        TableStyle([

            ('GRID', (0,0), (-1,-1), 1, colors.black),

            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),

            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),

            ('FONTSIZE', (0,0), (-1,-1), 10),

            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ])
    )

    elements.append(input_table)

    elements.append(
        Spacer(1, 30)
    )

    # ---------------------------------------------------
    # RESULTAT
    # ---------------------------------------------------

    result = Paragraph(
        f"<b>Profil skal inddækkes med "
        f"{int(thickness)} mm "
        f"Knauf Fireboard</b>",
        styles['Heading2']
    )

    elements.append(result)

    elements.append(
        Spacer(1, 20)
    )

    # ---------------------------------------------------
    # NOTE
    # ---------------------------------------------------

    note = Paragraph(
        "Monteres iht. gældende Knauf montagevejledning.",
        styles['BodyText']
    )

    elements.append(note)

    # ---------------------------------------------------
    # BUILD PDF
    # ---------------------------------------------------

    doc.build(elements)

    buffer.seek(0)

    return buffer

# ---------------------------------------------------
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
    # PDF DOWNLOAD
    # ---------------------------------------------------

    pdf_file = generate_pdf()

    st.download_button(
        label="📄 Download PDF rapport",
        data=pdf_file,
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
        "thickness": thickness
    }

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
