import base64
from io import BytesIO

import streamlit as st
import pandas as pd
from datetime import date

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

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(
    page_title="Brandbeskyttelse af stålkonstruktioner",
    layout="wide"
)

# -------------------------
# CUSTOM WIDTH + STYLE
# -------------------------

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

# -------------------------
# HEADER
# -------------------------

col1, col2 = st.columns([8, 2])

with col1:

    st.title(
        "Brandbeskyttelse af stålkonstruktioner"
    )

with col2:

    st.write("")
    st.write("")

    if st.button(
        "🔄 Start ny beregning",
        use_container_width=True
    ):

        st.session_state.clear()
        st.rerun()

# -------------------------
# LOAD DATA
# -------------------------

apv_df = pd.read_csv(
    "data/apv.csv",
    sep=";"
)

# -------------------------
# FIREBOARD DATA
# -------------------------

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
    ),
}

# -------------------------
# SESSION STATE
# -------------------------

for key in [

    "category",
    "montage",
    "sides"

]:

    if key not in st.session_state:

        st.session_state[key] = None

# -------------------------
# CARD FUNCTIONS
# -------------------------

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

# -------------------------
# PROFILKATEGORI
# -------------------------

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

# -------------------------
# ANDRE PROFILER
# -------------------------

custom_profile = (
    category == "Andre profiler"
)

if custom_profile:

    st.divider()

    st.subheader(
        "Valgfrie profiler"
    )

    apv_mode = st.radio(
        "Hvordan vil du bestemme Ap/V?",
        [
            "Indtast Ap/V direkte",
            "Beregn Ap/V"
        ]
    )

    if apv_mode == "Indtast Ap/V direkte":

        apv = st.number_input(
            "Indtast Ap/V forhold",
            min_value=10,
            max_value=500,
            value=150
        )

    else:

        st.markdown(
            "### Beregning af profilforhold"
        )

        st.markdown("""
        Beregning udføres iht. **EN 13381-4**  
        og **DS/EN 1993-1-2 (Eurocode 3)**.
        """)

        st.latex(
            r'''
            \frac{A_p}{V}
            =
            \frac{
                \mathrm{Indvendig\ omkreds\ [mm]}
            }{
                \mathrm{Tværsnitsareal\ [mm^2]}
            }
            \times 1000
            '''
        )

        st.caption(
            "Resultat angives i m²/m³"
        )

        perimeter = st.number_input(
            "Indvendig omkreds (mm)",
            min_value=1.0,
            value=300.0
        )

        area = st.number_input(
            "Stålets tværsnitsareal (mm²)",
            min_value=1.0,
            value=2000.0
        )

        apv = round(
            (perimeter / area) * 1000
        )

        st.success(
            f"Beregnet Ap/V: {apv} m²/m³"
        )

    profile = "Andet profil"

    montage = "Ikke relevant"

    sides = "Ikke relevant"

else:

    # -------------------------
    # PROFILER
    # -------------------------

    st.divider()

    filtered_df = apv_df[
        apv_df["profile_category"]
        == category
    ]

    profiles = filtered_df[
        "profile"
    ].unique()

    def sort_profiles(profiles):

        def extract_number(x):

            nums = ''.join(
                filter(
                    str.isdigit,
                    str(x)
                )
            )

            return int(nums) if nums else 0

        return sorted(
            profiles,
            key=extract_number
        )

    def format_profile(
        profile,
        category
    ):

        profile = str(profile)

        if (
            "Kvadratiske" in category
            or
            "Rektangulære" in category
        ):

            return f"{profile} mm"

        if "Cirkulære" in category:

            if "x" in profile.lower():

                diameter = (
                    profile
                    .split("x")[0]
                    .replace("CHS", "")
                    .strip()
                )

                return f"Ø{diameter} mm"

            return f"Ø{profile} mm"

        return profile

    formatted_profiles = {

        format_profile(
            p,
            category
        ): p

        for p in sort_profiles(profiles)
    }

    selected_profile_label = st.selectbox(
        "Vælg profilstørrelse",
        list(formatted_profiles.keys())
    )

    profile = formatted_profiles[
        selected_profile_label
    ]

# -------------------------
# MONTAGE + SIDER
# -------------------------

if not custom_profile:

    st.divider()

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

    # -------------------------
    # SIDER
    # -------------------------

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

# -------------------------
# BRANDTID
# -------------------------

st.divider()

fire_time = st.selectbox(
    "Vælg brandbeskyttelsestid",
    [30, 60, 90, 120],
    index=None,
    placeholder="Vælg brandtid"
)

if fire_time is None:
    st.stop()

# -------------------------
# TEMPERATUR
# -------------------------

st.divider()

temperature = st.number_input(
    "Indtast dimensionerende ståltemperatur (°C)",
    min_value=350,
    max_value=750,
    value=450,
    step=1
)

temperature = int(temperature)

# -------------------------
# FIND AP/V
# -------------------------

if not custom_profile:

    row = apv_df[

        (
            apv_df["profile"]
            == profile
        )

        &

        (
            apv_df["montage"]
            == montage
        )

        &

        (
            apv_df["sides"]
            == sides
        )
    ]

    if row.empty:

        st.error(
            "Denne kombination er ikke mulig "
            "for det valgte profil"
        )

        st.stop()

    apv = int(
        row.iloc[0]["apv"]
    )

# -------------------------
# FIND TYKKELSE
# -------------------------

table = fire_tables[fire_time]

if apv not in table.columns:

    st.error(
        "Der findes ingen Fireboard løsning "
        "for denne kombination"
    )

    st.stop()

if temperature not in table.index:

    st.error(
        "Temperaturen findes ikke i databasen"
    )

    st.stop()

thickness = table.loc[
    temperature,
    apv
]

if pd.isna(thickness):

    st.error(
        "Denne kombination er ikke mulig"
    )

    st.stop()

# -------------------------
# PROJEKTOPLYSNINGER
# -------------------------

st.divider()

st.subheader(
    "Projektoplysninger"
)

col1, col2 = st.columns(2)

with col1:

    project_name = st.text_input(
        "Projekt"
    )

with col2:

    company_name = st.text_input(
        "Firma"
    )

col3, col4 = st.columns(2)

with col3:

    prepared_by = st.text_input(
        "Udarbejdet af"
    )

with col4:

    report_date = st.date_input(
        "Dato",
        value=date.today(),
        format="DD-MM-YYYY"
    )

description = st.text_area(
    "Beskrivelse"
)

# -------------------------
# PDF FUNCTION
# -------------------------

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

    title = Paragraph(
        "Brandbeskyttelse af stålkonstruktioner med Knauf Fireboard",
        styles['Title']
    )

    elements.append(title)

    elements.append(
        Spacer(1, 25)
    )

    project_data = [

        ["Projekt", project_name],
        ["Beregning udført af", prepared_by],
        ["Firma", company_name],
        ["Dato", report_date.strftime("%d-%m-%Y")],
        ["Beskrivelse", description],
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

    input_data = [
        
    ["Profilkategori", category],
    ["Valgt stålprofil", str(profile)],
    ["Inddækning", f"{sides} sider"],
    ["Fastgørelsesmetode", montage],
    ["Brandbeskyttelsestid", f"{fire_time} minutter"],
    ["Dimensionerende ståltemperatur", f"{temperature} °C"],
    ["Beregnet profilforhold Ap/V", f"{apv} m²/m³"],
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

    result = Paragraph(
        f"<b>Resultat:    Profil skal inddækkes med "
        f"{int(thickness)} mm "
        f"Knauf Fireboard</b>",
        styles['Heading2']
    )

    elements.append(result)

    elements.append(
        Spacer(1, 20)
    )

    note = Paragraph(
        "Monteres i.h.t. Knauf montagevejledning, som findes i gældende Knauf Manual i afsnittet Brandbeskyttelse.",
        styles['BodyText']
    )

    elements.append(note)

    doc.build(elements)

    buffer.seek(0)

    return buffer

# -------------------------
# RESULTAT
# -------------------------

st.divider()

st.success(
    f"Beregnet profilforhold Ap/V: {apv}"
)

st.success(
    f"Profil skal inddækkes med "
    f"{int(thickness)} mm "
    f"Knauf Fireboard"
)

pdf = generate_pdf()

st.download_button(
    label="📄 Download PDF rapport",
    data=pdf,
    file_name=(
        f"Knauf_Fireboard_"
        f"{profile}_"
        f"R{fire_time}.pdf"
    ),
    mime="application/pdf"
)
