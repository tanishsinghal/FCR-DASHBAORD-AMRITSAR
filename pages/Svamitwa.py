import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Svamitwa Dashboard", layout="wide")

st.title("🗺️ Svamitwa Monitoring Dashboard")
st.markdown("---")

# ==============================
# LOAD DATA (UPDATED)
# ==============================
@st.cache_data(ttl=300)
def load_svamitwa_data():
    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    GID = "1518724049"   # YOUR_SVAMITWA_GID

    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)

    # Clean headers (NO aggressive replace)
    df.columns = df.columns.str.strip()

    # Standardize Tehsil column
    if "Name of Tehsil" in df.columns:
        df = df.rename(columns={"Name of Tehsil": "Tehsil"})

    # Remove total row
    if "Tehsil" in df.columns:
        df = df[df["Tehsil"].str.lower() != "total"]

    # Date
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Convert numeric columns safely
    for col in df.columns:
        if col not in ["Date", "Tehsil", "Name of Tehsil sub parts"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_svamitwa_data()

if df.empty:
    st.error("No data loaded. Check Google Sheet.")
    st.stop()


# ==============================
# SIDEBAR FILTERS (GLOBAL STYLE)
# ==============================
st.sidebar.header("🔎 Filters")

# Tehsil filter
tehsil_list = sorted(df["Tehsil"].dropna().unique())

selected_tehsil = st.sidebar.multiselect(
    "Select Tehsil",
    tehsil_list,
    default=tehsil_list
)

# Date filter
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    (min_date, max_date)
)

# Apply filter
filtered_df = df.copy()

if selected_tehsil:
    filtered_df = filtered_df[filtered_df["Tehsil"].isin(selected_tehsil)]

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
    ]


# ==============================
# KPI SUMMARY (MEANINGFUL)
# ==============================
st.subheader("📊 Key Performance Summary")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Total Villages Under Scheme",
    int(filtered_df["Total No. of Villages under Scheme"].sum())
)

k2.metric(
    "Villages Received",
    int(filtered_df["Total No. of Villages Received by Dist. from SoI"].sum())
)

k3.metric(
    "Ground Truth Completed",
    int(filtered_df["Villages where ground truthing completed & sent back to SoI"].sum())
)

k4.metric(
    "Map-1 Ground Truthing",
    int(filtered_df["Map-1 Ground Truthing"].sum())
)

st.markdown("---")

# ==============================
# TEHSIL WISE SUMMARY
# ==============================
st.subheader("📍 Tehsil-wise Performance")

tehsil_summary = (
    filtered_df
    .groupby("Tehsil")
    .sum(numeric_only=True)
    .reset_index()
)

fig_bar = px.bar(
    tehsil_summary,
    x="Tehsil",
    y=[
        "Total No. of Villages under Scheme",
        "Total No. of Villages Received by Dist. from SoI",
        "Villages where ground truthing completed & sent back to SoI"
    ],
    barmode="group"
)

st.plotly_chart(fig_bar, use_container_width=True)


# ==============================
# 📈 DAILY TREND
# ==============================
st.subheader("📈 Daily Trend")

trend = (
    filtered_df
    .groupby("Date")
    .sum(numeric_only=True)
    .reset_index()
)

fig_line = px.line(
    trend,
    x="Date",
    y=[
        "Total No. of Villages Received by Dist. from SoI",
        "Villages where ground truthing completed & sent back to SoI",
        "Map-1 Ground Truthing"
    ],
    markers=True
)

st.plotly_chart(fig_line, use_container_width=True)


# ==============================
# 🏆 TOP / BOTTOM 3
# ==============================
st.subheader("🏆 Top & Bottom Tehsils")

tehsil_summary["Total Activity"] = (
    tehsil_summary["Total No. of Villages Received by Dist. from SoI"] +
    tehsil_summary["Villages where ground truthing completed & sent back to SoI"]
)

top3 = tehsil_summary.sort_values("Total Activity", ascending=False).head(3)
bottom3 = tehsil_summary.sort_values("Total Activity").head(3)

c1, c2 = st.columns(2)

with c1:
    st.write("### 🔥 Top 3 Tehsils")
    st.dataframe(top3, use_container_width=True)

with c2:
    st.write("### ⚠️ Bottom 3 Tehsils")
    st.dataframe(bottom3, use_container_width=True)


# ==============================
# 📋 FULL DATA
# ==============================
st.subheader("📋 Detailed Data")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.caption("Svamitwa Monitoring System")
