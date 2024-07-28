import pandas as pd
import numpy as np
import streamlit as st


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
    
    st.markdown(
        """
        <h1 style='text-align: center; color: #FFFFFF;'>IPL Matchup Dashboard</h1>
        """,
        unsafe_allow_html=True
    )

    # st.title('IPL Matchup Dashboard')

    # weakness = pd.read_csv('.\\IPL_Data\\all_ipl_data.csv')

    weakness = get_matchups_data()

    # Get All Batters and Bowlers in a List
    batters_list = list(set(weakness.striker.to_list()))
    bowlers_list = list(set(weakness.bowler.to_list()))

    # Function to filter list based on search input
    def filter_list(search_term, items):
        return [item for item in items if search_term.lower() in item.lower()]

    # Input fields for batter and bowler names
    # batter_name = st.text_input('Enter batter name:', 'Kohli')
    # filtered_batters = filter_list(batter_name, batters_list)
    batter_select = st.selectbox('Select Batter:', batters_list, index=200)
    # bowler_name = st.text_input('Enter bowler name:', 'Bumrah')

    bowler_select = st.selectbox('Select Bowler:', bowlers_list, index=69)

    # Filter matchup data based on input names
    filtered_data = weakness[
        (weakness['striker'].str.contains(batter_select)) & (weakness['bowler'].str.contains(bowler_select))]

    # Filter only Required Columns
    filtered_data = filtered_data[['striker', 'bowler', 'innings', 'runs_scored', 'balls_faced',
                                   'dismissals', 'batting_SR', 'dot_percentage']]

    if not filtered_data.empty:
        st.markdown("<h1 style='text-align: center; color: yellow;'>Matchup Summary</h1>", unsafe_allow_html=True)
        # st.write("## " + filtered_data['striker'].iloc[0] + " vs " + filtered_data['bowler'].iloc[0])
        st.markdown(
            f"""
            <h3 style='text-align: center; color: #FFFFFF;'>{filtered_data['striker'].iloc[0]} vs {filtered_data['bowler'].iloc[0]}</h3>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")

        # Create columns for each box
        col1, col2 = st.columns(2)

        # Display each field in an enclosed box
        with col1:
            # st.info(f" Innings: \n ## **{filtered_data['innings'].iloc[0]}**")
            st.markdown(
                f"""
                <div style='background-color: #172D43; border-radius: 5px; padding: 10px; text-align: center;'>
                    <span style='color: #C7EBF3;'>Innings<br> <b style= 'font-size: 50px;'>{filtered_data['innings'].iloc[0]}</b></span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            # st.error(f"Dismissals:\n ## **{filtered_data['dismissals'].iloc[0]}**")
            st.markdown(
                f"""
                <div style='background-color: #3E2327; border-radius: 5px; padding: 10px; text-align: center;'>
                    <span style='color: #FFDEDE;'>Dismissals<br> <b style= 'font-size: 50px;'>{filtered_data['dismissals'].iloc[0]}</b></span>
                </div>
                <div style='padding-top: 15px;'></div>
                """,
                unsafe_allow_html=True
            )

        col3, col4 = st.columns(2)
        with col3:
            # st.success(f"Runs Scored: \n ## **{filtered_data['runs_scored'].iloc[0]}**")
            st.markdown(
                f"""
                <div style='background-color: #173928; border-radius: 5px; padding: 10px; text-align: center;'>
                    <span style='color: #D4EDDA;'>Runs Scored<br> <b style= 'font-size: 50px;'>{filtered_data['runs_scored'].iloc[0]}</b></span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col4:
            # st.warning(f'Balls Faced: \n ## **{filtered_data["balls_faced"].iloc[0]}**')
            st.markdown(
                f"""
                <div style='background-color: #3E3C15; border-radius: 5px; padding: 10px; text-align: center;'>
                    <span style='color: #FFFFBC;'>Balls Faced<br> <b style= 'font-size: 50px;'>{filtered_data["balls_faced"].iloc[0]}</b></span>
                </div>
                <div style='padding-top: 15px;'></div>
                """,
                unsafe_allow_html=True
            )
        col5, col6 = st.columns(2)
        with col5:
            # st.info(f"Batting Strike Rate:\n ## **{int(filtered_data['batting_SR'].iloc[0])}**")
            st.markdown(
                f"""
                        <div style='background-color: #282863; border-radius: 5px; padding: 10px; text-align: center;'>
                            <span style='color: #b6b6e3;'>Batting Strike Rate<br> <b style= 'font-size: 50px;'>{int(filtered_data['batting_SR'].iloc[0])}</b></span>
                        </div>
                        """,
                unsafe_allow_html=True
            )
        with col6:
            # st.success(f"Dot Percentage:\n ## **{int(filtered_data['dot_percentage'].iloc[0])}**")
            st.markdown(
                f"""
                <div style='background-color: #523117; border-radius: 5px; padding: 10px; text-align: center;'>
                    <span style='color: #e8d3c3;'>Dots Percentage<br> <b style= 'font-size: 50px;'>{int(filtered_data['dot_percentage'].iloc[0])}</b></span>
                </div>
                <div style='padding-top: 15px;'></div>
                """,
                unsafe_allow_html=True
            )


def main():
    bat_vs_bowl_matchup()


if __name__ == '__main__':
    main()