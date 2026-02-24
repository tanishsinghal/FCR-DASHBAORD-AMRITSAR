import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG (ONLY ONCE)
# ==============================
st.set_page_config(
    page_title="Bhunaksha (Tatima) Dashboard",
    layout="wide"
)

st.title("🗺️ Bhunaksha (Tatima Incorporation) Dashboard")
st.caption("Tatima Incorporation Progress & Status")
st.markdown("---")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data(ttl=300)
def load_bhunaksha_data():
    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    GID = "741935264"  # Bhunaksha_Data

    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)

    # Clean headers
    df.columns = df.columns.str.strip()

    # Date
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Numeric columns (EXACT from sheet)
    numeric_cols = [
        "No. of Villages of which Shapefiles available with Districts",
        "Total no. of villages where tatima incorporation work has been initiated",
        "Total no. of Tatima to be incorporated",
        "Total no. of Tatimas incorporated",
        "Tatima incorporation Pending at Patwari level",
        "No. of villages where Tatima work has been completed",
        "No. of villages where Tatima Incorporation work initiated (uploaded by ASMs)"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_bhunaksha_data()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header(" Filters")

date_range = st.sidebar.date_input(
    "Date Range",
    (df["Date"].min().date(), df["Date"].max().date())
)

tehsils = st.sidebar.multiselect(
    "Tehsil / Sub-Tehsil",
    sorted(df["Name of Tehsil/Sub Tehsil"].unique())
)

filtered_df = df.copy()

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
    ]

if tehsils:
    filtered_df = filtered_df[
        filtered_df["Name of Tehsil/Sub Tehsil"].isin(tehsils)
    ]

# ==============================
# KPI SUMMARY (MEANINGFUL)
# ==============================
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "🗂️ Villages with Shapefiles",
    int(filtered_df["No. of Villages of which Shapefiles available with Districts"].sum())
)

c2.metric(
    "🚀 Tatima Initiated (Villages)",
    int(filtered_df["Total no. of villages where tatima incorporation work has been initiated"].sum())
)

c3.metric(
    "📌 Tatima Incorporated",
    int(filtered_df["Total no. of Tatimas incorporated"].sum())
)

c4.metric(
    "⏳ Pending at Patwari",
    int(filtered_df["Tatima incorporation Pending at Patwari level"].sum())
)

c5.metric(
    "✅ Villages Completed",
    int(filtered_df["No. of villages where Tatima work has been completed"].sum())
)

st.markdown("---")

# ==============================
# TREND OVER TIME
# ==============================
st.subheader(" Tatima Progress Over Time")

trend = (
    filtered_df
    .groupby("Date")[[
        "Total no. of Tatimas incorporated",
        "Tatima incorporation Pending at Patwari level"
    ]]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    trend,
    x="Date",
    y=[
        "Total no. of Tatimas incorporated",
        "Tatima incorporation Pending at Patwari level"
    ],
    markers=True
)

st.plotly_chart(fig_trend, use_container_width=True)

# ==============================
# TEHSIL-WISE STATUS
# ==============================
st.subheader(" Tehsil-wise Tatima Status")

bar = (
    filtered_df
    .groupby("Name of Tehsil/Sub Tehsil")[[
        "Total no. of Tatimas incorporated",
        "Tatima incorporation Pending at Patwari level"
    ]]
    .sum()
    .reset_index()
)

fig_bar = px.bar(
    bar,
    x="Name of Tehsil/Sub Tehsil",
    y=[
        "Total no. of Tatimas incorporated",
        "Tatima incorporation Pending at Patwari level"
    ],
    barmode="group"
)

st.plotly_chart(fig_bar, use_container_width=True)

# ==============================
# DATA TABLE
# ==============================
st.subheader("📋 Bhunaksha Detailed Data")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.caption("Bhunaksha (Tatima) Monitoring | FCR Dashboard")