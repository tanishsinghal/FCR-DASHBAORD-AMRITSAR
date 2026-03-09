import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="FCR Dashboard",
    layout="wide"
)

st.title("📊 FCR Daily Dashboard")
st.markdown("---")


# ====================================================
# TEHSIL FILTER
# ====================================================

tehsil_list = [
    "ASR I",
    "Jandiala Guru",
    "ASR II",
    "Attari",
    "Ajnala",
    "Ramdass",
    "Baba Bakala Sahib",
    "Tarsikka",
    "Beas",
    "Lopoke",
    "Rajasansi",
    "Majitha"
]

selected_tehsils = st.sidebar.multiselect(
    "Select Tehsil",
    tehsil_list,
    default=tehsil_list
)

no_tehsil_selected = len(selected_tehsils) == 0

if no_tehsil_selected:
    st.warning("Please select at least one Tehsil")
# ====================================================
# LOAD MUTATION
# ====================================================

@st.cache_data(ttl=300)
def load_mutation():
    url = "https://docs.google.com/spreadsheets/d/135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY/export?format=csv&gid=2073381520"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

mutation_df = load_mutation()

if "tehsil" in mutation_df.columns:
    mutation_df = mutation_df[mutation_df["tehsil"].isin(selected_tehsils)]

mutation_pending = int(
    mutation_df["grand_total_of_mutation_pendency_beyond_30_days"].sum()
)

# ====================================================
# LOAD MUSAVI
# ====================================================

@st.cache_data(ttl=300)
def load_musavi():
    url = "https://docs.google.com/spreadsheets/d/135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY/export?format=csv&gid=1163442311"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

musavi_df = load_musavi()

if "Tehsil / Sub-Tehsil" in musavi_df.columns:
    musavi_df = musavi_df[musavi_df["Tehsil / Sub-Tehsil"].isin(selected_tehsils)]

musavi_pending = int(
    musavi_df["Pending at Patwari"].sum()
    + musavi_df["Pending at CRO"].sum()
    + musavi_df["Pending at RPSC"].sum()
)

# ====================================================
# LOAD BHUNAKSHA
# ====================================================

@st.cache_data(ttl=300)
def load_bhunaksha():
    url = "https://docs.google.com/spreadsheets/d/135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY/export?format=csv&gid=741935264"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

bhunaksha_df = load_bhunaksha()

if "Name of Tehsil/Sub Tehsil" in bhunaksha_df.columns:
    bhunaksha_df = bhunaksha_df[
        bhunaksha_df["Name of Tehsil/Sub Tehsil"].isin(selected_tehsils)
    ]

bhunaksha = {
    "shapefiles": int(bhunaksha_df["No. of Villages of which Shapefiles available with Districts"].sum()),
    "initiated": int(bhunaksha_df["Total no. of villages where tatima incorporation work has been initiated"].sum()),
    "incorporated": int(bhunaksha_df["Total no. of Tatimas incorporated"].sum()),
    "pending": int(bhunaksha_df["Tatima incorporation Pending at Patwari level"].sum()),
    "completed": int(bhunaksha_df["No. of villages where Tatima work has been completed"].sum()),
}

# ====================================================
# LOAD DIGITAL CROP
# ====================================================

@st.cache_data(ttl=300)
def load_crop():
    url = "https://docs.google.com/spreadsheets/d/135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY/export?format=csv&gid=30899428"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

crop_df = load_crop()

if "Tehsil" in crop_df.columns:
    crop_df = crop_df[crop_df["Tehsil"].isin(selected_tehsils)]

elif "Tehsil / Sub-Tehsil" in crop_df.columns:
    crop_df = crop_df[crop_df["Tehsil / Sub-Tehsil"].isin(selected_tehsils)]

crop = {
    "villages": int(crop_df["Total no. of villages"].sum()),
    "total_plots": int(crop_df["Total number of uploaded plots"].sum()),
    "surveyed": int(crop_df["Number of completed Plots till date"].sum()),
    "pending": int(crop_df["Pending for survey"].sum()),
    "surveyors": int(crop_df["Number of Pvt. Surveyors identified"].sum()),
}

# ====================================================
# LOAD SVAMITWA
# ====================================================

@st.cache_data(ttl=300)
def load_svamitwa():
    url = "https://docs.google.com/spreadsheets/d/135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY/export?format=csv&gid=1518724049"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

svamitwa_df = load_svamitwa()

if "Name of Tehsil" in svamitwa_df.columns:
    svamitwa_df = svamitwa_df[
        svamitwa_df["Name of Tehsil"].isin(selected_tehsils)
    ]

numeric_cols = svamitwa_df.select_dtypes(include="number").columns
sv = svamitwa_df[numeric_cols].sum()

# ====================================================
# TOTAL DISTRICT PENDENCY
# ====================================================

if no_tehsil_selected:

    total_pendency = 0

else:

    total_pendency = (
        mutation_pending
        + musavi_pending
        + bhunaksha["pending"]
        + crop["pending"]
    )

# ====================================================
# TOP KPI
# ====================================================

c1, c2 = st.columns(2)

c1.metric("Total Pendency", total_pendency)
c2.metric("Total Sub Divisions", len(selected_tehsils))

st.markdown("---")

# ====================================================
# MUTATION SUMMARY
# ====================================================

st.subheader("Mutation Summary")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Patwari >30 Days",
          int(mutation_df["pendency_at_patwari_level_beyond_30_days"].sum()))

m2.metric("Kanungo >30 Days",
          int(mutation_df["pendency_at_kanungo_level_beyond_30_days"].sum()))

m3.metric("CRO >30 Days",
          int(mutation_df["pendency_at_cro_level_beyond_30_days"].sum()))

m4.metric("Total Mutation Pending", mutation_pending)

st.markdown("---")

# ====================================================
# MUSAVI SUMMARY
# ====================================================

st.subheader("Musavi Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Villages", int(musavi_df["Total Villages"].sum()))
c2.metric("Maps Received", int(musavi_df["Maps Received"].sum()))
c3.metric("Maps Validated", int(musavi_df["Maps Validated"].sum()))
c4.metric("Total Pending", musavi_pending)

st.markdown("---")

# ====================================================
# BHUNAKSHA SUMMARY
# ====================================================

st.subheader("Bhunaksha Summary")

b1, b2, b3, b4, b5 = st.columns(5)

b1.metric("Shapefile Villages", bhunaksha["shapefiles"])
b2.metric("Villages Initiated", bhunaksha["initiated"])
b3.metric("Tatima Incorporated", bhunaksha["incorporated"])
b4.metric("Pending", bhunaksha["pending"])
b5.metric("Villages Completed", bhunaksha["completed"])

st.markdown("---")

# ====================================================
# DIGITAL CROP
# ====================================================
# ====================================================
# DIGITAL CROP
# ====================================================

@st.cache_data(ttl=300)
def load_crop():

    url = "https://docs.google.com/spreadsheets/d/135UDDzE8hCCSYn4WT1a6kED4lhL7mj6cDfms3PNGJPY/export?format=csv&gid=30899428"

    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()

    return df


crop_df = load_crop()

if no_tehsil_selected:

    crop = {
        "villages": 0,
        "total_plots": 0,
        "surveyed": 0,
        "pending": 0,
        "surveyors": 0,
    }

else:

    crop = {
        "villages": int(crop_df["Total no. of villages"].sum()),
        "total_plots": int(crop_df["Total number of uploaded plots"].sum()),
        "surveyed": int(crop_df["Number of completed Plots till date"].sum()),
        "pending": int(crop_df["Pending for survey"].sum()),
        "surveyors": int(crop_df["Number of Pvt. Surveyors identified"].sum()),
    }
# ====================================================
# SVAMITWA SUMMARY
# ====================================================

st.subheader("Svamitwa Summary")

cols = st.columns(4)

for i, col in enumerate(sv.index[:4]):
    cols[i].metric(col.replace("_", " "), int(sv[col]))

st.markdown("---")

st.caption("FCR Monitoring Dashboard")
st.caption("Prepared by Tanish Singhal")
# # ???????????????????????????????????????????????????????????????????????????????????????????????????
# ???????????????????????????????????????????????????????????????????????????????????????????????????
# ???????????????????????????????????????????????????????????????????????????????????????????????????
# ???????????????????????????????????????????????????????????????????????????????????????????????????
# ???????????????????????????????????????????????????????????????????????????????????????????????????
# ???????????????????????????????????????????????????????????????????????????????????????????????????
# ???????????????????????????????????????????????????????????????????????????????????????????????????
# ???????????????????????????????????????????????????????????????????????????????????????????????????

# ==============================
# PENDENCY SUMMARY
# ==============================

pendency_summary = {
    "Mutation Pending": mutation_pending,
    "Musavi Pending": musavi_pending,
    "Bhunaksha Pending": bhunaksha["pending"],
    "Digital Crop Pending": crop["pending"]
}

total_all = sum(pendency_summary.values())


# ==============================
# TOP 3 SUB DIVISIONS + CRITICAL ISSUES
# ==============================

st.subheader("📊 Top 3 Sub Divisions by Pendency")

col_left, col_right = st.columns([2,1])

with col_left:

    sub_data = {
        "ASR I": 120,
        "Jandiala Guru": 90,
        "ASR II": 60
    }

    sub_summary = pd.DataFrame(
        list(sub_data.items()),
        columns=["Sub Division","Total"]
    )

    total_sum = sub_summary["Total"].sum()

    for _, row in sub_summary.iterrows():

        name = row["Sub Division"]
        value = row["Total"]

        percent = (value / total_sum * 100)

        st.markdown(f"### {name}")
        st.write(f"**{value}** ({percent:.1f}% of total)")
        st.progress(percent/100)
with col_right:

    st.subheader("🔥 Critical Issues")

    top_issue = max(pendency_summary, key=pendency_summary.get)
    top_issue_value = pendency_summary[top_issue]

    highest_sub = sub_summary.iloc[0]["Sub Division"]
    highest_value = sub_summary.iloc[0]["Total"]

    st.markdown("### Top Issue:")
    st.write(top_issue)

    st.markdown(f"## {top_issue_value}")

    if total_all > 0:
        st.caption(f"{(top_issue_value/total_all*100):.1f}% of total")

    # st.markdown("---")

    # st.markdown("### Highest Alert:")
    #st.write(highest_sub)

    #st.markdown(f"## {highest_value}")
st.markdown("---")

# ==============================
# WORST 3 SUB DIVISIONS
# ==============================

st.subheader("⚠️ Worst 3 Sub Divisions by Pendency")

# Group data by Sub Division
sub_summary = (
    mutation_df
    .groupby("tehsil")["grand_total_of_mutation_pendency_beyond_30_days"]
    .sum()
    .sort_values(ascending=False)
    .head(3)
    .reset_index()
)

total_sum = sub_summary["grand_total_of_mutation_pendency_beyond_30_days"].sum()

for _, row in sub_summary.iterrows():

    name = row["tehsil"]
    value = row["grand_total_of_mutation_pendency_beyond_30_days"]

    percent = (value / total_sum * 100) if total_sum > 0 else 0

    st.markdown(f"### {name}")
    st.write(f"**{int(value)}** ({percent:.1f}% of worst pendency)")

    st.progress(percent/100)

    st.markdown("")

st.markdown("---")

