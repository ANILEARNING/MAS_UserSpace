import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_win_percentages(data, team_mapping):
    inning1 = data[data['innings'] == 1]
    inning2 = data[data['innings'] == 2]

    team1 = str(inning1['batting_team'].unique()[0])
    team2 = str(inning2['batting_team'].unique()[0])

    team1_short_name = team_mapping[team1]['short']
    team2_short_name = team_mapping[team2]['short']

    # Calculate outcomes based on total_runs_off_ball instead of total_runs
    t1_outcomes = data[data.batting_team == team1].total_runs_off_ball.value_counts()
    t2_outcomes = data[data.batting_team == team2].total_runs_off_ball.value_counts()

    # Use wicket_fallen instead of isOut
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
    
    over_ball = curr_overs
    over_number = int(str(over_ball).split('.')[0])
    ball_number = int(str(over_ball).split('.')[1])
    
    if ball_number >= 6:
        ball_number = 6
    current_balls = over_number*6 + ball_number 
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
