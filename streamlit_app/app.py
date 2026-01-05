# streamlit_app/app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ============================
# PAGE CONFIG
# ============================
st.set_page_config(page_title="⚽ Football 2024-25 Dashboard", layout="wide")
st.title("⚽ Football Match Analysis Dashboard (2024–25)")

# ============================
# LOAD DATA
# ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "football_matches_2024_2025.csv")

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error("Dataset not found. Please check file path.")
    st.stop()

# ============================
# SIDEBAR FILTERS
# ============================
st.sidebar.header("Filters")
league = st.sidebar.selectbox("Select Competition", sorted(df["competition_name"].unique()))
stages = ["All"] + sorted(df["stage"].dropna().unique())
stage = st.sidebar.selectbox("Select Stage", stages)

filtered = df[df["competition_name"] == league]
if stage != "All":
    filtered = filtered[filtered["stage"] == stage]

if filtered.empty:
    st.warning("No matches found for selected filters.")
    st.stop()

# ============================
# KPIs (UPDATED)
# ============================
total_matches = len(filtered)
avg_goals = filtered["total_goals"].mean()

team_goals = pd.concat([
    filtered[["home_team", "fulltime_home"]].rename(columns={"home_team": "team", "fulltime_home": "goals"}),
    filtered[["away_team", "fulltime_away"]].rename(columns={"away_team": "team", "fulltime_away": "goals"})
])

top_team = (
    team_goals.groupby("team")["goals"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
)

k1, k2, k3 = st.columns(3)
k1.metric("Total Matches", total_matches)
k2.metric("Avg Goals / Match", f"{avg_goals:.2f}")
k3.metric("Top Scoring Team", top_team)

st.markdown("---")

# ============================
# 1. Goals per Match
# ============================
fig1 = px.histogram(filtered, x="total_goals", nbins=12, title="Goals per Match")
st.plotly_chart(fig1, use_container_width=True)

# ============================
# 2. Home vs Away Goals
# ============================
fig2 = px.box(
    filtered,
    y=["fulltime_home", "fulltime_away"],
    labels={"value": "Goals", "variable": "Type"},
    title="Home vs Away Goals Distribution"
)
st.plotly_chart(fig2, use_container_width=True)

# ============================
# 3. Match Outcome Distribution
# ============================
outcomes = filtered["match_outcome"].value_counts().reset_index()
outcomes.columns = ["Outcome", "Count"]
fig3 = px.pie(outcomes, names="Outcome", values="Count", title="Match Outcome Distribution")
st.plotly_chart(fig3, use_container_width=True)

# ============================
# 4. Top 10 Highest Scoring Matches
# ============================
st.subheader("Top 10 Highest Scoring Matches")
top_matches = filtered.sort_values("total_goals", ascending=False).head(10)
st.dataframe(top_matches[["date_utc", "home_team", "away_team", "total_goals", "stage"]])

# ============================
# 5. Average Goals by Stage
# ============================
avg_goals_stage = filtered.groupby("stage")["total_goals"].mean().reset_index()
fig5 = px.bar(avg_goals_stage, x="stage", y="total_goals", title="Average Goals by Stage")
st.plotly_chart(fig5, use_container_width=True)

# ============================
# 6. Top 5 Scoring Teams
# ============================
top5_teams = (
    team_goals.groupby("team")["goals"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)
fig6 = px.bar(top5_teams, x="team", y="goals", title="Top 5 Scoring Teams")
st.plotly_chart(fig6, use_container_width=True)

# ============================
# 7. Matchday Goal Trend
# ============================
if "matchday" in filtered.columns:
    trend = filtered.groupby("matchday")["total_goals"].sum().reset_index()
    fig7 = px.line(trend, x="matchday", y="total_goals", title="Goals Trend by Matchday", markers=True)
    st.plotly_chart(fig7, use_container_width=True)

# ============================
# 8. Goal Difference Distribution
# ============================
fig8 = px.histogram(filtered, x="goal_difference", nbins=12, title="Goal Difference Distribution")
st.plotly_chart(fig8, use_container_width=True)

# ============================
# 9. Goals Heatmap
# ============================
heatmap_df = filtered.groupby(["fulltime_home", "fulltime_away"]).size().reset_index(name="matches")
fig9 = px.density_heatmap(
    heatmap_df,
    x="fulltime_home",
    y="fulltime_away",
    z="matches",
    title="Home vs Away Goals Heatmap",
    color_continuous_scale="Turbo"
)
st.plotly_chart(fig9, use_container_width=True)

# ============================
# 10. Matches by Referee
# ============================
ref_df = filtered["referee"].value_counts().head(10).reset_index()
ref_df.columns = ["Referee", "Matches"]
fig10 = px.bar(ref_df, x="Referee", y="Matches", title="Top 10 Referees by Matches")
st.plotly_chart(fig10, use_container_width=True)
