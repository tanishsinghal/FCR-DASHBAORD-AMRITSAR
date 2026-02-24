import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG (ONLY ONCE)
# ==============================
st.set_page_config(
    page_title="Musavi Validation Status",
    layout="wide"
)

st.title("🗺️ Musavi (Mauza Map) Validation Dashboard")
st.caption("Daily Musavi validation progress & pendency status")
st.markdown("---")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data(ttl=300)
def load_musavi_data():
    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    GID = "1163442311"  # Musavi_Validation_Status

    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Date handling
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    numeric_cols = [
        "Total Villages",
        "Maps Received",
        "Maps Validated",
        "Pending at Patwari",
        "Pending at CRO",
        "Pending at RPSC",
        "Total CRO Validation Done"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_musavi_data()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("🔍 Filters")

date_range = st.sidebar.date_input(
    "Date Range",
    (df["Date"].min().date(), df["Date"].max().date())
)

tehsils = st.sidebar.multiselect(
    "Tehsil / Sub-Tehsil",
    sorted(df["Tehsil / Sub-Tehsil"].unique())
)

filtered_df = df.copy()

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
    ]

if tehsils:
    filtered_df = filtered_df[
        filtered_df["Tehsil / Sub-Tehsil"].isin(tehsils)
    ]

# ==============================
# TOP SUMMARY KPIs (MEANINGFUL)
# ==============================
total_villages = int(filtered_df["Total Villages"].sum())
maps_received = int(filtered_df["Maps Received"].sum())
maps_validated = int(filtered_df["Maps Validated"].sum())

pending_total = int(
    filtered_df["Pending at Patwari"].sum() +
    filtered_df["Pending at CRO"].sum() +
    filtered_df["Pending at RPSC"].sum()
)

completion_pct = (
    (maps_validated / maps_received) * 100
    if maps_received > 0 else 0
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("🏘️ Total Villages", total_villages)
c2.metric("📥 Maps Received", maps_received)
c3.metric("✅ Maps Validated", maps_validated)
c4.metric("⏳ Total Pending", pending_total)
c5.metric("📊 Completion %", f"{completion_pct:.2f}%")

st.markdown("---")

# ==============================
# PENDENCY BREAKDOWN
# ==============================
st.subheader("📌 Pendency Breakdown")

p1, p2, p3 = st.columns(3)

p1.metric(
    "Patwari Pending",
    int(filtered_df["Pending at Patwari"].sum())
)

p2.metric(
    "CRO Pending",
    int(filtered_df["Pending at CRO"].sum())
)

p3.metric(
    "RPSC Pending",
    int(filtered_df["Pending at RPSC"].sum())
)

st.markdown("---")

# ==============================
# TEHSIL-WISE STATUS
# ==============================
st.subheader("📍 Tehsil-wise Musavi Validation Status")

bar_df = (
    filtered_df
    .groupby("Tehsil / Sub-Tehsil")[
        ["Maps Validated", "Pending at Patwari", "Pending at CRO", "Pending at RPSC"]
    ]
    .sum()
    .reset_index()
)

fig = px.bar(
    bar_df,
    x="Tehsil / Sub-Tehsil",
    y=[
        "Maps Validated",
        "Pending at Patwari",
        "Pending at CRO",
        "Pending at RPSC"
    ],
    barmode="stack",
    labels={"value": "Number of Villages"}
)

st.plotly_chart(fig, use_container_width=True)

# ==============================
# DATA TABLE
# ==============================
st.subheader("📋 Detailed Musavi Validation Data")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.caption("Musavi Validation Status | FCR Dashboard")