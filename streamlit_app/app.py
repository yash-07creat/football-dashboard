# streamlit_app/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ============================
# PAGE CONFIG
# ============================
st.set_page_config(
    page_title="⚽ Football 2024-25 Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("⚽ Football Match Analysis Dashboard (2024–25)")

# ============================
# LOAD DATASET
# ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "football_matches_2024_2025.csv")

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"Dataset not found at {DATA_PATH}")
    st.stop()

# ============================
# SIDEBAR FILTERS
# ============================
st.sidebar.header("Filters")
league = st.sidebar.selectbox("Select Competition", df["competition_name"].unique())
stage = st.sidebar.selectbox(
    "Select Stage",
    ["All"] + sorted(df["stage"].unique())
)

filtered = df[df["competition_name"] == league]
if stage != "All":
    filtered = filtered[filtered["stage"] == stage]

# ============================
# KPI CARDS
# ============================
total_matches = filtered.shape[0]
avg_goals = filtered["total_goals"].mean()
home_wins = filtered[filtered["match_outcome"] == "H"].shape[0] / total_matches * 100
top_scoring_team = pd.concat([filtered[["home_team","fulltime_home"]].rename(columns={"home_team":"team","fulltime_home":"goals"}),
                              filtered[["away_team","fulltime_away"]].rename(columns={"away_team":"team","fulltime_away":"goals"})]
                            ).groupby("team")["goals"].sum().idxmax()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Matches", total_matches)
kpi2.metric("Average Goals", f"{avg_goals:.2f}")
kpi3.metric("Home Win %", f"{home_wins:.1f}%")
kpi4.metric("Top Scoring Team", top_scoring_team)

st.markdown("---")

# ============================
# CHART 1: Total Goals Distribution
# ============================
fig_goals = px.histogram(
    filtered,
    x="total_goals",
    nbins=12,
    title="Goals per Match",
    labels={"total_goals":"Goals"}
)
st.plotly_chart(fig_goals, use_container_width=True)

# ============================
# CHART 2: Home vs Away Goals
# ============================
fig_box = px.box(
    filtered,
    y=["fulltime_home","fulltime_away"],
    labels={"value":"Goals","variable":"Type"},
    title="Home vs Away Goals Distribution"
)
st.plotly_chart(fig_box, use_container_width=True)

# ============================
# CHART 3: Match Outcomes
# ============================
outcome_counts = filtered["match_outcome"].value_counts().reset_index()
outcome_counts.columns = ["Outcome","Count"]
fig_outcome = px.pie(
    outcome_counts,
    names="Outcome",
    values="Count",
    title="Match Outcome Distribution"
)
st.plotly_chart(fig_outcome, use_container_width=True)

# ============================
# CHART 4: Top 10 Highest Scoring Matches
# ============================
st.subheader("Top 10 Highest Scoring Matches")
top_matches = filtered.sort_values("total_goals", ascending=False).head(10)
st.dataframe(top_matches[["date_utc","home_team","away_team","total_goals","stage"]])

# ============================
# OPTIONAL: Average Goals by Stage
# ============================
st.subheader("Average Goals by Stage")
avg_goals_stage = filtered.groupby("stage")["total_goals"].mean().reset_index()
fig_stage = px.bar(
    avg_goals_stage,
    x="stage",
    y="total_goals",
    title="Average Goals per Stage",
    labels={"total_goals":"Average Goals","stage":"Stage"}
)
st.plotly_chart(fig_stage, use_container_width=True)
