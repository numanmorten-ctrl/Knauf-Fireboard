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

    if st.button("🔄 Start ny beregning", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# -------------------------
# LOAD DATA
# -------------------------

apv_df = pd.read_csv("data/apv.csv")
apv_df["profile_type"] = apv_df["profile"].str.extract(r"([A-Z]+)")

# -------------------------
# KATEGORI MAPPING
# -------------------------

category_map = {
    "H-profiler": ["HEA", "HEB", "HEM"],
    "I-profiler": ["IPE", "INP"],
    "U-profiler": ["UNP"],
}

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

    df["temperature"] = df["temperature"].astype(int)

    df.set_index("temperature", inplace=True)

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
    df.columns = df.columns.astype(int)

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

for key in ["category", "montage", "sides"]:
    if key not in st.session_state:
        st.session_state[key] = None

# -------------------------
# CARD COMPONENT
# -------------------------

def card(label, image, state_key):

    selected = st.session_state[state_key] == label

    border = "3px solid #00c853" if selected else "1px solid #444"
    background = "#111827" if selected else "#0b1220"

    html = f"""
    <div style="
        border:{border};
        background-color:{background};
        border-radius:16px;
        padding:20px;
        text-align:center;
        min-height:220px;
        display:flex;
        flex-direction:column;
        justify-content:center;
    ">

        <img src="{image}" style="
            width:100%;
            max-width:160px;
            margin:auto;
            margin-bottom:20px;
        ">

        <div style="
            font-size:28px;
            font-weight:700;
        ">
            {label}
        </div>

    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    if st.button(
        f"Vælg {label}",
        key=f"{state_key}_{label}",
        use_container_width=True
    ):
        st.session_state[state_key] = label
        st.rerun()

# -------------------------
# KATEGORI
# -------------------------

st.subheader("Vælg profilkategori")

col1, col2, col3 = st.columns(3)

with col1:
    card("H-profiler", "images/h_profiles.png", "category")

with col2:
    card("I-profiler", "images/i_profiles.png", "category")

with col3:
    card("U-profiler", "images/u_profiles.png", "category")

category = st.session_state.category

if not category:
    st.stop()

# -------------------------
# PROFIL
# -------------------------

st.divider()

allowed_types = category_map.get(category, [])

profile_types = sorted(
    apv_df[
        apv_df["profile_type"].isin(allowed_types)
    ]["profile_type"].unique()
)

profile_type = st.selectbox(
    "Vælg profiltype",
    profile_types
)

filtered_profiles = apv_df[
    (apv_df["profile_type"] == profile_type) &
    (apv_df["profile"].str.contains(r"\d"))
]["profile"].unique()

def sort_profiles(profiles):

    def extract_number(x):
        num = ''.join(filter(str.isdigit, str(x)))
        return int(num) if num else 0

    return sorted(profiles, key=extract_number)

profile = st.selectbox(
    "Vælg profilstørrelse",
    sort_profiles(filtered_profiles)
)

# -------------------------
# MONTAGE
# -------------------------

st.divider()

st.subheader("Vælg inddækningstype")

col1, col2 = st.columns(2)

with col1:
    card("Klammeløsning", "images/klamme.png", "montage")

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

st.subheader("Vælg antal sider med inddækning")

col1, col2, col3, col4 = st.columns(4)

with col1:
    card("1", "images/side1.png", "sides")

with col2:
    card("2", "images/side2.png", "sides")

with col3:
    card("3", "images/side3.png", "sides")

with col4:
    card("4", "images/side4.png", "sides")

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

st.caption("Gyldigt interval: 350–750 °C")

temperature = int(temperature)

# -------------------------
# FIND AP/V
# -------------------------

row = apv_df[
    (apv_df["profile"] == profile) &
    (apv_df["montage"] == montage) &
    (apv_df["sides"] == sides)
]

if row.empty:
    st.error(
        "Denne kombination er ikke mulig for det valgte profil"
    )
    st.stop()

apv = int(row.iloc[0]["apv"])

# -------------------------
# FIND TYKKELSE
# -------------------------

table = fire_tables[fire_time]

if temperature not in table.index:
    st.error("Temperaturen findes ikke i databasen")
    st.stop()

if apv not in table.columns:
    st.error(
        "Der findes ingen Fireboard løsning for denne kombination"
    )
    st.stop()

thickness = table.loc[temperature, apv]

if pd.isna(thickness):
    st.error("Denne kombination er ikke mulig")
    st.stop()

# -------------------------
# RESULTAT
# -------------------------

st.divider()

st.success(f"AP/V: {apv}")

st.success(
    f"Profil skal inddækkes med "
    f"{int(thickness)} mm Knauf Fireboard"
)
