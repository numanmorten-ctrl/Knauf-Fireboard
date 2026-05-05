import streamlit as st
import pandas as pd

st.title("Brandbeskyttelse af stålkonstruktioner")

# -------------------------
# LOAD DATA
# -------------------------

apv_df = pd.read_csv("data/apv.csv")

fire_tables = {
    30: pd.read_csv("data/fireboard_30.csv", index_col=0),
    60: pd.read_csv("data/fireboard_60.csv", index_col=0),
    90: pd.read_csv("data/fireboard_90.csv", index_col=0),
    120: pd.read_csv("data/fireboard_120.csv", index_col=0),
}

# -------------------------
# INPUT
# -------------------------

profiles = sorted(apv_df["profile"].unique())
profile = st.selectbox("Profil", profiles)

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
    thickness = table.loc[temperature, str(apv)]

    st.success(f"AP/V: {apv}")
    st.success(f"Fireboard tykkelse: {thickness} mm")

except:
    st.error("Opslag fejlede")
