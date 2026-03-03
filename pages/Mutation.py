import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG (ONLY ONCE)
# ==============================
st.set_page_config(
    page_title="Mutation Pending Dashboard",
    layout="wide"
)

st.title("📑 Mutation Pending Status")
st.caption("Pendency beyond 15 / 30 days (Level-wise & Tehsil-wise)")
st.markdown("---")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data(ttl=300)
def load_mutation_data():
    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    GID = "2073381520"  # Mutation_Pending_Status

    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Date handling
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Numeric columns (EXACT from sheet)
    numeric_cols = [
        "Pendency at Patwari Level Beyond 15 days",
        "Pendency at Patwari Level Beyond 30 days",
        "Total",
        "Pendency at Kanungo Level Beyond 20 days",
        "Pendency at Kanungo Level Beyond 30 days",
        "Total.1",
        "Pendency at CRO Level Beyond 30 days",
        "Grand Total of Mutation pendency beyond 30 days"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df


df = load_mutation_data()

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
# KPI SUMMARY (MEANINGFUL)
# ==============================
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🧾 Patwari >30 Days",
    filtered_df["Pendency at Patwari Level Beyond 30 days"].sum()
)

c2.metric(
    "🧾 Kanungo >30 Days",
    filtered_df["Pendency at Kanungo Level Beyond 30 days"].sum()
)

c3.metric(
    "🧾 CRO >30 Days",
    filtered_df["Pendency at CRO Level Beyond 30 days"].sum()
)

c4.metric(
    "🚨 Total Mutations >30 Days",
    filtered_df["Grand Total of Mutation pendency beyond 30 days"].sum()
)

st.markdown("---")

# ==============================
# LEVEL-WISE COMPARISON
# ==============================
st.subheader("📊 Level-wise Pendency (>30 Days)")

level_df = pd.DataFrame({
    "Level": ["Patwari", "Kanungo", "CRO"],
    "Pending >30 Days": [
        filtered_df["Pendency at Patwari Level Beyond 30 days"].sum(),
        filtered_df["Pendency at Kanungo Level Beyond 30 days"].sum(),
        filtered_df["Pendency at CRO Level Beyond 30 days"].sum()
    ]
})

fig_level = px.bar(
    level_df,
    x="Level",
    y="Pending >30 Days",
    text="Pending >30 Days",
    color="Level"
)

st.plotly_chart(fig_level, use_container_width=True)

st.markdown("---")

# ==============================
# TEHSIL-WISE BREAKUP
# ==============================
st.subheader("📍 Tehsil-wise Mutation Pendency (>30 Days)")

tehsil_bar = (
    filtered_df
    .groupby("Tehsil")[
        [
            "Pendency at Patwari Level Beyond 30 days",
            "Pendency at Kanungo Level Beyond 30 days",
            "Pendency at CRO Level Beyond 30 days"
        ]
    ]
    .sum()
    .reset_index()
)

fig_tehsil = px.bar(
    tehsil_bar,
    x="Tehsil",
    y=[
        "Pendency at Patwari Level Beyond 30 days",
        "Pendency at Kanungo Level Beyond 30 days",
        "Pendency at CRO Level Beyond 30 days"
    ],
    barmode="stack"
)

st.plotly_chart(fig_tehsil, use_container_width=True)

st.markdown("---")



# ==============================
# TREND ANALYSIS
# ==============================
st.subheader("📈 Trend: Mutation Pendency (>30 Days)")

trend_df = (
    filtered_df
    .groupby("Date")["Grand Total of Mutation pendency beyond 30 days"]
    .sum()
    .reset_index()
)

if trend_df["Date"].nunique() < 2:
    st.info("📌 Trend requires data from multiple dates. Please expand the date range.")
else:
    fig_trend = px.line(
        trend_df,
        x="Date",
        y="Grand Total of Mutation pendency beyond 30 days",
        markers=True
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# ==============================
# DATA TABLE
# ==============================
st.subheader("📋 Detailed Mutation Pending Data")
st.dataframe(filtered_df, use_container_width=True)

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.caption("Mutation Pending Monitoring | FCR Dashboard")

st.caption("Prepared by Tanish Singhal")

