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
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Brandbeskyttelse af stålkonstruktioner",
    layout="wide"
)

# ---------------------------------------------------
# STYLE
# ---------------------------------------------------

st.markdown("""
<style>

.block-container {

    max-width: 1500px;
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    margin: auto;
}

div.stButton > button {

    width: 100%;
    margin-top: -14px;

    border-radius: 0 0 16px 16px;

    background-color: #0b1220;

    border: 1px solid #31333F;

    color: white;

    font-size: 15px;
    font-weight: 600;

    height: 46px;
}

div.stButton > button:hover {

    border: 1px solid #00c853;
    color: #00c853;
}

</style>
""", unsafe_allow_html=True)

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

    if st.session_state.calculations:

        project_text = (
            st.session_state.project_name
            if st.session_state.project_name
            else "Unavngivet projekt"
        )

        calc_count = len(
            st.session_state.calculations
        )

        updated = (
            st.session_state.last_updated
            .strftime("%d-%m-%Y %H:%M")
        )

        st.markdown(f"""
        <div style="
        padding:14px 18px;
        border:1px solid #1f3b2d;
        border-radius:10px;
        background-color:rgba(20,60,35,0.25);
        margin-top:10px;
        margin-bottom:10px;
        ">

        <div style="
        font-size:18px;
        font-weight:600;
        color:#7CFC9A;
        margin-bottom:6px;
        ">
        🟢 Aktivt projekt
        </div>

        <div style="font-size:15px;">
        📁 {project_text}
        </div>

        <div style="
        font-size:14px;
        margin-top:4px;
        ">
        {calc_count} gemte beregninger
        </div>

        <div style="
        font-size:13px;
        opacity:0.7;
        margin-top:4px;
        ">
        Senest ændret: {updated}
        </div>

        </div>
        """, unsafe_allow_html=True)

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
            "sides"
        ]

        for key in reset_keys:

            st.session_state[key] = None

        st.rerun()

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

    if st.button(
        "➕ Ny beregning",
        use_container_width=True
    ):

        reset_keys = [
            "category",
            "montage",
            "sides"
        ]

        for key in reset_keys:

            st.session_state[key] = None

        st.session_state.editing = False

        st.rerun()

    st.divider()

    if st.session_state.calculations:

        for idx, calc in enumerate(
            st.session_state.calculations
        ):

            label = (
                f"{calc['profile']} · "
                f"R{calc['fire_time']}"
            )

            if st.button(
                label,
                key=f"sidebar_calc_{idx}",
                use_container_width=True
            ):

                st.session_state.category = calc["category"]
                st.session_state.montage = calc["montage"]
                st.session_state.sides = calc["sides"]

                st.session_state.edit_index = idx
                st.session_state.editing = True

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

    border = (
        "3px solid #00c853"
        if selected
        else "1px solid #31333F"
    )

    background = (
        "#111827"
        if selected
        else "#0b1220"
    )

    image_base64 = get_base64_image(
        image_path
    )

    html = f"""
    <div style="
        border:{border};
        background-color:{background};
        border-radius:16px;
        padding:20px;
        text-align:center;
        min-height:200px;
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
            margin-bottom:20px;
        "/>

        <div style="
            font-size:18px;
            font-weight:700;
            color:white;
            text-align:center;
        ">
            {label}
        </div>

    </div>
    """

    st.components.v1.html(
        html,
        height=240
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
        border:1px solid #31333F;
        background-color:#161616;
        opacity:0.45;
        border-radius:16px;
        padding:20px;
        text-align:center;
        min-height:240px;
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
            margin-bottom:20px;
        "/>

        <div style="
            font-size:18px;
            font-weight:700;
            color:#999999;
            text-align:center;
        ">
            {label}
        </div>

    </div>
    """

    st.components.v1.html(
        html,
        height=240
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
# STEP HEADER
# ---------------------------------------------------

cols = st.columns(len(steps))

for idx, step in enumerate(steps):

    with cols[idx]:

        active = idx == current_step

        if active:

            st.success(f"{idx+1}. {step}")

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

    temperature = st.number_input(
        "Indtast dimensionerende ståltemperatur (°C)",
        min_value=350,
        max_value=750,
        value=450,
        step=1
    )

    temperature = int(temperature)

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
# FIND AP/V
# ---------------------------------------------------

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

thickness = table.loc[
    int(temperature),
    apv
]

# ---------------------------------------------------
# TAB 4 - RESULTAT
# ---------------------------------------------------

if current_step == 3:

    st.subheader(
        "Resultat"
    )

    st.divider()

    st.success(
        f"Beregnet profilforhold Ap/V: "
        f"{apv} m²/m³"
    )

    st.success(
        f"Profil skal inddækkes med "
        f"{int(thickness)} mm "
        f"Knauf Fireboard"
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

        report_date = st.date_input(
            "Dato"
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
