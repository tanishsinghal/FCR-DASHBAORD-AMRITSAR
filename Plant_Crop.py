import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG (ONLY HERE)
# ==============================
st.set_page_config(
    page_title="Plant Crop Survey – Rabi 2025–26",
    layout="wide"
)

st.title("🌾 Plant Crop Survey Dashboard (Rabi 2025–26)")
st.caption("Daily Progress & Performance Overview")
st.markdown("---")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data(ttl=300)
def load_plant_crop_data():
    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    GID = "874965086"  # Plant_Crop_Rabi_2025_26

    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)

    # Clean headers
    df.columns = df.columns.str.strip()

    # Rename columns to SAFE internal names
    column_map = {
        "Tehsil/Sub Tehsil": "Tehsil",
        "Total no. of villages": "Total_Villages",
        "Total number of uploaded plots": "Uploaded_Plots",
        "Number of completed Plots till date": "Completed_Plots",
        "Pending for survey": "Pending_Survey",
        "Number of Pvt. Surveyors identified": "Surveyors_Identified",
        "Number of villages allocated": "Villages_Allocated",
        "Performance in %": "Performance"
    }

    df = df.rename(columns=column_map)

    # Date handling
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Numeric columns
    numeric_cols = [
        "Total_Villages",
        "Uploaded_Plots",
        "Completed_Plots",
        "Pending_Survey",
        "Surveyors_Identified",
        "Villages_Allocated",
        "Performance"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_plant_crop_data()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("🔍 Filters")

date_range = st.sidebar.date_input(
    "Date Range",
    (df["Date"].min().date(), df["Date"].max().date())
)

tehsils = st.sidebar.multiselect(
    "Tehsil",
    sorted(df["Tehsil"].unique())
)

filtered_df = df.copy()

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
    ]

if tehsils:
    filtered_df = filtered_df[filtered_df["Tehsil"].isin(tehsils)]

# ==============================
# KPI SUMMARY
# ==============================
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("🏘️ Total no. of villages", int(filtered_df["Total_Villages"].sum()))
c2.metric("📐 Uploaded Plots", int(filtered_df["Uploaded_Plots"].sum()))
c3.metric("✅ Completed Plots", int(filtered_df["Completed_Plots"].sum()))
c4.metric("⏳ Pending Survey", int(filtered_df["Pending_Survey"].sum()))

avg_perf = filtered_df["Performance"].mean()
c5.metric("📊 Avg Performance", f"{avg_perf:.2f}%")

st.markdown("---")

# ==============================
# TREND OVER TIME
# ==============================
st.subheader("📈 Completion Trend Over Time")

trend = (
    filtered_df
    .groupby("Date")["Completed_Plots"]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    trend,
    x="Date",
    y="Completed_Plots",
    markers=True
)

st.plotly_chart(fig_trend, use_container_width=True)

# ==============================
# TEHSIL-WISE STATUS
# ==============================
st.subheader("📊 Tehsil-wise Survey Status")

bar = (
    filtered_df
    .groupby("Tehsil")[["Completed_Plots", "Pending_Survey"]]
    .sum()
    .reset_index()
)

fig_bar = px.bar(
    bar,
    x="Tehsil",
    y=["Completed_Plots", "Pending_Survey"],
    barmode="stack"
)

st.plotly_chart(fig_bar, use_container_width=True)

# ==============================
# RESOURCE DEPLOYMENT
# ==============================
st.subheader("👥 Resource Deployment")

resource = (
    filtered_df
    .groupby("Tehsil")[["Surveyors_Identified", "Villages_Allocated"]]
    .sum()
    .reset_index()
)

fig_res = px.bar(
    resource,
    x="Tehsil",
    y=["Surveyors_Identified", "Villages_Allocated"],
    barmode="group"
)

st.plotly_chart(fig_res, use_container_width=True)

# ==============================
# DATA TABLE
# ==============================
st.subheader("📋 Detailed Plant Crop Data")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.caption("Plant Crop Survey | Rabi 2025–26 | FCR Dashboard")