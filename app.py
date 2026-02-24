import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components


# ==============================
# CONFIG
# ==============================
@st.cache_data(ttl=300)
def load_bhunaksha_summary():
    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    GID = "741935264"  # Bhunaksha_Data

    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)

    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    return {
        "shapefiles": int(df["No. of Villages of which Shapefiles available with Districts"].sum()),
        "initiated": int(df["Total no. of villages where tatima incorporation work has been initiated"].sum()),
        "incorporated": int(df["Total no. of Tatimas incorporated"].sum()),
        "pending": int(df["Tatima incorporation Pending at Patwari level"].sum()),
        "completed": int(df["No. of villages where Tatima work has been completed"].sum()),
    }

@st.cache_data(ttl=300)
def load_plant_crop_summary():
    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    GID = "874965086"  # Plant_Crop_Rabi_2025_26

    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)

    df.columns = df.columns.str.strip()

    rename_map = {
        "Total no. of villages": "Total_Villages",
        "Total number of uploaded plots": "Uploaded_Plots",
        "Number of completed Plots till date": "Completed_Plots",
        "Pending for survey": "Pending_Survey",
        "Performance in %": "Performance"
    }

    df = df.rename(columns=rename_map)

    numeric_cols = [
        "Total_Villages",
        "Uploaded_Plots",
        "Completed_Plots",
        "Pending_Survey",
        "Performance"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


st.set_page_config(
    page_title="FCR Dashboard",
    layout="wide"
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY/edit?usp=sharing"


# ==============================
# LOAD DATA
# ==============================
@st.cache_data(ttl=300)
def load_data():
    SHEET_URL = "https://docs.google.com/spreadsheets/d/135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY/export?format=csv&gid=1781187694"

    df = pd.read_csv(SHEET_URL)

    # Clean header names
    df.columns = df.columns.str.strip()

    # Convert Date properly
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    pendency_cols = [
        "Uncontested",
        "Income Certificate",
        "Copying Service",
        "Inspection Records",
        "Overdue Mortgage",
        "Court Orders",
        "Fardbadars"
    ]

    # Fill blanks with 0
    df[pendency_cols] = df[pendency_cols].fillna(0)

    # Calculate total if not already
    df["Total"] = df[pendency_cols].sum(axis=1)

    # Drop rows that couldn't parse a date
    
    df = df.dropna(subset=["Date"])

    return df


df = load_data()


# ==============================
# SIDEBAR FILTERS
# ==============================

st.sidebar.title("🔍 Filters")

# Date Filter
# Remove invalid dates




st.sidebar.markdown("---")

df = df.dropna(subset=["Date"])

# Ensure datetime
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Re-drop after coercion
df = df.dropna(subset=["Date"])

min_date = df["Date"].min().date()

max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# Sub Division
sub_divisions = st.sidebar.multiselect(
    "Sub Division",
    df["Sub Division"].unique()
)

# Tehsil
tehsils = st.sidebar.multiselect(
    "Tehsil",
    df["Tehsil"].unique()
)

# Officer
officers = st.sidebar.multiselect(
    "Officer",
    df["Officer"].unique()
)

# ==============================
# APPLY FILTERS
# ==============================

filtered_df = df.copy()

# Date
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
    ]

# Sub Division
if sub_divisions:
    filtered_df = filtered_df[
        filtered_df["Sub Division"].isin(sub_divisions)
    ]

# Tehsil
if tehsils:
    filtered_df = filtered_df[
        filtered_df["Tehsil"].isin(tehsils)
    ]

# Officer
if officers:
    filtered_df = filtered_df[
        filtered_df["Officer"].isin(officers)
    ]


# ==============================
# HEADER
# ==============================

st.title("📊 FCR Daily Dashboard")

st.markdown("---")


# ==============================
# KPI SECTION
# ==============================

col1, col2, col3 = st.columns(3)

total_pendency = int(filtered_df["Total"].sum())
sub_count = filtered_df["Sub Division"].nunique()
record_count = len(filtered_df)

col1.metric("Total Pendency", total_pendency)
col2.metric("Sub Divisions", sub_count)
col3.metric("Records", record_count)


st.markdown("---")



# ==============================
# PENDENCY BREAKDOWN BY TYPE
# ==============================

st.subheader("📋 Pendency Breakdown by Type")

total_all = filtered_df["Total"].sum()

pendency_summary = {
    "Uncontested": filtered_df["Uncontested"].sum(),
    "Income Certificate": filtered_df["Income Certificate"].sum(),
    "Copying Service": filtered_df["Copying Service"].sum(),
    "Overdue Mortgage": filtered_df["Overdue Mortgage"].sum(),
    "Fardbadars": filtered_df["Fardbadars"].sum(),
    "Inspection Records": filtered_df["Inspection Records"].sum(),
    "Court Orders": filtered_df["Court Orders"].sum(),
}

cols = st.columns(4)

i = 0

for k, v in pendency_summary.items():

    percent = (v / total_all * 100) if total_all > 0 else 0

    # Color logic
    if percent > 50:
        color = "#7edfdd"   # Red
    elif percent > 20:
        color = "#c1e3b6"   # Orange
    else:
        color = "#cba9e3"   # Yellow

    with cols[i % 4]:
        st.markdown(
            f"""
            <div style="
                background-color:{color};
                padding:15px;
                border-radius:10px;
                text-align:center;
                box-shadow:0 2px 5px rgba(0,0,0,0.1);
            ">
                <h4>{k}</h4>
                <h2>{int(v)}</h2>
                <p>{percent:.1f}%</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    i += 1


############################################################################################################################
# ==============================
# MUTATION SUMMARY (MAIN PAGE)
# ==============================
st.markdown("---")

st.markdown("##  Mutation Summary")

@st.cache_data(ttl=300)
def load_mutation_summary():
    url = "https://docs.google.com/spreadsheets/d/135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY/export?format=csv&gid=2073381520"
    df = pd.read_csv(url)

    # FIX COLUMN NAMES AUTOMATICALLY
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df

m_df = load_mutation_summary()

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Patwari >30 Days",
    int(m_df["pendency_at_patwari_level_beyond_30_days"].sum())
)

m2.metric(
    "Kanungo >30 Days",
    int(m_df["pendency_at_kanungo_level_beyond_30_days"].sum())
)

m3.metric(
    "CRO >30 Days",
    int(m_df["pendency_at_cro_level_beyond_30_days"].sum())
)

m4.metric(
    "Total Mutations >30 Days",
    int(m_df["grand_total_of_mutation_pendency_beyond_30_days"].sum())
)
st.markdown("---")
# ==============================
# MUSAVI SUMMARY (MAIN PAGE)
# ==============================
st.subheader(" Musavi Summary")

@st.cache_data(ttl=300)
def load_musavi_summary():
    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    GID = "1163442311"  # Musavi_Validation_Status

    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)

    df.columns = df.columns.str.strip()

    numeric_cols = [
        "Total Villages",
        "Maps Received",
        "Maps Validated",
        "Pending at Patwari",
        "Pending at CRO",
        "Pending at RPSC"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


musavi_df = load_musavi_summary()

total_villages = int(musavi_df["Total Villages"].sum())
maps_received = int(musavi_df["Maps Received"].sum())
maps_validated = int(musavi_df["Maps Validated"].sum())
pending_total = int(
    musavi_df["Pending at Patwari"].sum() +
    musavi_df["Pending at CRO"].sum() +
    musavi_df["Pending at RPSC"].sum()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Villages", total_villages)
c2.metric("Maps Received", maps_received)
c3.metric("Maps Validated", maps_validated)
c4.metric("Total Pending", pending_total)
st.markdown("---")
# ==============================
# Plant Crop Summary (MAIN PAGE)
# ==============================

plant_df = load_plant_crop_summary()

st.subheader(" Plant Crop Summary (Rabi 2025–26)")

p1, p2, p3, p4, p5 = st.columns(5)

p1.metric(
    "Villages",
    int(plant_df["Total_Villages"].sum())
)

p2.metric(
    " Uploaded Plots",
    int(plant_df["Uploaded_Plots"].sum())
)

p3.metric(
    " Completed Plots",
    int(plant_df["Completed_Plots"].sum())
)

p4.metric(
    " Pending Survey",
    int(plant_df["Pending_Survey"].sum())
)

p5.metric(
    " Avg Performance",
    f"{plant_df['Performance'].mean():.2f}%"
)

st.markdown("---")
# ==============================
# BHUNAKSHA SUMMARY (MAIN PAGE)
# ==============================


st.subheader("🗺️ Bhunaksha (Tatima) Summary")

bhunaksha = load_bhunaksha_summary()

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("🗂️ Shapefiles Villages", bhunaksha["shapefiles"])
c2.metric("🚀 Villages Initiated", bhunaksha["initiated"])
c3.metric("📌 Tatima Incorporated", bhunaksha["incorporated"])
c4.metric("⏳ Pending (Patwari)", bhunaksha["pending"])
c5.metric("✅ Villages Completed", bhunaksha["completed"])
st.markdown("---")

# ==============================
# TOP 3 SUB DIVISIONS + CRITICAL ISSUES
# ==============================

st.subheader(" Top 3 Sub Divisions by Pendency")

col_left, col_right = st.columns([2, 1])


# ---- LEFT: TOP 3 SUB DIVISIONS ----

with col_left:

    sub_summary = (
        filtered_df
        .groupby("Sub Division")["Total"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .reset_index()
    )

    total_sum = filtered_df["Total"].sum()

    for _, row in sub_summary.iterrows():

        name = row["Sub Division"]
        value = row["Total"]

        percent = (value / total_sum * 100) if total_sum > 0 else 0

        st.markdown(f"### {name}")
        st.write(f"**{int(value)}** ({percent:.1f}% of total)")

        st.progress(min(percent / 100, 1.0))

        st.markdown("")


# ---- RIGHT: CRITICAL ISSUES ----

with col_right:

    st.subheader("Critical Issues")

    # Top pending type
    top_issue = max(
        pendency_summary,
        key=pendency_summary.get
    )

    top_issue_value = pendency_summary[top_issue]

    # Highest sub division
    highest_sub = sub_summary.iloc[0]["Sub Division"]
    highest_value = sub_summary.iloc[0]["Total"]

    st.markdown("### Top Issue:")
    st.write(top_issue)

    st.markdown(f"## {int(top_issue_value)}")

    st.caption(f"{(top_issue_value/total_all*100):.1f}% of total")

    st.markdown("---")

    st.markdown("### Highest Alert:")
    st.write(highest_sub)

    st.markdown(f"## {int(highest_value)}")


st.markdown("---")


# ==============================
# TOP 5 OFFICERS WITH TRENDS
# ==============================

st.subheader(" Top 5 Officers by Pendency")

officer_summary = (
    filtered_df
    .groupby(["Officer", "Sub Division"])["Total"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

total_sum = filtered_df["Total"].sum()

for _, row in officer_summary.iterrows():

    officer = row["Officer"]
    sub_div = row["Sub Division"]
    total_val = row["Total"]

    percent = (total_val / total_sum * 100) if total_sum > 0 else 0

    left, right = st.columns([2, 1])


    # ---- LEFT: INFO ----
    with left:

        st.markdown(
            f"### {sub_div} - {officer}"
        )

        st.write(
            f"**{int(total_val)}** ({percent:.1f}% of total)"
        )


    # ---- RIGHT: MINI TREND ----
    with right:

        trend_data = (
            filtered_df[
                filtered_df["Officer"] == officer
            ]
            .groupby("Date")["Total"]
            .sum()
            .reset_index()
        )

        fig = px.line(
            trend_data,
            x="Date",
            y="Total",
            height=180
        )

        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)


    st.markdown("---")


# ==============================
# TREND CHART
# ==============================

st.subheader(" Trend Overview")

trend = (
    filtered_df
    .groupby("Date")["Total"]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    trend,
    x="Date",
    y="Total",
    title="District Trend"
)

st.plotly_chart(fig_trend, use_container_width=True)


# ==============================
# BAR CHART
# ==============================

st.subheader(" Pendency by Sub Division")

bar = (
    filtered_df
    .groupby("Sub Division")["Total"]
    .sum()
    .reset_index()
    .sort_values("Total", ascending=False)
)

fig_bar = px.bar(
    bar,
    x="Sub Division",
    y="Total",
    color="Total"
)

st.plotly_chart(fig_bar, use_container_width=True)


# ==============================
# HEATMAP
# ==============================

st.subheader(" Heatmap: Pendency Types")

pendency_cols = [
    "Uncontested",
    "Income Certificate",
    "Copying Service",
    "Inspection Records",
    "Overdue Mortgage",
    "Court Orders",
    "Fardbadars"
]

heatmap_data = filtered_df.groupby("Sub Division")[pendency_cols].sum()

fig_heat = px.imshow(
    heatmap_data.T,
    labels=dict(x="Sub Division", y="Type", color="Count"),
    aspect="auto"
)

st.plotly_chart(fig_heat, use_container_width=True)


# ==============================
# TOP OFFICERS
# ==============================

st.subheader(" Top 5 Officers")

top_officers = (
    filtered_df
    .groupby("Officer")["Total"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

st.table(top_officers)


# ==============================
# ALERT SYSTEM
# ==============================

st.subheader(" Alerts")

THRESHOLD = st.slider(
    "Alert Threshold",
    10, 200, 50
)

alerts = filtered_df[filtered_df["Total"] > THRESHOLD]

if alerts.empty:
    st.success("No Critical Alerts 🎉")
else:
    st.error(f"{len(alerts)} High Pendency Records")
    st.dataframe(alerts)


# ==============================
# FULL TABLE
# ==============================

st.subheader(" Complete Summary")

st.dataframe(filtered_df)


# ==============================
# FOOTER
# ==============================

st.markdown("---")
st.caption("Developed for FCR Monitoring | ")
st.caption("Tanish Singhal | +91-9888636338 ")
