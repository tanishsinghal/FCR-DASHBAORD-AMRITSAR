import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Svamitwa Dashboard",
    layout="wide"
)

st.title("🗺️ Svamitwa Dashboard")
st.markdown("---")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data(ttl=300)
def load_bhunaksha_data():
    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    Svamitwa_GID = "1518724049"

    SHEET_URL = (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
        f"/export?format=csv&gid={Svamitwa_GID}"
    )

    df = pd.read_csv(SHEET_URL)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Parse Date safely
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # 🔴 CRITICAL: remove NaT dates
    df = df.dropna(subset=["Date"])

    # Numeric columns
    num_cols = [
        "Total_Villages_Notified",
        "Map3_Received_From_SoI",
        "Map3_Sent_To_SoI",
    ]

    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df


df = load_bhunaksha_data()

# ==============================
# SAFETY CHECK
# ==============================
if df.empty:
    st.warning("No Bhunaksha data available. Please check Google Sheet.")
    st.stop()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.title("🔍 Filters")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

districts = st.sidebar.multiselect(
    "District",
    sorted(df["District"].dropna().unique())
)

tehsils = st.sidebar.multiselect(
    "Tehsil",
    sorted(df["Tehsil"].dropna().unique())
)

# ==============================
# APPLY FILTERS
# ==============================
filtered_df = df.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(start_date)) &
        (filtered_df["Date"] <= pd.to_datetime(end_date))
    ]

if districts:
    filtered_df = filtered_df[filtered_df["District"].isin(districts)]

if tehsils:
    filtered_df = filtered_df[filtered_df["Tehsil"].isin(tehsils)]

# ==============================
# KPI SECTION
# ==============================
col1, col2, col3 = st.columns(3)

col1.metric(
    "🏘️ Total Villages Notified",
    int(filtered_df["Total_Villages_Notified"].sum())
)

col2.metric(
    "📥 Map3 Received from SoI",
    int(filtered_df["Map3_Received_From_SoI"].sum())
)

col3.metric(
    "📤 Map3 Sent to SoI",
    int(filtered_df["Map3_Sent_To_SoI"].sum())
)

st.markdown("---")

# ==============================
# TREND CHART
# ==============================
st.subheader("📈 Map3 Progress Over Time")

trend = (
    filtered_df
    .groupby("Date")[["Map3_Received_From_SoI", "Map3_Sent_To_SoI"]]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    trend,
    x="Date",
    y=["Map3_Received_From_SoI", "Map3_Sent_To_SoI"],
    markers=True
)

st.plotly_chart(fig_trend, use_container_width=True)

# ==============================
# DISTRICT-WISE BAR CHART
# ==============================
st.subheader("📊 District-wise Map3 Status")

bar = (
    filtered_df
    .groupby("District")[["Map3_Received_From_SoI", "Map3_Sent_To_SoI"]]
    .sum()
    .reset_index()
)

fig_bar = px.bar(
    bar,
    x="District",
    y=["Map3_Received_From_SoI", "Map3_Sent_To_SoI"],
    barmode="group"
)

st.plotly_chart(fig_bar, use_container_width=True)

# ==============================
# DATA TABLE
# ==============================
st.subheader("📋 Detailed Bhunaksha Data")
st.dataframe(filtered_df, use_container_width=True)

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.caption("Bhunaksha Monitoring Dashboard | FCR System")