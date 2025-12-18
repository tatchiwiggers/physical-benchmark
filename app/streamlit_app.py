import streamlit as st
import pandas as pd
import altair as alt


st.set_page_config(
    page_title="Football Benchmark Dashboard",
    layout="wide"
)


@st.cache_data
def load_data():
    return pd.read_csv("data/prepped_players_data.csv")

df = load_data()


st.sidebar.header("Filters")

leagues = sorted(df["newestLeague"].dropna().unique().tolist())
teams = sorted(df["team"].dropna().unique().tolist())
positions = sorted(df["Position"].dropna().unique().tolist())

selected_league = st.sidebar.selectbox("Select League", ["All"] + leagues)
selected_team = st.sidebar.selectbox("Select Team", ["All"] + teams)
selected_position = st.sidebar.selectbox("Select Position", ["All"] + positions)

filtered_df = df.copy()

if selected_league != "All":
    filtered_df = filtered_df[filtered_df["newestLeague"] == selected_league]

if selected_team != "All":
    filtered_df = filtered_df[filtered_df["team"] == selected_team]

if selected_position != "All":
    filtered_df = filtered_df[filtered_df["Position"] == selected_position]


def safe_metric(df, column):
    if df.empty:
        return "—"
    value = df[column].mean(skipna=True)
    if pd.isna(value):
        return "—"
    return f"{value:.1f} m"


st.title("🏃‍♂️ High-Intensity Running Benchmark")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Avg High-Speed Dist (per90)",
    safe_metric(filtered_df, "TotalHighSpeedDist_per90")
)

col2.metric(
    "Avg 20–25 km/h Dist (per90)",
    safe_metric(filtered_df, "HiSpeedRunDist_per90")
)

col3.metric(
    "Avg Sprint Dist >25 km/h (per90)",
    safe_metric(filtered_df, "SprintDist_per90")
)

st.markdown("---")


st.subheader("📊 Distribution by Team")

if filtered_df.empty:
    st.info("No data available for the selected filters.")
else:
    team_stats = (
        filtered_df
        .groupby("team")[[
            "TotalHighSpeedDist_per90",
            "HiSpeedRunDist_per90",
            "SprintDist_per90"
        ]]
        .mean()
        .reset_index()
        .sort_values("TotalHighSpeedDist_per90", ascending=False)
    )

    chart = (
        alt.Chart(team_stats)
        .transform_fold(
            [
                "TotalHighSpeedDist_per90",
                "HiSpeedRunDist_per90",
                "SprintDist_per90"
            ],
            as_=["Metric", "Value"]
        )
        .mark_bar()
        .encode(
            y=alt.Y("team:N", sort="-x", title="Team"),
            x=alt.X("Value:Q", title="Meters per 90 min"),
            color=alt.Color("Metric:N", title="Metric"),
            tooltip=[
                alt.Tooltip("team:N", title="Team"),
                alt.Tooltip("Metric:N", title="Metric"),
                alt.Tooltip("Value:Q", title="Value (per90)", format=".1f")
            ]
        )
    )

    st.altair_chart(chart, use_container_width=True)

st.subheader("📋 Player Statistics (per 90 mins)")

if filtered_df.empty:
    st.info("No players match the selected filters.")
else:
    st.dataframe(
        filtered_df[[
            "player", "team", "Position",
            "TotalHighSpeedDist_per90",
            "HiSpeedRunDist_per90",
            "SprintDist_per90"
        ]]
        .sort_values("TotalHighSpeedDist_per90", ascending=False),
        use_container_width=True
    )
