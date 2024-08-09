import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

data = pd.read_csv("IPL_Data/raw_ipl_data.csv")


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


data['total_runs'] = data.apply(lambda x: x['runs_off_bat'] + x['extras'], axis = 1)

data['isOut'] = data['player_dismissed'].apply(lambda x: 1 if type(x) == type('str') else 0)


match_id = 1254058

match_data = data[data['match_id'] == match_id]

inning1 = match_data[match_data['innings'] == 1]
inning2 = match_data[match_data['innings'] == 2]

team1 = str(inning1['batting_team'].unique()[0])
team2 = str(inning2['batting_team'].unique()[0])

team1_short_name = team_mapping[team1]['short']
team2_short_name = team_mapping[team2]['short']

# Wickets fallen in ALL IPL Seasons
t1_outs = data[data.batting_team == team1].isOut.sum()
t2_outs = data[data.batting_team == team2].isOut.sum()

# Scores on each ball in ALL IPL Seasons
t1_outcomes = data[data.batting_team == team1].total_runs.value_counts()
t2_outcomes = data[data.batting_team == team2].total_runs.value_counts()

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


# Probability of Outcomes
t1_pb = [i/sum(t1_outcomes_count) for i in t1_outcomes_count]
t2_pb = [i/sum(t2_outcomes_count) for i in t2_outcomes_count]

t1_cum_pb = list(np.cumsum(t1_pb))
t2_cum_pb = list(np.cumsum(t2_pb))


# first innings
def innings_1_runs(curr_overs, curr_score, curr_wickets):
    i1p_0 = t1_cum_pb[0]
    i1p_1 = t1_cum_pb[1]
    i1p_2 = t1_cum_pb[2]
    i1p_3 = t1_cum_pb[3]
    i1p_4 = t1_cum_pb[4]
    i1p_6 = t1_cum_pb[5]
    i1p_w = 1

    # initialize runs, wickets
    pred_runs = curr_score
    pred_wks = curr_wickets
    
    # calculate leftover balls
    over_ball = curr_overs
    over_number = int(str(over_ball).split('.')[0])
    ball_number = int(str(over_ball).split('.')[1])
    
    if ball_number >= 6:
        ball_number = 6
    current_balls = over_number*6 + ball_number 
    leftover_balls = 120 - current_balls

    for i in range(leftover_balls):
    
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

# second innings
def innings_2_runs(curr_overs, curr_score, curr_wickets, target):

    i2p_0 = t2_cum_pb[0]
    i2p_1 = t2_cum_pb[1]
    i2p_2 = t2_cum_pb[2]
    i2p_3 = t2_cum_pb[3]
    i2p_4 = t2_cum_pb[4]
    i2p_6 = t2_cum_pb[5]
    i2p_w = 1

    # initialize runs, wickets
    pred_runs = curr_score
    pred_wks = curr_wickets
    
    # calculate leftover balls
    over_ball = curr_overs
    over_number = int(str(over_ball).split('.')[0])
    ball_number = int(str(over_ball).split('.')[1])
    
    if ball_number >= 6:
        ball_number = 6
    current_balls = over_number*6 + ball_number 
    leftover_balls = 120 - current_balls

    for i in range(leftover_balls):
    
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

df_ing1 = match_data[match_data.innings == 1]
df_ing2 = match_data[match_data.innings == 2]

df_ing1 = df_ing1.sort_values('ball', ascending = True)
df_ing2 = df_ing2.sort_values('ball', ascending = True)


df_ing1.reset_index(inplace = True, drop = True)
df_ing2.reset_index(inplace = True, drop = True)


# Win Prediction Chart

# 1st Innings

# 1, 2 innings & predict win 

# for each ball make a prediction: 1st runs, 2nd runs, win/lose/tie

# initialize win/tie/lose
win_count = 0
tie_count = 0
lose_count = 0

win_count_ls = []
tie_count_ls = []
lose_count_ls = []

ing1_curr_score = 0
ing1_curr_overs = 0
ing1_curr_wickets = 0


i=0
j=0
# each ball
for i in range(len(df_ing1)):
    
    # 1st innings values
    ing1_curr_score += df_ing1.total_runs[i]
    ing1_curr_overs = df_ing1.ball[i]
    ing1_curr_wickets += df_ing1.isOut[i]
    
    #2nd innings values
    ing2_curr_score = 0
    ing2_curr_wickets = 0
    ing2_curr_overs = 0.0
    
    # make a prediction for 100 times & get win/lose/tie count(ex: 28% win)
    for j in range(100):
        
        ing1_prediction = innings_1_runs(ing1_curr_overs, ing1_curr_score, ing1_curr_wickets)
        target = ing1_prediction
        
        ing2_prediction = innings_2_runs(ing2_curr_overs, ing2_curr_score, ing2_curr_wickets, target)
        
#         print(ing1_prediction, ing2_prediction)
        
        # prediction w.r.t 2nd team
        if ing2_prediction > target:
            win_count += 1
        elif ing2_prediction == target:
            tie_count += 1
        else:
            lose_count += 1
            
    win_count_ls.append(win_count)
    tie_count_ls.append(tie_count)
    lose_count_ls.append(lose_count)
    
    win_count = 0
    tie_count = 0
    lose_count = 0


# each ball
#2nd innings values



ing2_curr_score = 0
ing2_curr_wickets = 0
ing2_curr_overs = 0.0

i=0
j=0


for i in range(len(df_ing2)):
    
    ing1_actual_score = sum(df_ing1.total_runs)
    ing2_actual_score = sum(df_ing2.total_runs)
    # 1st innings values
    target = ing1_actual_score
    
    #2nd innings values
    ing2_curr_score += df_ing2.total_runs[i]
    ing2_curr_wickets += df_ing2.isOut[i]
    ing2_curr_overs = df_ing2.ball[i]
    
    # make a prediction for 100 times & get win/lose/tie count(ex: 28% win)
    for k in range(100):
        ing2_prediction = innings_2_runs(ing2_curr_overs, ing2_curr_score, ing2_curr_wickets, target)
        
#         print(target, ing2_prediction)
        
        # prediction w.r.t 2nd team
        if ing2_prediction > target:
            win_count += 1
        elif ing2_prediction == target:
            tie_count += 1
        else:
            lose_count += 1
            
    win_count_ls.append(win_count)
    tie_count_ls.append(tie_count)
    lose_count_ls.append(lose_count)
    
    win_count = 0
    tie_count = 0
    lose_count = 0



# Streamlit page config
st.set_page_config(page_title="IPL Win Percentage Chart", layout="wide")

# Title
st.title("IPL Match Win Percentage Chart")


# Create the Plotly figure
fig = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces for each team and tie
fig.add_trace(
    go.Scatter(
        x=list(range(len(win_count_ls))), 
        y=win_count_ls, 
        name=team2, 
        line=dict(color=team_mapping[team2]['colors'][0], 
                  shape='spline'))
)
fig.add_trace(
    go.Scatter(
        x=list(range(len(tie_count_ls))), 
        y=tie_count_ls, 
        name='Tie Value', 
        line=dict(color='grey', 
                  shape='spline'))
)
fig.add_trace(
    go.Scatter(
        x=list(range(len(lose_count_ls))), 
        y=lose_count_ls, 
        name=team1, 
        line=dict(color=team_mapping[team1]['colors'][0], 
                  shape='spline'))
)

# Update layout
fig.update_layout(
    title='Win Percentage Chart: ' + team1_short_name + ' vs ' + team2_short_name,
    xaxis_title="Ball No",
    yaxis_title="Win %",
    legend_title="Teams",
    font=dict(size=12),
    hovermode="x unified",
    yaxis=dict(range=[0, 100], tickvals=[0, 25, 50, 75, 100])
)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)