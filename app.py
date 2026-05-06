import base64
import streamlit as st
import pandas as pd

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(
    page_title="Brandbeskyttelse af stålkonstruktioner",
    layout="wide"
)

# -------------------------
# CUSTOM WIDTH
# -------------------------

st.markdown("""
<style>

.block-container {
    max-width: 1300px;
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    margin: auto;
}

/* KNAP UNDER CARD */

div.stButton > button {
    width: 100%;
    height: 0px;
    padding: 0;
    margin-top: -260px;
    margin-bottom: 260px;

    background: transparent;
    border: none;

    color: transparent;
    font-size: 0;
}

/* HOVER */

div.stButton > button:hover {
    border: none;
    background: transparent;
}

/* FJERN FOCUS */

div.stButton > button:focus {
    outline: none;
    box-shadow: none;
}

</style>
""", unsafe_allow_html=True)
# -------------------------
# HEADER + RESET BUTTON
# -------------------------

col1, col2 = st.columns([8, 2])

with col1:
    st.title("Brandbeskyttelse af stålkonstruktioner")

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

    df = pd.read_csv(path, sep=";")

    df = df.dropna(how="all")

    df.rename(
        columns={df.columns[0]: "temperature"},
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

    df = df.dropna(subset=["temperature"])

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

    df = df.loc[:, df.columns.notna()]

    df.columns = (
        df.columns.astype(int)
    )

    return df

fire_tables = {
    30: load_fireboard("data/fireboard_30.csv"),
    60: load_fireboard("data/fireboard_60.csv"),
    90: load_fireboard("data/fireboard_90.csv"),
    120: load_fireboard("data/fireboard_120.csv"),
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
# CARD COMPONENT
# -------------------------

def card(label, image_path, state_key):

    selected = (
        st.session_state[state_key] == label
    )

    border_color = (
        "#00c853"
        if selected
        else "#31333F"
    )

    with st.container(border=True):

        st.markdown(
            f"""
            <style>
            .card-image {{
                display:flex;
                justify-content:center;
                margin-top:10px;
                margin-bottom:20px;
            }}

            .card-title {{
                text-align:center;
                font-size:28px;
                font-weight:700;
                margin-bottom:10px;
            }}

            div[data-testid="stVerticalBlock"] > div:has(.selected-{label}) {{
                border:3px solid {border_color};
                border-radius:16px;
                background-color:#0b1220;
                padding:10px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="selected-{label}"></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="card-image">',
            unsafe_allow_html=True
        )

        st.image(
            image_path,
            width=160
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="card-title">
                {label}
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            f"Vælg {label}",
            key=f"{state_key}_{label}",
            use_container_width=True
        ):
            st.session_state[state_key] = label
            st.rerun()

# -------------------------
# PROFILKATEGORI
# -------------------------

st.subheader("Vælg profilkategori")

col1, col2, col3 = st.columns(3)

with col1:
    card(
        "H-profiler",
        "images/h_profiles.png",
        "category"
    )

with col2:
    card(
        "I-profiler",
        "images/i_profiles.png",
        "category"
    )

with col3:
    card(
        "U-profiler",
        "images/u_profiles.png",
        "category"
    )

col4, col5, col6 = st.columns(3)

with col4:
    card(
        "Kvadratiske rør varmvalsede",
        "images/shs_hot.png",
        "category"
    )

with col5:
    card(
        "Kvadratiske rør koldvalsede",
        "images/shs_cold.png",
        "category"
    )

with col6:
    card(
        "Rektangulære rør varmvalsede",
        "images/rhs_hot.png",
        "category"
    )

col7, col8, col9 = st.columns(3)

with col7:
    card(
        "Rektangulære rør koldvalsede",
        "images/rhs_cold.png",
        "category"
    )

with col8:
    card(
        "Cirkulære rør middelsvære",
        "images/chs_medium.png",
        "category"
    )

with col9:
    card(
        "Cirkulære rør svære",
        "images/chs_heavy.png",
        "category"
    )

category = st.session_state.category

if not category:
    st.stop()

# -------------------------
# PROFILER
# -------------------------

st.divider()

filtered_df = apv_df[
    apv_df["profile_category"] == category
]

profiles = filtered_df["profile"].unique()

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

def format_profile(profile, category):

    profile = str(profile)

    # Kvadratiske + rektangulære rør
    if (
        "Kvadratiske" in category
        or
        "Rektangulære" in category
    ):

        return f"{profile} mm"

    # Cirkulære rør
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
    format_profile(p, category): p
    for p in sort_profiles(profiles)
}

selected_profile_label = st.selectbox(
    "Vælg profilstørrelse",
    list(formatted_profiles.keys())
)

profile = formatted_profiles[selected_profile_label]

# -------------------------
# MONTAGE
# -------------------------

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

col1, col2, col3, col4 = st.columns(4)

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

row = apv_df[
    (
        apv_df["profile"] == profile
    )
    &
    (
        apv_df["montage"] == montage
    )
    &
    (
        apv_df["sides"] == sides
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

if temperature not in table.index:

    st.error(
        "Temperaturen findes ikke i databasen"
    )

    st.stop()

if apv not in table.columns:

    st.error(
        "Der findes ingen Fireboard løsning "
        "for denne kombination"
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
