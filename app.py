import streamlit as st
import pandas as pd

st.title("Brandbeskyttelse af stålkonstruktioner")

# -------------------------
# LOAD DATA
# -------------------------

apv_df = pd.read_csv("data/apv.csv")

# Split profiltype (HEA, HEB osv.)
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
# INPUT
# -------------------------

st.subheader("Vælg profilkategori")

col1, col2 = st.columns(2)

with col1:
    if st.button("I-profiler"):
        st.session_state.category = "I-profiler"

with col2:
    if st.button("U-profiler"):
        st.session_state.category = "U-profiler"

category = st.session_state.get("category")

# 🔹 Profiltype (kun hvis kategori valgt)
if category:
    allowed_types = category_map.get(category, [])

    profile_types = sorted(
        apv_df[apv_df["profile_type"].isin(allowed_types)]["profile_type"].unique()
    )

    profile_type = st.selectbox("Profiltype", profile_types)

    # 🔹 Filtrer profiler
    filtered_profiles = apv_df[
        (apv_df["profile_type"] == profile_type) &
        (apv_df["profile"].str.contains(r"\d"))
    ]["profile"].unique()

    # 🔹 Sortér korrekt
    def sort_profiles(profiles):
        def extract_number(x):
            num = ''.join(filter(str.isdigit, str(x)))
            return int(num) if num != "" else 0
        
        return sorted(profiles, key=extract_number)

    profile = st.selectbox("Profil", sort_profiles(filtered_profiles))

else:
    st.info("Vælg en profilkategori")
    st.stop()

# 🔹 Resten som før
montage = st.selectbox(
    "Montagetype",
    ["Klammeløsning", "Bjælkeprofil eller PDP profil"]
)

sides = st.selectbox("Antal sider", [1, 2, 3, 4])
fire_time = st.selectbox("Brandtid (min)", [30, 60, 90, 120])

temperature = st.number_input("Temperatur (°C)", value=450, step=1)

# -------------------------
# VALIDERING
# -------------------------

if temperature < 350 or temperature > 750:
    st.error("Temperaturen skal være mellem 350 og 750 °C")
    st.stop()

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
    st.error("Kombination findes ikke")
    st.stop()

apv = int(row.iloc[0]["apv"])

# -------------------------
# FIND TYKKELSE
# -------------------------

table = fire_tables[fire_time]

try:
    thickness = table.loc[temperature, apv]

    st.success(f"AP/V: {apv}")
    st.success(f"Fireboard tykkelse: {thickness} mm")

except KeyError:
    st.error("Opslag fejlede")
    st.write("Debug info:")
    st.write("Temperatur:", temperature)
    st.write("APV:", apv)
    st.write("Tilgængelige temperaturer:", list(table.index)[:10])
    st.write("Tilgængelige APV:", list(table.columns)[:10])
