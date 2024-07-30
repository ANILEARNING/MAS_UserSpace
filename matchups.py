import pandas as pd
import numpy as np
import streamlit as st
import requests

def get_matchups_data():
    
    data = pd.read_csv('IPL_Data\\all_ipl_data.csv')

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

def bat_vs_bowl_matchup():
    # Set page config
    # st.set_page_config(layout="wide", page_title="IPL Matchup Dashboard")

    # Custom CSS for overall styling
    st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #333333;
    }
    .stSelectbox > div > div {
        background-color: #F0F2F6;
    }
    .metric-box {
        background-color: #F0F2F6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-title {
        color: #555555;
        font-size: 16px;
        margin-bottom: 10px;
    }
    .metric-value {
        color: #1E88E5;
        font-size: 32px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <h1 style='text-align: center; color: #1E88E5; padding: 20px 0;'>IPL Matchup Dashboard</h1>
        """,
        unsafe_allow_html=True
    )

    # Create tabs
    tab1, tab2 = st.tabs(["Matchup Analysis", "Raw Data"])

    with tab1:
        try:
            weakness = get_matchups_data()

            # Get All Batters and Bowlers in a List
            batters_list = sorted(list(set(weakness.striker.to_list())))
            bowlers_list = sorted(list(set(weakness.bowler.to_list())))

            col1, col2 = st.columns(2)
            with col1:
                batter_select = st.selectbox('Select Batter:', batters_list, index=batters_list.index('V Kohli') if 'V Kohli' in batters_list else 0)
            with col2:
                bowler_select = st.selectbox('Select Bowler:', bowlers_list, index=bowlers_list.index('JJ Bumrah') if 'JJ Bumrah' in bowlers_list else 0)

            # Filter matchup data based on input names
            filtered_data = weakness[
                (weakness['striker'] == batter_select) & (weakness['bowler'] == bowler_select)]

            # Filter only Required Columns
            filtered_data = filtered_data[['striker', 'bowler', 'innings', 'runs_scored', 'balls_faced',
                                           'dismissals', 'batting_SR', 'dot_percentage']]

            if not filtered_data.empty:
                st.markdown(f"<h2 style='text-align: center; color: #333333; padding: 20px 0;'>{batter_select} vs {bowler_select}</h2>", unsafe_allow_html=True)

                # Create columns for each box
                col1, col2, col3 = st.columns(3)

                # Custom function to create metric box
                def metric_box(title, value):
                    return f"""
                    <div class="metric-box">
                        <div class="metric-title">{title}</div>
                        <div class="metric-value">{value}</div>
                    </div>
                    """

                # Display each field in an enclosed box
                with col1:
                    st.markdown(metric_box("Innings", filtered_data['innings'].iloc[0]), unsafe_allow_html=True)
                    st.markdown(metric_box("Runs Scored", filtered_data['runs_scored'].iloc[0]), unsafe_allow_html=True)

                with col2:
                    st.markdown(metric_box("Dismissals", filtered_data['dismissals'].iloc[0]), unsafe_allow_html=True)
                    st.markdown(metric_box("Balls Faced", filtered_data["balls_faced"].iloc[0]), unsafe_allow_html=True)

                with col3:
                    st.markdown(metric_box("Batting Strike Rate", f"{filtered_data['batting_SR'].iloc[0]:.2f}"), unsafe_allow_html=True)
                    st.markdown(metric_box("Dot Percentage", f"{filtered_data['dot_percentage'].iloc[0]:.2f}%"), unsafe_allow_html=True)

            else:
                st.warning("No data found for this matchup. Please select different players.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")

    with tab2:
        try:
            if 'filtered_data' in locals() and not filtered_data.empty:
                st.markdown("<h2 style='text-align: center; color: #333333; padding: 20px 0;'>Raw Data</h2>", unsafe_allow_html=True)
                st.dataframe(filtered_data.style.highlight_max(axis=0, color='#E3F2FD').highlight_min(axis=0, color='#FFCDD2'))
            else:
                st.info("No data available. Please select players in the Matchup Analysis tab.")
        except Exception as e:
            st.error(f"An error occurred while displaying raw data: {str(e)}")


def main():
    bat_vs_bowl_matchup()
