import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime


team_mapping = {
        "Mumbai Indians": {"short": "MI", "colors": ["#78a5ff", "#133b77"]},  # Brighter shade of blue
        "Royal Challengers Bengaluru": {"short": "RCB", "colors": ["#ff4d4d", "#2B2A29"]},  # Brighter shade of red
        "Royal Challengers Bangalore": {"short": "RCB", "colors": ["#ff4d4d", "#2B2A29"]},  # Brighter shade of red
        "Delhi Capitals": {"short": "DC", "colors": ["#6a7fff", "#B9251C"]},  # Brighter shade of blue
        "Delhi Daredevils": {"short": "DD", "colors": ["#6a7fff", "#B9251C"]},  # Brighter shade of blue
        "Chennai Super Kings": {"short": "CSK", "colors": ["#FFCB05", "#2478A7"]},  # No change
        "Gujarat Titans": {"short": "GT", "colors": ["#77C7F2", "#C0D3E4"]},  # No change
        "Punjab Kings": {"short": "PBKS", "colors": ["#f98181", "#753D51"]},  # Brighter shade of red
        "Kings XI Punjab": {"short": "KXIP", "colors": ["#f98181", "#753D51"]},  # Brighter shade of red
        "Lucknow Super Giants": {"short": "LSG", "colors": ["#1f7bff", "#77A4DC"]},  # Brighter shade of blue
        "Rajasthan Royals": {"short": "RR", "colors": ["#FF85A2", "#FFB2D9"]},  # Brighter shade of pink
        "Kolkata Knight Riders": {"short": "KKR", "colors": ["#7951db", "#7E72A8"]},  # No change
        "Sunrisers Hyderabad": {"short": "SRH", "colors": ["#ff8266", "#FFA94D"]},  # Brighter shade of orange
        "Rising Pune Supergiant": {"short": "RPS", "colors": ["#ff8266", "#FFA94D"]},  # Brighter shade of orange
        "Rising Pune Supergiants": {"short": "RPS", "colors": ["#ff8266", "#FFA94D"]},  # Brighter shade of orange
        "Pune Warrior": {"short": "PWI", "colors": ["#ff8266", "#FFA94D"]},  # Brighter shade of orange
        "Pune Warriors": {"short": "PWI", "colors": ["#ff8266", "#FFA94D"]},  # Brighter shade of orange
        "Deccan Chargers": {"short": "DC", "colors": ["#ff8266", "#FFA94D"]},  # Brighter shade of orange
        "Kochi Tuskers Kerala": {"short": "DC", "colors": ["#ff8266", "#FFA94D"]},  # Brighter shade of orange
        "Gujarat Lions": {"short": "GL", "colors": ["#77C7F2", "#C0D3E4"]},  # No change
    }



def feature_extraction(data):

    if data.empty:
        print("The DataFrame is empty")
        return None

    

    # Fill NA for wides, noballs, byes, legbyes

    data['wides'] = data['wides'].fillna(0).astype(int)
    data['noballs'] = data['noballs'].fillna(0).astype(int)
    data['byes'] = data['byes'].fillna(0).astype(int)
    data['legbyes'] = data['legbyes'].fillna(0).astype(int)


    data['legal_ball'] = data.apply(lambda row: 0 if (row['wides'] != 0) or (row['noballs'] != 0) else 1, axis=1)

    data['over_ball'] = pd.Series(dtype='float')

    data['over_ball'] = data['over_ball'].round(1)


    # Over_ball Column

    # for i in range(len(data)):


    #     if int(data.loc[i, 'ball']*10) - int(data.loc[i, 'ball'])*10 == 1:  # First Ball
    #         data.loc[i, 'over_ball'] = data.loc[i, 'ball']
    #     else:  # Not First Ball of Over
    #         if data.loc[i, 'legal_ball'] == 0:  # Check if Current Ball is Wide or No Ball
    #             if data.loc[i-1, 'legal_ball'] == 0:  # Check if Previous Ball was Wide or No Ball
    #                 data.loc[i, 'over_ball'] = data.loc[i-1, 'over_ball']
    #             else:  # Previous Ball was Legal
    #                 data.loc[i, 'over_ball'] = data.loc[i-1, 'over_ball'] + 0.1
    #         else:  # Legal Ball
    #             if data.loc[i-1, 'legal_ball'] == 0:  # Check if Previous Ball was Wide or No Ball
    #                 data.loc[i, 'over_ball'] = data.loc[i-1, 'over_ball']
    #             else:
    #                 data.loc[i, 'over_ball'] = data.loc[i-1, 'over_ball'] + 0.1


    data['prev_legal_ball'] = data['legal_ball'].shift(1)
    data['prev_over_ball'] = data['over_ball'].shift(1)

    # Calculate over_ball using vectorized operations
    data['is_first_ball'] = (data['ball'] * 10 % 10 == 1).astype(int)
    data['is_wide_or_no_ball'] = (data['legal_ball'] == 0).astype(int)
    data['prev_is_wide_or_no_ball'] = (data['prev_legal_ball'] == 0).astype(int)

    conditions = [
        data['is_first_ball'] == 1,
        (data['is_wide_or_no_ball'] == 1) & (data['prev_is_wide_or_no_ball'] == 1),
        (data['is_wide_or_no_ball'] == 1) & (data['prev_is_wide_or_no_ball'] == 0),
        (data['is_wide_or_no_ball'] == 0) & (data['prev_is_wide_or_no_ball'] == 1),
        (data['is_wide_or_no_ball'] == 0) & (data['prev_is_wide_or_no_ball'] == 0)
    ]

    choices = [
        data['ball'],
        data['prev_over_ball'],
        data['prev_over_ball'] + 0.1,
        data['prev_over_ball'],
        data['prev_over_ball'] + 0.1
    ]

    data['over_ball'] = np.select(conditions, choices, default=data['ball'])
    data['over_ball'] = data['over_ball'].fillna(data['ball']).round(1)

    # Clean up temporary columns
    data = data.drop(['is_first_ball', 'is_wide_or_no_ball', 'prev_is_wide_or_no_ball', 'prev_legal_ball', 'prev_over_ball'], axis=1)



    # Total Runs of Ball
    data['total_runs_off_ball'] = data['runs_off_bat'] + data['extras']
    data['total_runs_off_ball'] = data['runs_off_bat'] + data['extras']

    # Wicket Fallen
    data['wicket_fallen'] = data.apply(lambda x: 1 if pd.notna(x['player_dismissed']) else 0, axis=1)
    data['wicket_fallen'] = data.apply(lambda x: 1 if pd.notna(x['player_dismissed']) else 0, axis=1)

    # Add Dots, 1s, 2s, 3s, fours, sixes

    data['is_dot'] = data['total_runs_off_ball'].apply(lambda x: 1 if x == 0 else 0)
    data['is_one'] = data['total_runs_off_ball'].apply(lambda x: 1 if x == 1 else 0)
    data['is_two'] = data['total_runs_off_ball'].apply(lambda x: 1 if x == 2 else 0)
    data['is_three'] = data['total_runs_off_ball'].apply(lambda x: 1 if x == 3 else 0)
    data['is_four'] = data['total_runs_off_ball'].apply(lambda x: 1 if x == 4 else 0)
    data['is_six'] = data['total_runs_off_ball'].apply(lambda x: 1 if x == 6 else 0)


    # Add Overs and Ball Count

    data['overs'] = data['ball'].apply(lambda x: int(x))

    ball_count = data.groupby('innings')['ball'].cumcount() + 1

    data['ball_count'] = ball_count.values


    # Add Striker Final Score

    striker_total_runs =  data.groupby(['striker'])['runs_off_bat'].sum()

    data['striker_final_runs'] = data['striker'].map(striker_total_runs)

    data['is_wide'] = data['wides'].apply(lambda x: 1 if x > 0 else 0)


    # wides faced by striker

    wides_faced = data.groupby(data['striker'])['is_wide'].sum()

    data['striker_wides_faced'] = data['striker'].map(wides_faced)


    # striker total balls faced
    data['striker_total_balls_faced'] = data.groupby('striker')['ball'].transform('count')

    # striker legal balls faced
    data['striker_balls_faced'] = data['striker_total_balls_faced'] - data['striker_wides_faced']

    # striker strike rate
    data['striker_strike_rate'] = (data['striker_final_runs'] / data['striker_balls_faced']) * 100


    # strike final score
    data['striker_final_score'] = data.apply(lambda row: str(row['striker_final_runs']) + "(" + str(row['striker_balls_faced']) + ")", axis=1)


    # Create a set of players who were dismissed
    players_dismissed = set(data['player_dismissed'].dropna().unique())

    # Apply the function to the striker column and create a new column 'striker_status'
    data['striker_status'] = data['striker'].apply(lambda x: 'out' if x in players_dismissed else 'notout')

    
    # Add Striker dots, fours, sixes, strike rate

    striker_dots = data.groupby(['striker'])['is_dot'].sum()

    data['striker_dots'] = data['striker'].map(striker_dots)

    striker_fours = data.groupby(['striker'])['is_four'].sum()

    data['striker_fours'] = data['striker'].map(striker_fours)

    striker_sixes = data.groupby(['striker'])['is_six'].sum()

    data['striker_sixes'] = data['striker'].map(striker_sixes)


    # Calculate distinct overs bowled by each bowler
    distinct_overs_bowled = data.groupby('bowler')['over_ball'].nunique()

    # Map the number of balls bowled to the original DataFrame
    data['bowler_balls_bowled'] = data['bowler'].map(distinct_overs_bowled)

    # Convert the number of balls bowled to overs and balls
    data['bowler_overs_bowled'] = data['bowler_balls_bowled'].apply(lambda x: f"{x // 6}.{x % 6}")


    # Total Dots Bowled by Bowler

    bowler_total_dots = data.groupby(['bowler'])['is_dot'].sum()

    data['bowler_total_dots'] = data['bowler'].map(bowler_total_dots)

    # Add Bowler Final Figures

    data['total_runs_conceded'] = data['runs_off_bat'] + data['wides'] + data['noballs']

    bowler_total_runs = data.groupby(['bowler'])['total_runs_conceded'].sum()
    data['bowler_final_runs_conceded'] = data['bowler'].map(bowler_total_runs)

    bowler_total_wickets = data.groupby(['bowler'])['player_dismissed'].count()
    data['bowler_final_wickets'] = data['bowler'].map(bowler_total_wickets)

    data['bowler_final_figures'] = data.apply(lambda row: str(row['bowler_final_runs_conceded'])  + str("/") + str(row['bowler_final_wickets']), axis=1)


    # Bowler Final Economy
    try:
        data['bowler_final_economy'] = data.apply(lambda x: round( (x['bowler_final_runs_conceded'] / float(x['bowler_balls_bowled'])) * 6, 2), axis=1)
    except:
        data['bowler_final_economy'] = 0

    # Total Balls in Over
    data['over_number'] = data['over_ball'].apply(lambda x: int(x))

    total_balls = data.groupby(['innings','over_number'])['over_ball'].count()

    data['total_balls_in_over'] = data.apply(lambda x: total_balls.get((x['innings'], x['over_number']), 0), axis=1)

    # Get Maiden Over

    maiden_over = data.groupby(['innings','over_number'])['total_runs_off_ball'].sum()

    # Map the total runs of each over back to the DataFrame
    data['runs_off_over'] = data.apply(lambda x: maiden_over.get((x['innings'], x['over_number']), 0), axis=1)

    data['maiden_over'] = data.apply(lambda x: 1 if (x['runs_off_over'] == 0) and (x['total_balls_in_over'] == 6 ) else 0, axis=1)

    bowler_total_maidens = data.groupby(['bowler'])['maiden_over'].sum()

    data['bowler_total_maidens'] = data['bowler'].map(bowler_total_maidens)

    data['bowler_total_maidens'] = data['bowler_total_maidens'] // 6


    cum_runs = data.groupby('innings')['total_runs_off_ball'].cumsum()

    data['cum_runs'] = cum_runs.values

    cum_wickets = data.groupby('innings')['wicket_fallen'].cumsum()

    data['cum_wickets'] = cum_wickets.values

    batter = data[['striker', 'batting_team', 'striker_balls_faced', 'striker_dots', 'striker_fours', 'striker_sixes', 'striker_strike_rate', 'striker_final_runs', 'striker_final_score', 'striker_status']]

    batter = batter.drop_duplicates()

    batter = batter.sort_values(by=['striker_final_runs', 'striker_balls_faced'], ascending=[False, True])

    bowler = data[['bowler', 'bowling_team', 'bowler_balls_bowled', 'bowler_overs_bowled', 'bowler_total_dots', 'bowler_final_runs_conceded', 'bowler_total_maidens', 'bowler_final_economy', 'bowler_final_wickets']]

    bowler = bowler.drop_duplicates()

    bowler = bowler.sort_values(by=['bowler_final_wickets', 'bowler_final_economy'], ascending=[False, True])


    # Create ExcelWriter object
    # with pd.ExcelWriter('extracted_data.xlsx') as writer:
    #     # Write each DataFrame to a separate sheet
    #     data.to_excel(writer, sheet_name='Data', index=False)
    #     batter.to_excel(writer, sheet_name='Batter', index=False)
    #     bowler.to_excel(writer, sheet_name='Bowler', index=False)

    return data, batter, bowler


def get_progression_graph(data):
    # Split by Innings
    inning1 = data[data['innings'] == 1]
    inning2 = data[data['innings'] == 2]

    team1 = str(inning1['batting_team'].unique()[0])
    team2 = str(inning2['batting_team'].unique()[0])

    # Innings Scores

    team1_short_name = team_mapping[team1]['short']
    team2_short_name = team_mapping[team2]['short']

    team1_final_score = inning1['cum_runs'].iloc[-1]
    team2_final_score = inning2['cum_runs'].iloc[-1]

    team1_final_wickets = inning1['cum_wickets'].iloc[-1]
    team2_final_wickets = inning2['cum_wickets'].iloc[-1]


    inning1_overs = inning1['ball'].iloc[-1]
    inning2_overs = inning2['ball'].iloc[-1]

    inning1_label = f"{team1_short_name}: {team1_final_score}/{team1_final_wickets} in {inning1_overs}"
    inning2_label = f"{team2_short_name}: {team2_final_score}/{team2_final_wickets} in {inning2_overs}"

    # inning1_label, inning2_label -> ('SRH: 113/10 in 18.3', 'KKR: 114/2 in 10.3')

    # Winner

    if team1_final_score > team2_final_score:
        winner = team1
        win_by = f"{team1_final_score - team2_final_score} Runs"
    elif team1_final_score < team2_final_score:
        winner = team2
        win_by = f"{team1_final_wickets - team2_final_wickets} Wickets"
    else:
        winner = "Draw"

    # winner, win_by -> ('Kolkata Knight Riders', '8 Wickets')

    # Score Info

    inning1_score_info = inning1.apply(lambda row: f"{team1_short_name}: {row['cum_runs']}/{row['cum_wickets']} ({round(row['over_ball'], 1)})", axis=1)

    inning2_score_info = inning2.apply(lambda row: f"{team2_short_name}: {row['cum_runs']}/{row['cum_wickets']} ({round(row['over_ball'], 1)})", axis=1)


    # Add Figure

    fig = go.Figure()

    # Create Inning1 Progression Line

    fig.add_trace(go.Scatter(
        x=inning1['ball_count'],
        y=inning1['cum_runs'],
        name=inning1_label,
        line=dict(color=team_mapping[team1]['colors'][0], width=4),
        text=inning1_score_info,
        hoverinfo='text'
    ))

    # Plot Inning1 Wickets

    for i in range(len(inning1)):
        if inning1['wicket_fallen'].iloc[i] == 1:
            if inning1['player_dismissed'].iloc[i] == inning1['striker'].iloc[i]:
                wicket_info = f"""{team1_short_name}: {inning1['cum_runs'].iloc[i]}/{inning1['cum_wickets'].iloc[i]} ({round(inning1['over_ball'].iloc[i],1)})
                <br>{inning1['player_dismissed'].iloc[i]} {inning1['striker_final_score'].iloc[i]} """
            else:
                wicket_info = f"""{team1_short_name}: {inning1['cum_runs'].iloc[i]}/{inning1['cum_wickets'].iloc[i]} ({round(inning1['over_ball'].iloc[i],1)})
                <br>{inning1['player_dismissed'].iloc[i]} {inning1[inning1['striker'] == inning1['player_dismissed'].iloc[i]].iloc[-1]} """

            fig.add_trace(
                go.Scatter(
                    x=[inning1['ball_count'].iloc[i]],
                    y=[inning1['cum_runs'].iloc[i]],
                    mode='markers',
                    marker=dict(color=team_mapping[team2]['colors'][1], size=10),
                    text=wicket_info,
                    hoverinfo='text',
                    name=wicket_info
                )
            )


    # Create Inning2 Progression Line

    fig.add_trace(go.Scatter(
        x=inning2['ball_count'],
        y=inning2['cum_runs'],
        name=inning2_label,
        line=dict(color=team_mapping[team2]['colors'][0], width=4),
        text=inning2_score_info,
        hoverinfo='text'
    ))

    # Plot Inning2 Wickets

    for i in range(len(inning2)):
        if inning2['wicket_fallen'].iloc[i] == 1:
            if inning2['player_dismissed'].iloc[i] == inning2['striker'].iloc[i]:
                wicket_info = f"""{team2_short_name}: {inning2['cum_runs'].iloc[i]}/{inning2['cum_wickets'].iloc[i]} ({round(inning2['over_ball'].iloc[i],1)})
                <br>{inning2['player_dismissed'].iloc[i]} {inning2['striker_final_score'].iloc[i]} """
            else:
                wicket_info = f"""{team2_short_name}: {inning2['cum_runs'].iloc[i]}/{inning2['cum_wickets'].iloc[i]} ({round(inning2['over_ball'].iloc[i],1)})
                <br>{inning2['player_dismissed'].iloc[i]} {inning2['non_striker_final_score'].iloc[i]} """

            fig.add_trace(
                go.Scatter(
                    x=[inning2['ball_count'].iloc[i]],
                    y=[inning2['cum_runs'].iloc[i]],
                    mode='markers',
                    marker=dict(color=team_mapping[team1]['colors'][1], size=10),
                    text=wicket_info,
                    hoverinfo='text',
                    name=wicket_info
                )
            )


    # Additional

    
    inning1_powerplay_score = None
    inning1_middle_overs_score = None
    inning1_death_overs_score = None



    # for i in range(len(inning1)):
    #     current_over = round(inning1.loc[i, 'over_ball'], 1)
    #     if current_over == 5.6:
    #         inning1_powerplay_score = f"{team1_short_name}: {inning1.loc[i, 'cum_runs']}/{inning1.loc[i, 'cum_wickets']}"


    # for i in range(len(inning1)):
    #     current_over = round(inning1.loc[i, 'over_ball'], 1)
    #     if current_over == 14.6:
    #         inning1_middle_overs_score = f"{team1_short_name}: {inning1.loc[i, 'cum_runs']}/{inning1.loc[i, 'cum_wickets']}"

    powerplay_end = inning1[inning1['over_ball'].round(1) == 5.6]
    if not powerplay_end.empty:
        inning1_powerplay_score = f"{team1_short_name}: {powerplay_end['cum_runs'].iloc[0]}/{powerplay_end['cum_wickets'].iloc[0]}"
    else:
        inning1_powerplay_score = f"{team1_short_name}: N/A"

    # For middle overs score (end of 15th over)
    middle_overs_end = inning1[inning1['over_ball'].round(1) == 14.6]
    if not middle_overs_end.empty:
        inning1_middle_overs_score = f"{team1_short_name}: {middle_overs_end['cum_runs'].iloc[0]}/{middle_overs_end['cum_wickets'].iloc[0]}"
    else:
        inning1_middle_overs_score = f"{team1_short_name}: N/A"


    if inning1_middle_overs_score is None and len(inning1) > 0:
        inning1_middle_overs_score = f"{team1_short_name}: {inning1['cum_runs'].iloc[-1]}/{inning1['cum_wickets'].iloc[-1]}"

    if len(inning1) > 0:
        inning1_death_overs_score =  f"{team1_short_name}: {inning1['cum_runs'].iloc[-1]}/{inning1['cum_wickets'].iloc[-1]}"



    i = 0

    # Inning2 Powerplay, Middle Overs, Death Overs Score

    inning2_powerplay_score = None
    inning2_middle_overs_score = None
    inning2_death_overs_score = None

    # Use iloc to access rows by position instead of label-based loc
    for i in range(len(inning2)):
        current_over = round(inning2.iloc[i]['over_ball'], 1)  # Use iloc to access by position
        if current_over == 5.6:
            inning2_powerplay_score = f"{team2_short_name}: {inning2.iloc[i]['cum_runs']}/{inning2.iloc[i]['cum_wickets']}"

    for i in range(len(inning2)):
        current_over = round(inning2.iloc[i]['over_ball'], 1)  # Use iloc to access by position
        if current_over == 14.6:
            inning2_middle_overs_score = f"{team2_short_name}: {inning2.iloc[i]['cum_runs']}/{inning2.iloc[i]['cum_wickets']}"

    if inning2_middle_overs_score is None and len(inning2) > 0:
        inning2_middle_overs_score = f"{team2_short_name}: {inning2['cum_runs'].iloc[-1]}/{inning2['cum_wickets'].iloc[-1]}"

    if len(inning2) > 0:
        inning2_death_overs_score =  f"{team2_short_name}: {inning2['cum_runs'].iloc[-1]}/{inning2['cum_wickets'].iloc[-1]}"


    # Add powerplay annotation
    fig.add_annotation(x=18, y=0, text=f"Powerplay",
                    showarrow=False, font=dict(color="white", size=12))

    fig.add_annotation(x=18, y=125, text=f"{inning1_powerplay_score}<br>{inning2_powerplay_score}",
                    showarrow=False, font=dict(color="white", size=16))

    # Add middle overs annotation
    fig.add_annotation(x=70, y=0, text="Middle Overs",
                    showarrow=False, font=dict(color="white", size=12))

    fig.add_annotation(x=70, y=125, text=f"{inning1_middle_overs_score}<br>{inning2_middle_overs_score}",
                    showarrow=False, font=dict(color="white", size=16))


    # Add death overs annotation
    fig.add_annotation(x=110, y= 0, text="Death Overs",
                    showarrow=False, font=dict(color="white", size=12))

    fig.add_annotation(x=110, y=125, text=f"{inning1_death_overs_score}<br>{inning2_death_overs_score}",
                    showarrow=False, font=dict(color="white", size=16))


    # Add layout
    fig.update_layout(
        title={
            'text': f'{team1} vs {team2} : Innings Summary<br>{winner} Won By {win_by}',
            'x': 0.4,
            'font': {
                'size': 24  # Increase title font size
            }
        },
        xaxis_title='Balls',
        yaxis_title='Runs',
        plot_bgcolor='#313131',
        paper_bgcolor='#393939',
        font=dict(color="white"),
        legend=dict(font=dict(color="white"))
    )


    return fig


def get_top_batters(batter):
    # Top 4 Batsman
    colors = [team_mapping[team]['colors'][0] for team in batter['batting_team']]

    fig1 = go.Figure(go.Bar(
        x=batter['striker_final_runs'].head(4),
        y=batter['striker'].head(4),
        orientation='h',
        marker=dict(color=colors),
        text=batter['striker_final_runs'],
        hovertext=batter['striker_strike_rate'].apply(lambda x: f"Strike Rate: {int(x)}"),
        hoverinfo='text'
    ))

    fig1.update_layout(
        title=f'Top 4 Batsmen',
        xaxis_title='Final Runs',
        yaxis_title='Batsman',
        yaxis=dict(autorange='reversed')
    )

    return fig1


def get_top_bowlers(bowler):
    
    # Top 4 Bowler
    colors = [team_mapping[team]['colors'][0] for team in bowler['bowling_team']]

    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=bowler['bowler_final_wickets'].head(4),
        y=bowler['bowler'].head(4),
        orientation='h',
        marker=dict(color=colors),
        text=bowler['bowler_final_wickets'],
        hovertext=bowler['bowler_final_economy'].apply(lambda x: f"Economy: {x}"),
        hoverinfo='text'
    ))

    fig2.update_layout(
        title=f'Top 4 Bowlers',
        xaxis_title='Final Wickets',
        yaxis_title='Bowler',
        yaxis=dict(autorange='reversed')
    )

    return fig2



def main():

    st.set_page_config(
        layout="wide"
    )


    all_ipl_data = pd.read_csv('IPL_Data\\raw_ipl_data.csv')

    match_ids = list(all_ipl_data.match_id.unique())

    matches_list = {}

    for match_id in match_ids:
        match = all_ipl_data[all_ipl_data['match_id'] == match_id]

        season = match.iloc[0]['season']
        start_date = match.iloc[0]['start_date']

        # Parse the date string to a datetime object
        date_obj = datetime.strptime(start_date, "%Y-%m-%d")

        # Format the datetime object to the desired format
        formatted_date = date_obj.strftime("%d %b")

        batting_team = match.iloc[0]['batting_team']
        bowling_team = match.iloc[0]['bowling_team']

        team1 = team_mapping[batting_team]['short']

        team2 = team_mapping[bowling_team]['short']

        filter_string = f"{team1} vs {team2} {formatted_date} {season}"
        
        matches_list[filter_string] = match_id


    matches_names = list(matches_list.keys())

    select_match = st.selectbox('Select Match:', matches_names, index=2)

    match_id = matches_list[select_match]

    match_data = all_ipl_data[all_ipl_data['match_id'] == match_id]

    # print(match_data)

    data, batter, bowler = feature_extraction(match_data)

    progression_graph = get_progression_graph(data)

    top_batters = get_top_batters(batter)

    top_bowlers = get_top_bowlers(bowler)

    

    st.title("Cricket Match Visualization")

    

    # Display the progression graph
    st.subheader("Match Progression")
    progression_graph.update_layout(height=800)
    st.plotly_chart(progression_graph, use_container_width=True, height=800)

    # Create two columns for batters and bowlers
    col1, col2 = st.columns(2)

    # Display the top batters graph in the first column
    with col1:
        st.subheader("Top Batters")
        st.plotly_chart(top_batters, use_container_width=True)

    # Display the top bowlers graph in the second column
    with col2:
        st.subheader("Top Bowlers")
        st.plotly_chart(top_bowlers, use_container_width=True)


if __name__ == '__main__':
    main()