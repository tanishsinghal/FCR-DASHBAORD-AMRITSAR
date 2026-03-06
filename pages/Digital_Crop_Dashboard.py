import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG (ONLY ONCE)
# ==============================
st.set_page_config(
    page_title="Digital_Crop_Dashboard",
    layout="wide"
)

st.title("🗺️ Digital_Crop_Dashboard")
st.caption("Daily Digital Crop validation progress & pendency status")
st.markdown("---")


@st.cache_data(ttl=300)
def load_crop_data():

    SPREADSHEET_ID = "135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY"
    GID = "30899428"

    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

    df = pd.read_csv(url)

    df.columns = df.columns.str.strip()

    return df


df = load_crop_data()

# Detect survey columns
survey_cols = [c for c in df.columns if "Plots surveyed" in c]
surveyor_cols = [c for c in df.columns if "Surveyors on field" in c]

if len(survey_cols) == 0:
    st.error("No 'Plots surveyed' columns found in Google Sheet.")
    st.stop()

if len(surveyor_cols) == 0:
    st.error("No 'Surveyors on field' columns found in Google Sheet.")
    st.stop()

latest_survey_col = survey_cols[-1]
latest_surveyor_col = surveyor_cols[-1]

# Create dashboard fields
df["Daily Progress"] = df[latest_survey_col]

df["Surveyors In Field"] = df[latest_surveyor_col]

df["Survey Completion"] = (
    df["Number of completed Plots till date"] /
    df["Total number of uploaded plots"]
) * 100

df["Approval Rate"] = (
    df["Performance  in %"]
    .astype(str)
    .str.replace("%","")
    .astype(float)
)

total_target = df["Total number of uploaded plots"].sum()

completed_plots = df["Number of completed Plots till date"].sum()

pending = df["Pending for survey"].sum()
total_villages = df["Total no. of villages"].sum()

survey_today = df["Daily Progress"].sum()

surveyors = df["Number of Pvt. Surveyors identified"].sum()


# Rename column for easier use
df = df.rename(columns={
    "Tehsil/Sub Tehsil":"Tehsil"
})


df["Total Plots"] = df["Total number of uploaded plots"]

df["Surveyed Plots"] = df["Number of completed Plots till date"]

df["Surveyors"] = df["Number of Pvt. Surveyors identified"]

df["In Field"] = df["Surveyors In Field"]

df["Survey Progress"] = (
    df["Surveyed Plots"] / df["Total Plots"]
) * 100



st.markdown("""
<style>

.stApp{
background-color:#0b1b2b;
color:white;
}

.card{
background:#1c2c3e;
padding:25px;
border-radius:12px;
box-shadow:0px 0px 10px rgba(0,0,0,0.4);
border-left:4px solid #2ec4b6;
}

.card h3{
color:#7dd3fc;
font-size:14px;
margin-bottom:10px;
}

.card h1{
font-size:34px;
}

.sub-card{
background:#1c2c3e;
padding:20px;
border-radius:12px;
margin-bottom:15px;
}

.progress{
height:10px;
background:#34495e;
border-radius:5px;
}

.progress-bar{
height:10px;
background:#00c896;
border-radius:5px;
}

</style>
""",unsafe_allow_html=True)


st.markdown("## 📊 Key Metrics")

c1,c2,c3,c4,c5,c6 = st.columns(6)

with c1:
    st.markdown(f"""
    <div class='card'>
    <h3>TOTAL TARGETED PLOTS</h3>
    <h1>{int(total_target):,}</h1>
    <p>District-wide target</p>
    </div>
    """,unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='card'>
    <h3>TOTAL UPLOADED PLOTS</h3>
    <h1>{int(df['Total number of uploaded plots'].sum()):,}</h1>
    <p>Across all sub-divisions</p>
    </div>
    """,unsafe_allow_html=True)

with c3:
    completion = (completed_plots / total_target) * 100

    st.markdown(f"""
    <div class='card'>
    <h3>TOTAL SURVEYED</h3>
    <h1>{int(completed_plots):,}</h1>
    <p>{completion:.2f}% completion</p>
    </div>
    """,unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class='card'>
    <h3>PENDING FOR SURVEY</h3>
    <h1>{int(pending):,}</h1>
    </div>
    """,unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class='card'>
    <h3>SURVEYORS IDENTIFIED</h3>
    <h1>{int(surveyors):,}</h1>
    </div>
    """,unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class='card'>
    <h3>SURVEYED TODAY</h3>
    <h1>{int(survey_today):,}</h1>
    </div>
    """,unsafe_allow_html=True)
st.markdown("________________________________________________________________________________________________________")

m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        "🏘️ Total Villages",
        f"{int(total_villages):,}"
    )

with m2:
    st.metric(
        "✅ Completed Plots",
        f"{int(completed_plots):,}"
    )

with m3:
    st.metric(
        "⏳ Pending Survey",
        f"{int(pending):,}"
    )
st.markdown("________________________________________________________________________________________________________")
# ___________________________________________________________________________________________________________________
st.markdown("## 📊 Sub-Division Performance")

cols = st.columns(4)

for i, row in df.iterrows():

    col = cols[i % 4]

    progress = row["Survey Progress"]
    approval = row.get("Approval Rate", 0)

    progress_color = "#00c896"

    if progress < 40:
        progress_color = "#ff4d4d"

    with col:

        st.markdown(f"""
        <div class='sub-card'>

        <h3 style="color:#38bdf8">{row['Tehsil']}</h3>

        <p>Survey Progress {progress:.2f}%</p>

        <div class="progress">
            <div class="progress-bar" style="width:{progress}%;background:{progress_color}"></div>
        </div>

        <br>

        <p>Total Plots: {int(row['Total Plots']):,}</p>
        <p>Surveyed Plots: {int(row['Surveyed Plots']):,}</p>
        <p>Surveyors: {int(row['Surveyors'])}</p>
        <p>In Field: {int(row['In Field'])}</p>

        </div>
        """, unsafe_allow_html=True)



st.markdown("""
<style>

.chart-card{
background:#1c2c3e;
padding:20px;
border-radius:14px;
box-shadow:0px 10px 25px rgba(0,0,0,0.35);
margin-bottom:25px;
}

.chart-title{
color:#38bdf8;
font-size:18px;
font-weight:600;
margin-bottom:10px;
}

</style>
""",unsafe_allow_html=True)

st.markdown("## 📊 Analytics")

# ---------- ROW 1 ----------
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>Survey Completion</div>", unsafe_allow_html=True)

        fig1 = px.bar(
            df,
            x="Tehsil",
            y="Survey Completion",
            color="Survey Completion",
            color_continuous_scale="Tealgrn"
        )

        fig1.update_layout(
            paper_bgcolor="#1c2c3e",
            plot_bgcolor="#1c2c3e",
            font_color="white",
            xaxis_tickangle=-25,
            margin=dict(l=10, r=10, t=10, b=10)
        )

        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


with col2:
    with st.container():
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>Approval Rate</div>", unsafe_allow_html=True)

        fig2 = px.bar(
            df,
            x="Tehsil",
            y="Approval Rate",
            color="Approval Rate",
            color_continuous_scale="Teal"
        )

        fig2.update_layout(
            paper_bgcolor="#1c2c3e",
            plot_bgcolor="#1c2c3e",
            font_color="white",
            xaxis_tickangle=-25,
            margin=dict(l=10, r=10, t=10, b=10)
        )

        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ---------- ROW 2 ----------
col3, col4 = st.columns(2)

with col3:
    with st.container():
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>Surveyor Deployment</div>", unsafe_allow_html=True)

        fig3 = px.bar(
            df,
            x="Tehsil",
            y=["Surveyors", "Surveyors In Field"],
            barmode="group"
        )

        fig3.update_layout(
            paper_bgcolor="#1c2c3e",
            plot_bgcolor="#1c2c3e",
            font_color="white",
            xaxis_tickangle=-25,
            margin=dict(l=10, r=10, t=10, b=10)
        )

        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


with col4:
    with st.container():
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>Daily Progress</div>", unsafe_allow_html=True)

        fig4 = px.line(
            df,
            x="Tehsil",
            y="Daily Progress",
            markers=True
        )

        fig4.update_layout(
            paper_bgcolor="#1c2c3e",
            plot_bgcolor="#1c2c3e",
            font_color="white",
            xaxis_tickangle=-25,
            margin=dict(l=10, r=10, t=10, b=10)
        )

        fig4.update_traces(line=dict(color="#38bdf8", width=3))

        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)



st.markdown("## 🏆 Top Performing Subdivisions")

top5 = df.sort_values(
    "Survey Completion",
    ascending=False
).head(5)

fig_top = px.bar(
    top5,
    x="Tehsil",
    y="Survey Completion",
    color="Survey Completion",
    color_continuous_scale="Greens",
    title="Top 5 Survey Completion"
)

fig_top.update_layout(
    paper_bgcolor="#1c2c3e",
    plot_bgcolor="#1c2c3e",
    font_color="white"
)

st.plotly_chart(fig_top, use_container_width=True)

###############################################################################################################
st.markdown("##  Worst Performing Subdivisions")

worst5 = df.sort_values(
    "Survey Completion",
    ascending=True
).head(5)

fig_worst = px.bar(
    worst5,
    x="Tehsil",
    y="Survey Completion",
    color="Survey Completion",
    text="Survey Completion",
    color_continuous_scale="Reds"
)

fig_worst.update_layout(
    paper_bgcolor="#1c2c3e",
    plot_bgcolor="#1c2c3e",
    font_color="white",
    title="Lowest Survey Completion"
)

fig_worst.update_traces(texttemplate="%{text:.1f}%", textposition="outside")


st.plotly_chart(fig_worst, use_container_width=True)

###############################################################################################################

st.markdown("## 📊 District Progress")

district_progress = pd.DataFrame({
    "Category": ["Target Plots", "Completed Plots", "Pending Plots"],
    "Plots": [
        total_target,
        completed_plots,
        pending
    ]
})

fig_progress = px.bar(
    district_progress,
    x="Category",
    y="Plots",
    color="Category",
    text="Plots",
    color_discrete_sequence=["#38bdf8", "#22c55e", "#ef4444"]
)

fig_progress.update_layout(
    paper_bgcolor="#1c2c3e",
    plot_bgcolor="#1c2c3e",
    font_color="white",
    showlegend=False
)

fig_progress.update_traces(textposition="outside")

st.plotly_chart(fig_progress, use_container_width=True)

##########################################################################################
st.markdown("## 📊 Completion Trend Over Time (Tehsil-wise)")

# Convert wide → long format
trend_df = df.melt(
    id_vars=["Tehsil"],
    value_vars=survey_cols,
    var_name="Date",
    value_name="Completed_Plots"
)

trend_df["Date"] = trend_df["Date"].str.replace("Plots surveyed on ", "")
trend_df["Date"] = pd.to_datetime(trend_df["Date"], format="%d-%m-%Y")

# Tehsil filter
selected_tehsil = st.multiselect(
    "Select Tehsil",
    trend_df["Tehsil"].unique(),
    default=trend_df["Tehsil"].unique()
)

trend_filtered = trend_df[trend_df["Tehsil"].isin(selected_tehsil)]

fig_trend = px.line(
    trend_filtered,
    x="Date",
    y="Completed_Plots",
    color="Tehsil",
    markers=True
)

fig_trend.update_layout(
    paper_bgcolor="#0b1b2b",
    plot_bgcolor="#0b1b2b",
    font_color="white"
)

st.plotly_chart(fig_trend, use_container_width=True)

##################################################################################################################################

st.markdown("## 📊 Tehsil-wise Survey Status")

status_df = df[[
    "Tehsil",
    "Number of completed Plots till date",
    "Pending for survey"
]].copy()

status_df = status_df.rename(columns={
    "Number of completed Plots till date": "Completed_Plots",
    "Pending for survey": "Pending_Survey"
})

fig_status = px.bar(
    status_df,
    x="Tehsil",
    y=["Completed_Plots", "Pending_Survey"],
    barmode="stack"
)

fig_status.update_layout(
    paper_bgcolor="#0b1b2b",
    plot_bgcolor="#0b1b2b",
    font_color="white",
    xaxis_tickangle=-25
)

st.plotly_chart(fig_status, use_container_width=True)
###############################################################################################################################

df["Number of Pvt. Surveyors identified"] = pd.to_numeric(
    df["Number of Pvt. Surveyors identified"], errors="coerce"
)

df["Number of villages allocated"] = pd.to_numeric(
    df["Number of villages allocated"], errors="coerce"
)

st.markdown("## 👥 Resource Deployment")

resource_df = df[[
    "Tehsil",
    "Number of Pvt. Surveyors identified",
    "Number of villages allocated"
]].copy()

resource_df = resource_df.rename(columns={
    "Number of Pvt. Surveyors identified": "Surveyors Identified",
    "Number of villages allocated": "Villages Allocated"
})

fig_resource = px.bar(
    resource_df,
    x="Tehsil",
    y=["Surveyors Identified", "Villages Allocated"],
    barmode="group"
)

fig_resource.update_layout(
    paper_bgcolor="#0b1b2b",
    plot_bgcolor="#0b1b2b",
    font_color="white",
    xaxis_tickangle=-25
)

st.plotly_chart(fig_resource, use_container_width=True)




st.subheader("Detailed Sub-Division Report")

st.dataframe(df,use_container_width=True)