import time
import pandas as pd
import numpy as np
import streamlit as st
import requests

def get_matchups_data():
    
    data = pd.read_csv('IPL_Data/all_ipl_data.csv')

    # 50s and 100s

    runs_per_innings = pd.DataFrame(data.groupby(['striker', 'match_id'])['runs_off_bat'].sum().reset_index())

    runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
    runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

    fifties = pd.DataFrame(runs_per_innings.groupby(['striker'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
    hundreds = pd.DataFrame(runs_per_innings.groupby(['striker'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})

    # Additional Columns

    data['is_dot'] = data['runs_off_bat'].apply(lambda x: 1 if x == 0 else 0)
    data['is_one'] = data['runs_off_bat'].apply(lambda x: 1 if x == 1 else 0)
    data['is_two'] = data['runs_off_bat'].apply(lambda x: 1 if x == 2 else 0)
    data['is_three'] = data['runs_off_bat'].apply(lambda x: 1 if x == 3 else 0)
    data['is_four'] = data['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
    data['is_six'] = data['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

    bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
        'stumped', 'hit wicket']

    data['bowlers_wicket'] = data['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

    
    bat_vs_ball = data

    # Additional Columns

    dots = bat_vs_ball.groupby(['striker', 'bowler'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
    fours = bat_vs_ball.groupby(['striker', 'bowler'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
    sixes = bat_vs_ball.groupby(['striker', 'bowler'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

    runs_scored = bat_vs_ball.groupby(['striker', 'bowler'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
    balls_faced = bat_vs_ball.groupby(['striker', 'bowler'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
    dismissals = bat_vs_ball.groupby(['striker', 'bowler'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'dismissals'})
    innings = bat_vs_ball.groupby(['striker', 'bowler'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

    matchup = pd.merge(innings, runs_scored, on=['striker', 'bowler']).merge(
        balls_faced, on=['striker', 'bowler']).merge(
            dismissals, on=['striker', 'bowler']).merge(
                dots, on=['striker', 'bowler']).merge(
                    fours, on=['striker', 'bowler']).merge(
                        sixes, on=['striker', 'bowler'])

    matchup['batting_SR'] = 100 * matchup['runs_scored'] / matchup['balls_faced']
    matchup['dot_percentage'] = 100 * matchup['dots'] / matchup['balls_faced']
    matchup['inning_vs_dismissal'] = matchup['innings'] - matchup['dismissals']

    return matchup

def load_data():
    # with st.spinner('Loading matchup data...'):
    # time.sleep(2)  # Simulating data loading
    return get_matchups_data()

def main():
    # st.set_page_config(page_title="IPL Matchup Dashboard", page_icon="🏏", layout="wide")

    # Custom CSS for styling
    st.markdown("""
        <style>
        :root {
            --primary-color: #1E88E5;
            --secondary-color: #FFC107;
            --text-color: #212121;
            --background-color: #FFFFFF;
        }
        .dark-mode {
            --primary-color: #64B5F6;
            --secondary-color: #FFD54F;
            --text-color: #E0E0E0;
            --background-color: #121212;
        }
        body {
            color: var(--text-color);
            background-color: var(--background-color);
        }
        .stat-box {
            background-color: var(--background-color);
            border: 2px solid var(--primary-color);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-label {
            color: var(--text-color);
            font-size: 16px;
            font-weight: bold;
        }
        .stat-value {
            color: var(--secondary-color);
            font-size: 28px;
            font-weight: bold;
        }
        h1, h2, h3 {
            color: var(--primary-color);
        }
        .stButton > button {
            background-color: var(--primary-color);
            color: white;
            font-weight: bold;
            padding: 0.5em 1em;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .stButton > button:hover {
            background-color: var(--secondary-color);
            color: var(--text-color);
        }
        </style>""", unsafe_allow_html=True)

    bat_vs_bowl_matchup()

def bat_vs_bowl_matchup():
    try:
        # Use session state to store selections
        if 'batter_select' not in st.session_state:
            st.session_state.batter_select = None
        if 'bowler_select' not in st.session_state:
            st.session_state.bowler_select = None

        # Load data only once
        if 'matchup_data' not in st.session_state:
            st.session_state.matchup_data = load_data()

        matchup_data = st.session_state.matchup_data
        
        batters_list = sorted(list(set(matchup_data.striker.to_list())))
        bowlers_list = sorted(list(set(matchup_data.bowler.to_list())))
        
        col1, col2 = st.columns(2)
        with col1:
            batter_select = st.selectbox('Select Batter:', batters_list, index=200, key='batter')
        with col2:
            bowler_select = st.selectbox('Select Bowler:', bowlers_list, index=69, key='bowler')
        
        # Add a "Find" button
        if st.button('Find Matchup'):
            # Show loader only when button is clicked
            with st.spinner('Fetching matchup data...'):
                # Simulate a delay (you can remove this in production)
                time.sleep(2)
                
                filtered_data = matchup_data[
                    (matchup_data['striker'] == batter_select) & (matchup_data['bowler'] == bowler_select)]
                
                if not filtered_data.empty:
                    display_matchup_summary(filtered_data)
                    display_detailed_stats(filtered_data)
                else:
                    st.warning("No data available for this matchup.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def display_matchup_summary(data):
    st.markdown("<h2 style='text-align: center;'>Matchup Summary</h2>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <h3 style='text-align: center;'>{data['striker'].iloc[0]} vs {data['bowler'].iloc[0]}</h3>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    stats = [
        ("Innings", data['innings'].iloc[0]),
        ("Runs Scored", data['runs_scored'].iloc[0]),
        ("Balls Faced", data["balls_faced"].iloc[0]),
        ("Dismissals", data['dismissals'].iloc[0]),
        ("Batting Strike Rate", f"{data['batting_SR'].iloc[0]:.2f}"),
        ("Dot Percentage", f"{data['dot_percentage'].iloc[0]:.2f}%"),
    ]

    for i, (label, value) in enumerate(stats):
        with [col1, col2, col3][i % 3]:
            st.markdown(
                f"""
                <div class="stat-box">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

def display_detailed_stats(data):
    st.markdown("<h3 style='text-align: center;'>Detailed Matchup Statistics</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Scoring Breakdown")
        scoring_data = {
            'Dots': data['dots'].iloc[0],
            'Fours': data['fours'].iloc[0],
            'Sixes': data['sixes'].iloc[0]
        }
        st.bar_chart(scoring_data,y_label="Total Counts")

    with col2:
        st.subheader("Key Performance Indicators")
        kpi_data = {
            'Boundary %': f"{100 * (data['fours'].iloc[0] + data['sixes'].iloc[0]) / data['balls_faced'].iloc[0]:.2f}%",
            'Dot Ball %': f"{data['dot_percentage'].iloc[0]:.2f}%",
            'Average': f"{data['runs_scored'].iloc[0] / max(1, data['dismissals'].iloc[0]):.2f}",
            'Balls per Dismissal': f"{data['balls_faced'].iloc[0] / max(1, data['dismissals'].iloc[0]):.2f}"
        }
        for kpi, value in kpi_data.items():
            st.metric(label=kpi, value=value)

    st.markdown("---")
    # st.subheader("Runs Scored per Innings")
    # runs_per_innings = data['runs_scored'] / data['innings']
    # st.bar_chart({'Runs per Innings': runs_per_innings})
