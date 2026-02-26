import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG (ONLY ONCE)
# ==============================
st.set_page_config(
    page_title="Svamitwa Dashboard",
    layout="wide"
)

st.title("🗺️ Svamitwa Monitoring Dashboard")
st.markdown("---")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data(ttl=300)
def load_svamitwa_data():
    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    GID = "1518724049"  # YOUR_SVAMITWA_GID

    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)

    # Clean headers properly
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace(">", "")
        .str.replace("/", "")
    )

    # Remove total row if exists
    if "Name_of_Tehsil" in df.columns:
        df = df[df["Name_of_Tehsil"] != "Total"]

    # Parse Date
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

    # Convert all possible numeric columns
    for col in df.columns:
        if col not in ["Date", "Name_of_Tehsil"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_svamitwa_data()

if df.empty:
    st.warning("No data available. Check Google Sheet.")
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

tehsils = st.sidebar.multiselect(
    "Tehsil",
    sorted(df["Name_of_Tehsil"].unique())
)

# ==============================
# APPLY FILTERS
# ==============================
filtered_df = df.copy()

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
    ]

if tehsils:
    filtered_df = filtered_df[
        filtered_df["Name_of_Tehsil"].isin(tehsils)
    ]

# ==============================
# KPI SUMMARY
# ==============================
st.subheader("📊 Key Performance Summary")

numeric_columns = filtered_df.select_dtypes(include="number").columns

kpi_cols = st.columns(min(4, len(numeric_columns)))

for i, col in enumerate(numeric_columns[:4]):
    with kpi_cols[i]:
        st.metric(
            col.replace("_", " "),
            int(filtered_df[col].sum())
        )

st.markdown("---")

# ==============================
# TEHSIL WISE STATUS
# ==============================
st.subheader("📍 Tehsil-wise Progress")

tehsil_summary = (
    filtered_df
    .groupby("Name_of_Tehsil")[numeric_columns]
    .sum()
    .reset_index()
)

fig_bar = px.bar(
    tehsil_summary,
    x="Name_of_Tehsil",
    y=numeric_columns[:3],
    barmode="group"
)

st.plotly_chart(fig_bar, use_container_width=True)

# ==============================
# DAILY TREND
# ==============================
st.subheader("📈 Daily Trend")

trend = (
    filtered_df
    .groupby("Date")[numeric_columns]
    .sum()
    .reset_index()
)

fig_line = px.line(
    trend,
    x="Date",
    y=numeric_columns[:3],
    markers=True
)

st.plotly_chart(fig_line, use_container_width=True)

# ==============================
# FULL DATA TABLE
# ==============================
st.subheader("📋 Detailed Data")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.caption("Svamitwa Monitoring System | FCR Dashboard")
