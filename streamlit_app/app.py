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
    st.error(f"Dataset not found at {DATA_PATH}")
    st.stop()

# ============================
# SIDEBAR FILTERS
# ============================
st.sidebar.header("Filters")
league = st.sidebar.selectbox("Select Competition", df["competition_name"].unique())
stages = ["All"] + sorted(df["stage"].unique())
stage = st.sidebar.selectbox("Select Stage", stages)

filtered = df[df["competition_name"] == league]
if stage != "All":
    filtered = filtered[filtered["stage"] == stage]

# ============================
# HANDLE EMPTY DATA
# ============================
total_matches = filtered.shape[0]
if total_matches == 0:
    st.warning("No matches found for this competition & stage combination.")
    st.stop()

# ============================
# KPIs (ACCURATE CALCULATION)
# ============================
outcome_counts = filtered["match_outcome"].value_counts()

home_wins_count = outcome_counts.get("H", 0)
away_wins_count = outcome_counts.get("A", 0)
draws_count = outcome_counts.get("D", 0)

home_wins_pct = (home_wins_count / total_matches) * 100
away_wins_pct = (away_wins_count / total_matches) * 100
draws_pct = (draws_count / total_matches) * 100

avg_goals = filtered["total_goals"].mean()

team_goals = pd.concat([
    filtered[["home_team","fulltime_home"]].rename(columns={"home_team":"team","fulltime_home":"goals"}),
    filtered[["away_team","fulltime_away"]].rename(columns={"away_team":"team","fulltime_away":"goals"})
]).groupby("team")["goals"].sum().sort_values(ascending=False)

top_team = team_goals.index[0]

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
kpi1.metric("Total Matches", total_matches)
kpi2.metric("Average Goals", f"{avg_goals:.2f}")
kpi3.metric("Home Win %", f"{home_wins_pct:.1f}%")
kpi4.metric("Away Win %", f"{away_wins_pct:.1f}%")
kpi5.metric("Draw %", f"{draws_pct:.1f}%")
kpi6.metric("Top Scoring Team", top_team)


# ============================
# 1. Goals per Match
# ============================
fig1 = px.histogram(filtered, x="total_goals", nbins=12, title="Goals per Match", labels={"total_goals":"Goals"})
st.plotly_chart(fig1, use_container_width=True)

# ============================
# 2. Home vs Away Goals
# ============================
fig2 = px.box(filtered, y=["fulltime_home","fulltime_away"], labels={"value":"Goals","variable":"Type"}, title="Home vs Away Goals Distribution")
st.plotly_chart(fig2, use_container_width=True)

# ============================
# 3. Match Outcome Distribution
# ============================
outcome_counts = filtered["match_outcome"].value_counts().reset_index()
outcome_counts.columns = ["Outcome","Count"]
fig3 = px.pie(outcome_counts, names="Outcome", values="Count", title="Match Outcome Distribution")
st.plotly_chart(fig3, use_container_width=True)

# ============================
# 4. Top 10 Highest Scoring Matches
# ============================
st.subheader("Top 10 Highest Scoring Matches")
top_matches = filtered.sort_values("total_goals", ascending=False).head(10)
st.dataframe(top_matches[["date_utc","home_team","away_team","total_goals","stage"]])

# ============================
# 5. Average Goals by Stage
# ============================
avg_goals_stage = filtered.groupby("stage")["total_goals"].mean().reset_index()
fig5 = px.bar(avg_goals_stage, x="stage", y="total_goals", color="total_goals", title="Average Goals per Stage", labels={"total_goals":"Avg Goals","stage":"Stage"})
st.plotly_chart(fig5, use_container_width=True)

# ============================
# 6. Top 5 Scoring Teams
# ============================
top5_teams = team_goals.head(5).reset_index()
fig6 = px.bar(top5_teams, x="team", y="goals", color="goals", title="Top 5 Scoring Teams")
st.plotly_chart(fig6, use_container_width=True)

# ============================
# 7. Matchday Trend of Total Goals
# ============================
if "matchday" in filtered.columns:
    trend_df = filtered.groupby("matchday")["total_goals"].sum().reset_index()
    fig7 = px.line(trend_df, x="matchday", y="total_goals", title="Total Goals Over Matchdays", markers=True)
    st.plotly_chart(fig7, use_container_width=True)

# ============================
# 8. Home vs Away Points Comparison
# ============================
fig8 = px.bar(filtered, x="home_team", y=["home_points","away_points"], title="Home vs Away Points per Match", labels={"value":"Points","variable":"Type"})
st.plotly_chart(fig8, use_container_width=True)

# ============================
# 9. Goal Difference Distribution
# ============================
fig9 = px.histogram(filtered, x="goal_difference", nbins=10, title="Goal Difference Distribution")
st.plotly_chart(fig9, use_container_width=True)

# ============================
# 10. Cumulative Goals per Team
# ============================
cumulative_goals = pd.concat([
    filtered[["home_team","fulltime_home"]].rename(columns={"home_team":"team","fulltime_home":"goals"}),
    filtered[["away_team","fulltime_away"]].rename(columns={"away_team":"team","fulltime_away":"goals"})
])
cumulative_goals = cumulative_goals.groupby("team")["goals"].cumsum().reset_index()
cumulative_goals["team"] = pd.concat([
    filtered["home_team"],
    filtered["away_team"]
]).reset_index(drop=True)
fig10 = px.line(cumulative_goals, x=cumulative_goals.index, y="goals", color="team", title="Cumulative Goals per Team")
st.plotly_chart(fig10, use_container_width=True)
