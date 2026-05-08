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
st.markdown(
    '<div id="top"></div>',
    unsafe_allow_html=True
)

from datetime import datetime

if "last_updated" not in st.session_state:

    st.session_state.last_updated = datetime.now()

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

        calculation_count = len(
            st.session_state.calculations
        )

        last_updated = (
            st.session_state.last_updated
            .strftime("%d-%m-%Y %H:%M")
        )

        st.markdown(f"""
        <div style="
        padding: 14px 18px;
        border: 1px solid #1f3b2d;
        border-radius: 10px;
        background-color: rgba(20,60,35,0.25);
        margin-top: 10px;
        margin-bottom: 10px;
        ">

        <div style="
        font-size: 18px;
        font-weight: 600;
        color: #7CFC9A;
        margin-bottom: 6px;
        ">
        🟢 Aktivt projekt
        </div>

        <div style="font-size: 15px;">
        📁 {project_text}
        </div>

        <div style="
        font-size: 14px;
        margin-top: 4px;
        ">
        {calculation_count} gemte beregninger
        </div>

        <div style="
        font-size: 13px;
        opacity: 0.7;
        margin-top: 4px;
        ">
        Senest ændret: {last_updated}
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

        # Nulstil kun aktive valg

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

# -------------------------
# LOAD DATA
# -------------------------

apv_df = pd.read_csv(
    "data/apv.csv",
    sep=";"
)

# -------------------------
# AUTO SCROLL TO TOP
# -------------------------

if st.session_state.get(
    "scroll_to_top",
    False
):

    st.components.v1.html(
        """
        <script>

        function scrollToTop() {

            const main = window.parent.document.querySelector(
                '.main'
            );

            if (main) {

                main.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });

            }

            window.parent.scrollTo({
                top: 0,
                behavior: 'smooth'
            });

        }

        // Vent til Streamlit er HELT færdig

        setTimeout(scrollToTop, 800);

        </script>
        """,
        height=0
    )

    st.session_state.scroll_to_top = False
    
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

defaults = {

    "category": None,
    "montage": None,
    "sides": None,

    # Beregninger
    "calculations": [],
    "edit_index": None,

    # Projektoplysninger
    "project_name": "",
    "company": "",
    "prepared_by": "",
    "description": ""
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value
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
# DEFAULT VALUES
# -------------------------

apv_mode = None

perimeter = None

area = None

selected_profile_label = None

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

        col1, col2 = st.columns([1, 2])

        with col1:

            st.markdown("""
            Beregning udføres iht. **EN 13381-4**  
            og **DS/EN 1993-1-2 (Eurocode 3)**.
            """)

            st.caption(
                "Resultat angives i m²/m³"
            )

        with col2:

            st.latex(
                r'''
                A_p/V
                =
                \frac{
                    \mathrm{Indvendig\ omkreds\ [mm]}
                }{
                    \mathrm{Tværsnitsareal\ [mm^2]}
                }
                \times 1000
                '''
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

# Gem i session_state

st.session_state.project_name = project_name
st.session_state.company = company
st.session_state.prepared_by = prepared_by
st.session_state.description = description
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
    f"Beregnet profilforhold Ap/V: "
    f"{apv} m²/m³"
)

st.success(
    f"Profil skal inddækkes med "
    f"{int(thickness)} mm "
    f"Knauf Fireboard"
)

# -------------------------
# GEM BEREGNING
# -------------------------

calculation_data = {

    # -------------------------
    # INPUTS
    # -------------------------

    "category": category,
    "profile": profile,
    "montage": montage,
    "sides": sides,

    "fire_time": fire_time,
    "temperature": temperature,

    "apv": apv,
    "thickness": thickness,

    # -------------------------
    # CUSTOM PROFILE DATA
    # -------------------------

    "apv_mode": (
        apv_mode
        if custom_profile
        else None
    ),

    "perimeter": (
        perimeter
        if custom_profile
        else None
    ),

    "area": (
        area
        if custom_profile
        else None
    ),

    # -------------------------
    # PROFILE SELECTION
    # -------------------------

    "selected_profile_label": (
        selected_profile_label
        if not custom_profile
        else None
    )
}

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

    else:

        st.session_state.calculations.append(
            calculation_data
        )

    st.session_state.last_updated = datetime.now()

    st.rerun()

# -------------------------
# GEMTE BEREGNINGER
# -------------------------

if st.session_state.calculations:

    st.divider()

    st.subheader(
        "Samlede beregninger"
    )

    for idx, calc in enumerate(
        st.session_state.calculations
    ):

        with st.container():

            col1, col2, col3 = st.columns(
                [8, 1, 1]
            )

            with col1:

                st.markdown(f"""
                ### Beregning {idx + 1}

                **Profil:** {calc['profile']}  
                **Brandtid:** {calc['fire_time']} min  
                **Temperatur:** {calc['temperature']} °C  
                **Ap/V:** {calc['apv']} m²/m³  
                **Fireboard:** {int(calc['thickness'])} mm
                """)

            # -------------------------
            # EDIT
            # -------------------------

            with col2:

                if st.button(
                    "✏️",
                    key=f"edit_{idx}"
                ):

                    selected_calc = (
                        st.session_state.calculations[idx]
                    )

                    # -------------------------
                    # LOAD VALUES BACK
                    # -------------------------

                    st.session_state.category = (
                        selected_calc["category"]
                    )

                    st.session_state.montage = (
                        selected_calc["montage"]
                    )

                    st.session_state.sides = (
                        selected_calc["sides"]
                    )

                    st.session_state.fire_time = (
                        selected_calc["fire_time"]
                    )

                    st.session_state.temperature = (
                        selected_calc["temperature"]
                    )

                    st.session_state.profile = (
                        selected_calc["profile"]
                    )

                    st.session_state.selected_profile_label = (
                        selected_calc.get(
                            "selected_profile_label"
                        )
                    )

                    st.session_state.apv_mode = (
                        selected_calc.get(
                            "apv_mode"
                        )
                    )

                    st.session_state.perimeter = (
                        selected_calc.get(
                            "perimeter"
                        )
                    )

                    st.session_state.area = (
                        selected_calc.get(
                            "area"
                        )
                    )

                    st.session_state.edit_index = idx

                    st.session_state.scroll_to_top = True

                    st.rerun()

            # -------------------------
            # DELETE
            # -------------------------

            with col3:

                if st.button(
                    "🗑️",
                    key=f"delete_{idx}"
                ):

                    st.session_state.calculations.pop(
                        idx
                    )

                    st.session_state.last_updated = (
                        datetime.now()
                    )

                    st.rerun()

            st.divider()

    # -------------------------
    # HANDLINGER NEDERST
    # -------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🔄 Ny beregning",
            key="bottom_new_calc",
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

    with col2:

        if st.button(
            "🗑️ Nyt projekt",
            key="bottom_new_project",
            use_container_width=True
        ):

            st.session_state.clear()

            st.rerun()
