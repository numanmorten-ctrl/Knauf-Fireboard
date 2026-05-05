import streamlit as st
import pandas as pd

st.title("Brandbeskyttelse af stålkonstruktioner")

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
    df = df.rename(columns={df.columns[0]: "temperature"})

    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df = df.dropna(subset=["temperature"])
    df["temperature"] = df["temperature"].astype(int)

    df = df.set_index("temperature")

    df.columns = pd.to_numeric(df.columns, errors="coerce")
    df = df.dropna(axis=1)
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
    border = "3px solid #00c853" if selected else "1px solid #ccc"

    st.markdown(f"""
        <div style="
            border: {border};
            border-radius: 12px;
            padding: 10px;
            text-align: center;
        ">
            <img src="{image}" style="width:100%; max-width:160px;"><br>
            <b>{label}</b>
        </div>
    """, unsafe_allow_html=True)

    if st.button(f"Vælg {label}", key=f"{state_key}_{label}"):
        st.session_state[state_key] = label

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

allowed_types = category_map.get(category, [])

profile_types = sorted(
    apv_df[apv_df["profile_type"].isin(allowed_types)]["profile_type"].unique()
)

profile_type = st.selectbox("Profiltype", profile_types)

filtered_profiles = apv_df[
    (apv_df["profile_type"] == profile_type) &
    (apv_df["profile"].str.contains(r"\d"))
]["profile"].unique()

def sort_profiles(profiles):
    def extract_number(x):
        num = ''.join(filter(str.isdigit, str(x)))
        return int(num) if num else 0
    return sorted(profiles, key=extract_number)

profile = st.selectbox("Profil", sort_profiles(filtered_profiles))

# -------------------------
# MONTAGE
# -------------------------

st.subheader("Vælg montage")

col1, col2 = st.columns(2)

with col1:
    card("Klammeløsning", "images/klamme.png", "montage")

with col2:
    card("Bjælkeprofil eller PDP profil", "images/bjaelke.png", "montage")

montage = st.session_state.montage

if not montage:
    st.stop()

# -------------------------
# SIDES
# -------------------------

st.subheader("Antal sider")

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
# ØVRIGE INPUT
# -------------------------

fire_time = st.selectbox("Brandtid (min)", [30, 60, 90, 120])
temperature = st.number_input("Temperatur (°C)", value=450, step=1)

if temperature < 350 or temperature > 750:
    st.error("Temperaturen skal være mellem 350 og 750 °C")
    st.stop()

temperature = int(temperature)

# -------------------------
# BEREGNING
# -------------------------

row = apv_df[
    (apv_df["profile"] == profile) &
    (apv_df["montage"] == montage) &
    (apv_df["sides"] == sides)
]

if row.empty:
    st.error("Kombination findes ikke")
    st.stop()

apv = int(row.iloc[0]["apv"])

table = fire_tables[fire_time]

try:
    thickness = table.loc[temperature, apv]

    st.success(f"AP/V: {apv}")
    st.success(f"Fireboard tykkelse: {thickness} mm")

except KeyError:
    st.error("Opslag fejlede")
    st.write("Temperatur:", temperature)
    st.write("APV:", apv)
