import time
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import decimal
from plotly.subplots import make_subplots

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

    def round_overs(overs):
        if isinstance(overs, str):
            full_overs, partial_overs = map(int, overs.split('.'))
        else:
            decimal_overs = decimal.Decimal(str(overs))
            full_overs = int(decimal_overs)
            partial_overs = int((decimal_overs - full_overs) * 10)

        if full_overs >= 20:
            return 20
        elif partial_overs >= 6:
            return full_overs + 1
        else:
            return f'{full_overs}.{partial_overs}'
    inning1_overs = round_overs(inning1['ball'].iloc[-1])
    inning2_overs = round_overs(inning2['ball'].iloc[-1])

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
            try:
                if inning1['player_dismissed'].iloc[i] == inning1['striker'].iloc[i]:
                    wicket_info = f"""{team1_short_name}: {inning1['cum_runs'].iloc[i]}/{inning1['cum_wickets'].iloc[i]} ({round(inning1['over_ball'].iloc[i],1)})
                    <br>{inning1['player_dismissed'].iloc[i]} {inning1['striker_final_score'].iloc[i]} """
                else:
                    wicket_info = f"""{team1_short_name}: {inning1['cum_runs'].iloc[i]}/{inning1['cum_wickets'].iloc[i]} ({round(inning1['over_ball'].iloc[i],1)})
                    <br>{inning1['player_dismissed'].iloc[i]} {inning1['non_striker_final_score'].iloc[i]} """
            except:
                wicket_info="NA"

            fig.add_trace(
                go.Scatter(
                    x=[inning1['ball_count'].iloc[i]],
                    y=[inning1['cum_runs'].iloc[i]],
                    mode='markers',
                    marker=dict(
                        color=team_mapping[team2]['colors'][1],
                        size=10,
                        line=dict(
                            color='white',  # Border color
                            width=1       # Border width
                        )
                    ),
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
            try:
                if inning2['player_dismissed'].iloc[i] == inning2['striker'].iloc[i]:
                    wicket_info = f"""{team2_short_name}: {inning2['cum_runs'].iloc[i]}/{inning2['cum_wickets'].iloc[i]} ({round(inning2['over_ball'].iloc[i],1)})
                    <br>{inning2['player_dismissed'].iloc[i]} {inning2['striker_final_score'].iloc[i]} """
                else:
                    wicket_info = f"""{team2_short_name}: {inning2['cum_runs'].iloc[i]}/{inning2['cum_wickets'].iloc[i]} ({round(inning2['over_ball'].iloc[i],1)})
                    <br>{inning2['player_dismissed'].iloc[i]} {inning2['non_striker_final_score'].iloc[i]} """
            except:
                wicket_info = "NA"

            fig.add_trace(
                go.Scatter(
                    x=[inning2['ball_count'].iloc[i]],
                    y=[inning2['cum_runs'].iloc[i]],
                    mode='markers',
                    marker=dict(
                        color=team_mapping[team1]['colors'][1],  # Marker color
                        size=10,  # Marker size
                        line=dict(
                            color='white',  # Border color
                            width=1       # Border width
                        )
                    ),
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


    # Max Score
    max_score = max(inning2['cum_runs'].iloc[-1], inning1['cum_runs'].iloc[-1])

    # Add powerplay annotation
    fig.add_annotation(x=18, y=0, text=f"Powerplay",
                    showarrow=False, font=dict(color="white", size=12))

    fig.add_annotation(x=18, y=max_score + 5, text=f"{inning1_powerplay_score}<br>{inning2_powerplay_score}",
                    showarrow=False, font=dict(color="white", size=16))

    # Add middle overs annotation
    fig.add_annotation(x=70, y=0, text="Middle Overs",
                    showarrow=False, font=dict(color="white", size=12))

    fig.add_annotation(x=70, y=max_score + 5, text=f"{inning1_middle_overs_score}<br>{inning2_middle_overs_score}",
                    showarrow=False, font=dict(color="white", size=16))


    # Add death overs annotation
    fig.add_annotation(x=110, y= 0, text="Death Overs",
                    showarrow=False, font=dict(color="white", size=12))

    fig.add_annotation(x=110, y=max_score + 5, text=f"{inning1_death_overs_score}<br>{inning2_death_overs_score}",
                    showarrow=False, font=dict(color="white", size=16))



    try:
        # Update layout without the Innings Summary in the title
        fig.update_layout(
            title={
                'text': f'{team1} vs {team2}',
                'x': 0.25,
                'font': {
                    'size': 24
                }
            },
            xaxis_title='Balls',
            yaxis_title='Runs',
            plot_bgcolor='#313131',
            paper_bgcolor='#393939',
            font=dict(color="white"),
            legend=dict(font=dict(color="white"))
        )
    except:
        # Super Over case
        fig.update_layout(
            title={
                'text': f'{team1} vs {team2}',
                'x': 0.5,
                'font': {
                    'size': 24
                }
            },
            xaxis_title='Balls',
            yaxis_title='Runs',
            plot_bgcolor='#313131',
            paper_bgcolor='#393939',
            font=dict(color="white"),
            legend=dict(font=dict(color="white"))
        )

    return fig, winner, win_by, inning1_label, inning2_label


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

def calculate_win_percentages(data, team_mapping):
    inning1 = data[data['innings'] == 1]
    inning2 = data[data['innings'] == 2]

    team1 = str(inning1['batting_team'].unique()[0])
    team2 = str(inning2['batting_team'].unique()[0])

    team1_short_name = team_mapping[team1]['short']
    team2_short_name = team_mapping[team2]['short']

    t1_outcomes = data[data.batting_team == team1].total_runs_off_ball.value_counts()
    t2_outcomes = data[data.batting_team == team2].total_runs_off_ball.value_counts()

    t1_outs = data[data.batting_team == team1].wicket_fallen.sum()
    t2_outs = data[data.batting_team == team2].wicket_fallen.sum()

    outcomes = [0, 1, 2, 3, 4, 6, 'w']

    t1_outcomes_count = []
    for outcome in outcomes:
        try:
            if outcome != 'w':
                t1_outcomes_count.append(t1_outcomes[outcome])
            else:
                t1_outcomes_count.append(t1_outs)
        except:
            t1_outcomes_count.append(0)
            
    t2_outcomes_count = []
    for outcome in outcomes:
        try:
            if outcome != 'w':
                t2_outcomes_count.append(t2_outcomes[outcome])
            else:
                t2_outcomes_count.append(t2_outs)
        except:
            t2_outcomes_count.append(0)

    t1_pb = [i/sum(t1_outcomes_count) for i in t1_outcomes_count]
    t2_pb = [i/sum(t2_outcomes_count) for i in t2_outcomes_count]

    t1_cum_pb = list(np.cumsum(t1_pb))
    t2_cum_pb = list(np.cumsum(t2_pb))

    win_count_ls, tie_count_ls, lose_count_ls = [], [], []

    for i in range(len(data)):
        win_count, tie_count, lose_count = 0, 0, 0
        for _ in range(100):
            if data['innings'].iloc[i] == 1:
                ing1_prediction = innings_1_runs(data['over_ball'].iloc[i], data['cum_runs'].iloc[i], data['cum_wickets'].iloc[i], t1_cum_pb)
                target = ing1_prediction
                ing2_prediction = innings_2_runs(0, 0, 0, target, t2_cum_pb)
            else:
                target = inning1['cum_runs'].iloc[-1]
                ing2_prediction = innings_2_runs(data['over_ball'].iloc[i], data['cum_runs'].iloc[i], data['cum_wickets'].iloc[i], target, t2_cum_pb)

            if ing2_prediction > target:
                win_count += 1
            elif ing2_prediction == target:
                tie_count += 1
            else:
                lose_count += 1
                
        win_count_ls.append(win_count)
        tie_count_ls.append(tie_count)
        lose_count_ls.append(lose_count)

    return {
        "win_count_ls": win_count_ls,
        "tie_count_ls": tie_count_ls,
        "lose_count_ls": lose_count_ls,
        "team1": team1,
        "team2": team2,
        "team1_short_name": team1_short_name,
        "team2_short_name": team2_short_name
    }

def innings_1_runs(curr_overs, curr_score, curr_wickets, t1_cum_pb):
    i1p_0, i1p_1, i1p_2, i1p_3, i1p_4, i1p_6, i1p_w = t1_cum_pb

    pred_runs = curr_score
    pred_wks = curr_wickets
    
    over_ball = curr_overs
    over_number = int(str(over_ball).split('.')[0])
    ball_number = int(str(over_ball).split('.')[1])
    
    if ball_number >= 6:
        ball_number = 6
    current_balls = over_number*6 + ball_number 
    leftover_balls = 120 - current_balls

    for _ in range(leftover_balls):
        r_value = np.random.random()

        if r_value <= i1p_0:
            pred_runs += 0
        elif r_value <= i1p_1:
            pred_runs += 1
        elif r_value <= i1p_2:
            pred_runs += 2
        elif r_value <= i1p_3:
            pred_runs += 3
        elif r_value <= i1p_4:
            pred_runs += 4
        elif r_value <= i1p_6:
            pred_runs += 6
        else:
            pred_runs += 0
            pred_wks += 1
            if pred_wks == 10:
                break

    return pred_runs

def innings_2_runs(curr_overs, curr_score, curr_wickets, target, t2_cum_pb):
    i2p_0, i2p_1, i2p_2, i2p_3, i2p_4, i2p_6, i2p_w = t2_cum_pb

    pred_runs = curr_score
    pred_wks = curr_wickets
    
    # over_ball = curr_overs
    # over_number = int(str(over_ball).split('.')[0])
    # ball_number = int(str(over_ball).split('.')[1])
    
    # if ball_number >= 6:
    #     ball_number = 6
    # current_balls = over_number*6 + ball_number 
    # leftover_balls = 120 - current_balls

    # calculate leftover balls
    over_ball = curr_overs
    over_parts = str(over_ball).split('.')
    over_number = int(over_parts[0])
    
    if len(over_parts) > 1:
        ball_number = int(over_parts[1])
    else:
        ball_number = 0

    if ball_number >= 6:
        ball_number = 0
        over_number += 1
    
    current_balls = over_number * 6 + ball_number 
    leftover_balls = 120 - current_balls

    for _ in range(leftover_balls):
        r_value = np.random.random()

        if r_value <= i2p_0:
            pred_runs += 0
        elif r_value <= i2p_1:
            pred_runs += 1
        elif r_value <= i2p_2:
            pred_runs += 2
        elif r_value <= i2p_3:
            pred_runs += 3
        elif r_value <= i2p_4:
            pred_runs += 4
        elif r_value <= i2p_6:
            pred_runs += 6
        else:
            pred_runs += 0
            pred_wks += 1
            if pred_wks == 10:
                break
        
        if pred_runs > target:
            break

    return pred_runs

def plot_win_percentage(win_count_ls, tie_count_ls, lose_count_ls, team1, team2, team1_short_name, team2_short_name, team_mapping):
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    fig.add_trace(
        go.Scatter(
            x=list(range(len(win_count_ls))), 
            y=win_count_ls, 
            name=team2, 
            line=dict(color=team_mapping[team2]['colors'][0], shape='spline'))
    )
    fig.add_trace(
        go.Scatter(
            x=list(range(len(tie_count_ls))), 
            y=tie_count_ls, 
            name='Tie Value', 
            line=dict(color='grey', shape='spline'))
    )
    fig.add_trace(
        go.Scatter(
            x=list(range(len(lose_count_ls))), 
            y=lose_count_ls, 
            name=team1, 
            line=dict(color=team_mapping[team1]['colors'][0], shape='spline'))
    )

    fig.update_layout(
        title='Win Percentage Chart: ' + team1_short_name + ' vs ' + team2_short_name,
        xaxis_title="Ball No",
        yaxis_title="Win %",
        legend_title="Teams",
        font=dict(size=12),
        hovermode="x unified",
        yaxis=dict(range=[0, 100], tickvals=[0, 25, 50, 75, 100])
    )

    return fig

def main():
    # st.set_page_config(layout="wide", page_title="IPL Match Analysis")

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .streamlit-header {
            font-size: 2.5rem;
            color: #0e1117;
            text-align: center;
            padding: 1rem 0;
            background-color: #E6E6FA;
            border-radius: 5px;
            margin-bottom: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 3rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0 20px;
            background-color: #E6E6FA;
            border-radius: 5px;
            color: #0e1117;
            font-size: 18px;
            font-weight: bold;
            min-width: 150px;
            justify-content: center;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #D8BFD8;
            color: #0e1117;
        }

        .stTabs [aria-selected="true"] {
            background-color: #9370DB !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="streamlit-header">IPL Match Analysis Dashboard</h1>', unsafe_allow_html=True)

    # Load data
    all_ipl_data = pd.read_csv('IPL_Data/raw_ipl_data.csv')

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        seasons = sorted(all_ipl_data['season'].unique())
        selected_season = st.selectbox('Select Season:', seasons, index=len(seasons)-1)

    season_data = all_ipl_data[all_ipl_data['season'] == selected_season]
    match_ids = list(season_data.match_id.unique())

    matches_list = {}
    for match_id in match_ids:
        match = season_data[season_data['match_id'] == match_id]
        start_date = match.iloc[0]['start_date']
        date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d %b")
        batting_team = match.iloc[0]['batting_team']
        bowling_team = match.iloc[0]['bowling_team']
        team1 = team_mapping[batting_team]['short']
        team2 = team_mapping[bowling_team]['short']
        filter_string = f"{team1} vs {team2} {formatted_date}"
        matches_list[filter_string] = match_id

    with col2:
        select_match = st.selectbox('Select Match:', list(matches_list.keys()))

    match_id = matches_list[select_match]
    match_data = all_ipl_data[all_ipl_data['match_id'] == match_id]
    data, batter, bowler = feature_extraction(match_data)

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Match Summary", "Player Performance", "Venue Details and Data"])

    with tab1:
        progression_graph, winner, win_by, inning1_label, inning2_label = get_progression_graph(data)
        
        # Display the innings summary with better formatting
        st.markdown(f"""
        <div style='background-color: #E6E6FA; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
            <h2 style='text-align: center; color: #1e1e1e;'>Innings Summary</h2>
            <p style='text-align: center; font-size: 18px; color: #1e1e1e;'>
                {inning1_label}<br>
                {inning2_label}<br>
                <strong>{winner} Won By {win_by}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display the graph
        st.plotly_chart(progression_graph, use_container_width=True, height=800)

        # # Add the win percentage chart
        # # Update the win percentage calculation
        # win_percentage_result = calculate_win_percentages(data, team_mapping)
        
        # win_count_ls = win_percentage_result["win_count_ls"]
        # tie_count_ls = win_percentage_result["tie_count_ls"]
        # lose_count_ls = win_percentage_result["lose_count_ls"]
        # team1 = win_percentage_result["team1"]
        # team2 = win_percentage_result["team2"]
        # team1_short_name = win_percentage_result["team1_short_name"]
        # team2_short_name = win_percentage_result["team2_short_name"]
        
        # win_percentage_chart = plot_win_percentage(win_count_ls, tie_count_ls, lose_count_ls, team1, team2, team1_short_name, team2_short_name, team_mapping)
        # st.plotly_chart(win_percentage_chart, use_container_width=True, height=600)

        # Update the win percentage calculation
        win_percentage_result = calculate_win_percentages(data, team_mapping)
        
        win_count_ls = win_percentage_result["win_count_ls"]
        tie_count_ls = win_percentage_result["tie_count_ls"]
        lose_count_ls = win_percentage_result["lose_count_ls"]
        team1 = win_percentage_result["team1"]
        team2 = win_percentage_result["team2"]
        team1_short_name = win_percentage_result["team1_short_name"]
        team2_short_name = win_percentage_result["team2_short_name"]
        
        win_percentage_chart = plot_win_percentage(win_count_ls, tie_count_ls, lose_count_ls, team1, team2, team1_short_name, team2_short_name, team_mapping)
        st.plotly_chart(win_percentage_chart, use_container_width=True, height=600)

        # Key Stats
        col1, col2, col3, = st.columns(3)
        with col1:
            st.metric("Total Sixes", data['is_six'].sum())
        with col2:
            st.metric("Total Fours", data['is_four'].sum())
        with col3:
            st.metric("Extras", data['extras'].sum())
        
        st.metric("Highest Individual Score", f"{batter['striker_final_runs'].max()} ({batter.loc[batter['striker_final_runs'].idxmax(), 'striker']})")
        st.metric("Best Bowling Figures", f"{bowler['bowler_final_wickets'].max()}/{bowler.loc[bowler['bowler_final_wickets'].idxmax(), 'bowler_final_runs_conceded']} ({bowler.loc[bowler['bowler_final_wickets'].idxmax(), 'bowler']})")

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top Batters")
            top_batters = get_top_batters(batter)
            st.plotly_chart(top_batters, use_container_width=True)

        with col2:
            st.subheader("Top Bowlers")
            top_bowlers = get_top_bowlers(bowler)
            st.plotly_chart(top_bowlers, use_container_width=True)

        # New visualization: Run distribution pie chart
        st.subheader("Run Distribution of Whole Innings")
        run_distribution = go.Figure(data=[go.Pie(
            labels=['Ones', 'Twos', 'Threes', 'Fours', 'Sixes', 'Extras'],
            values=[data['is_one'].sum(), data['is_two'].sum()*2, data['is_three'].sum()*3, 
                    data['is_four'].sum()*4, data['is_six'].sum()*6, data['extras'].sum()],
            hole=.3
        )])
        run_distribution.update_layout(height=400)
        st.plotly_chart(run_distribution, use_container_width=True)

    with tab3:
        st.markdown('<h2 class="streamlit-header">Detailed Stats</h2>', unsafe_allow_html=True)
        if st.checkbox("Show raw data"):
            st.dataframe(data)
        with st.expander("Match Details", expanded=True):
            st.write(f"Date: {match_data['start_date'].iloc[0]}")
            st.write(f"Venue: {match_data['venue'].iloc[0]}")
            
            # Check if 'city' column exists before trying to access it
            if 'city' in match_data.columns:
                st.write(f"City: {match_data['city'].iloc[0]}")
            
            # Check if 'toss_winner' and 'toss_decision' columns exist
            if 'toss_winner' in match_data.columns and 'toss_decision' in match_data.columns:
                st.write(f"Toss Winner: {match_data['toss_winner'].iloc[0]}")
                st.write(f"Toss Decision: {match_data['toss_decision'].iloc[0]}")
            
            # Add more details that are available in your dataset
            # For example:
            if 'winner' in match_data.columns:
                st.write(f"Match Winner: {match_data['winner'].iloc[0]}")
            
            if 'player_of_match' in match_data.columns:
                st.write(f"Player of the Match: {match_data['player_of_match'].iloc[0]}")

    st.sidebar.markdown("""
    <h2>UpComing Features in Match Analyzer:</h2>
    <div id="blinking-content">
        <p>• Match Rating</p>
        <p>• Match Winning Percentage</p>
    </div>
    <style>
        @keyframes blink {
            50% { opacity: 0; }
        }
        #blinking-content {
            animation: blink 1s linear infinite;
        }
    </style>
    """, unsafe_allow_html=True)

    # Add a placeholder for the script
    script_placeholder = st.sidebar.empty()

    # Wait for 10 seconds
    time.sleep(10)

    # After 10 seconds, update the content to remove the animation
    script_placeholder.markdown("""
        <style>
            #blinking-content {
                animation: none;
                opacity: 1;
            }
        </style>
        """, unsafe_allow_html=True)
