import pandas as pd
import numpy as np
import statistics

from .db import create_connection
import flask
from flask import Blueprint, request, jsonify

nfl = Blueprint("nfl", __name__)
pd.set_option('display.max_columns', 100)

nfl_fourth_year = 2022
nfl_third_year = 2023
nfl_prior_year = 2024
nfl_current_year = 2025

year_name_dict = {2019: 'six_years_ago', 2020: 'five_years_ago' , 2021: 'four_years_ago',
                  2022: 'fourth', 2023: 'third', 2024: 'prior', 2025: 'current'}
limit_stat_dict = {'pass_att': 'pass_att', 'pass_yards': 'pass_att', 'pass_td': 'pass_att', 'pass_comp': 'pass_att',
                   'pass_longest': 'pass_att',
                   'rush_att': 'rush_att', 'rush_yards': 'rush_att', 'rush_td': 'rush_att', 'rush_longest': 'rush_att',
                   'rec': 'targets', 'targets': 'targets', 'rec_yards': 'targets', 'rec_td': 'targets',
                   'rec_longest': 'targets'}


def get_years_played(df):
    years_played = sorted(list(set(df['year'].values.tolist())))
    return years_played

def get_weeks_played(df, year):
    weeks_played = df.loc[df['year'] == year]['week'].values.tolist()
    return weeks_played

def nfl_info(**kwargs):
    if 'df' in kwargs:
        df_player_logs = kwargs['df']
        df_player_logs = df_player_logs[['name', 'year', 'week', 'position', 'game_id', 'player_id', 'team_id', 'opp_id']]
    else:
        cols_to_select = f"game_id, player_id, team_id, opp_id"

        # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
        connection = create_connection()
        cursor = connection.cursor()

        player_query = f'''SELECT
                        CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                        player.position, {cols_to_select}
                        FROM
                        nfl_player_stats
                        JOIN
                        player ON player.id = nfl_player_stats.player_id
                        JOIN 
                        nfl_games on nfl_games.id = nfl_player_stats.game_id
                        WHERE nfl_games.year >= 2019 AND nfl_player_stats.player_id = %s'''
        values = [kwargs['player_id']]
        cursor.execute(player_query, values)
        results = list(cursor.fetchall())

        df_columns = ['name', 'year', 'week', 'position', 'game_id', 'player_id', 'team_id', 'opp_id']
        df_player_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)
        df_player_logs = df_player_logs.loc[df_player_logs['player_id'] == int(kwargs['player_id'])]


    playing_years = sorted(list(set(df_player_logs['year'].values.tolist())))
    opponent_dict = {}
    team_dict = {}
    for year in playing_years[-4:]:
        df_opp = df_player_logs.copy()
        df_opp = df_opp.loc[df_opp['year'] == year][['week', 'opp_id']]
        opponent_dict[year] = dict(zip(df_opp.week, df_opp.opp_id))


        team_list = df_player_logs.loc[df_player_logs['year'] == year]['team_id'].values.tolist()
        team_merge = []
        for team in team_list:
            if team not in team_merge:
                team_merge.append(team)
        if len(team_merge) == 1:
            team_dict[year] = team_merge[0]
        else:
            team_dict[year] = team_merge

    output = {'opponent': opponent_dict, 'team': team_dict}
    return output



# GET ROUTES - Player related bet data
@nfl.route('/nfl/player/game_logs', methods=['GET'])
def nfl_player_game_logs():
    player_id = int(request.args.get('id', None))
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = int(request.args.get('value', None))
    json_output = {}

    if column_name in ['pass_att', 'pass_yards', 'pass_td', 'pass_comp', 'pass_longest']:
        columns = 'pass_att, pass_yards, pass_td, pass_comp, pass_longest'
        df_columns = ['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'pass_att', 'pass_yards',
                      'pass_td', 'pass_comp', 'pass_longest']
    elif column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        columns = 'rush_att, rush_yards, rush_td, rush_longest, fumbles'
        df_columns = ['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'rush_att', 'rush_yards',
                      'rush_td', 'rush_longest', 'fumbles']
    else:
        columns = 'rec, targets, rec_yards, rec_td, rec_longest'
        df_columns = ['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'rec', 'targets',
                      'rec_yards', 'rec_td', 'rec_longest']

    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, game_id, player_id, team_id, opp_id, {columns}
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    WHERE nfl_games.year >= 2022 AND nfl_player_stats.player_id = %s'''
    values = [player_id]
    cursor.execute(player_query, values)

    results = list(cursor.fetchall())

    df_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)

    # This block gets players most recent information
    df_player_info = df_logs.tail(1)
    player_pos = df_player_info['pos'].values.tolist()[0]

    json_output.update({'player_position': player_pos})
    json_output.update({'player_name': df_player_info['name'].values.tolist()[0]})
    json_output.update({'player_team': df_player_info['team_id'].values.tolist()[0]})

    # PLAYER GAME LOG INFORMATION
    json_output.update({'current_game_logs': df_logs[ df_logs['year'] == nfl_current_year].to_json()})
    json_output.update({'prior_game_logs': df_logs[df_logs['year'] == nfl_prior_year].to_json()})
    json_output.update({'third_game_logs': df_logs[df_logs['year'] == nfl_third_year].to_json()})
    json_output.update({'fourth_game_logs': df_logs[df_logs['year'] == nfl_fourth_year].to_json()})
    json_output.update({'last_four_game_logs': df_logs.tail(4).to_json()})
    json_output.update({'last_eight_game_logs': df_logs.tail(8).to_json()})

    if operator == 'over':
        json_output.update({'current_bet_logs': df_logs[
            (df_logs['year'] == nfl_current_year) & (df_logs[column_name] > value)].to_json()})
        json_output.update({'prior_bet_logs': df_logs.loc[
            (df_logs['year'] == nfl_prior_year) & (df_logs[column_name] > value)].to_json()})
        json_output.update({'third_bet_logs': df_logs.loc[
            (df_logs['year'] == nfl_third_year) & (df_logs[column_name] > value)].to_json()})
        json_output.update({'fourth_bet_logs': df_logs.loc[
            (df_logs['year'] == nfl_fourth_year) & (df_logs[column_name] > value)].to_json()})
    else:
        json_output.update({'current_bet_logs': df_logs.loc[
            (df_logs['year'] == nfl_current_year) & (df_logs[column_name] <= value)].to_json()})
        json_output.update({'prior_bet_logs': df_logs.loc[
            (df_logs['year'] == nfl_prior_year) & (df_logs[column_name] <= value)].to_json()})
        json_output.update({'third_bet_logs': df_logs.loc[
            (df_logs['year'] == nfl_third_year) & (df_logs[column_name] <= value)].to_json()})
        json_output.update({'third_bet_logs': df_logs.loc[
            (df_logs['year'] == nfl_fourth_year) & (df_logs[column_name] <= value)].to_json()})

    return json_output

@nfl.route('/nfl/player/bet_occurrence_data', methods=['GET'])
def nfl_player_bet_data():
    player_id = int(request.args.get('id', None))
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = int(request.args.get('value', None))
    opp_id = int(request.args.get('opp_id', None))
    json_output = {}

    limit_stat = limit_stat_dict[column_name]
    columns = f'''{limit_stat}, {column_name}'''
    df_columns = ['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', limit_stat, column_name]

    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, game_id, player_id, team_id, opp_id, {columns}
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    WHERE nfl_games.year >= 2022 AND nfl_player_stats.player_id = {player_id}'''
    # values = [player_id]
    cursor.execute(player_query)
    results = list(cursor.fetchall())

    df_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)

    # GET TOTAL BET OCCURRENCE (LAST 3 YEARS AND CURRENT YEAR)
    total_games_played = len(df_logs.index)

    # GET CURRENT YEAR BET OCCURRENCE (2025)
    df_current = df_logs[df_logs['year'] == nfl_current_year].reset_index(drop=True)
    df_current.index = df_current.index + 1
    current_games_played = len(df_current.index)

    # GET PRIOR YEAR BET OCCURRENCE (2024)
    df_prior = df_logs[df_logs['year'] == nfl_prior_year].reset_index(drop=True)
    df_prior.index = df_prior.index +1
    prior_games_played = len(df_prior.index)

    # GET THIRD YEAR BET OCCURRENCE (2023)
    df_third = df_logs[df_logs['year'] == nfl_third_year].reset_index(drop=True)
    df_third.index = df_third.index + 1
    third_games_played = len(df_third.index)

    # GET FOURTH YEAR BET OCCURRENCE (2023)
    df_fourth = df_logs[df_logs['year'] == nfl_fourth_year].reset_index(drop=True)
    df_fourth.index = df_fourth.index + 1
    fourth_games_played = len(df_fourth.index)

    # BET OCCURRENCES IN THE LAST 4 AND 8 GAMES
    last_four = df_logs.tail(4).reset_index(drop=True)
    last_eight = df_logs.tail(8).reset_index(drop=True)

    # BET OCCURRENCES IN GAMES VS OPPONENT
    df_opponent = df_logs[df_logs['opp_id'] == opp_id].reset_index(drop=True)
    games_vs_opponent = len(df_opponent.index)


    if operator == 'over':
        total_bet_occurrences = df_logs[df_logs[column_name] > value]
        current_bet_occurrences = df_current[df_current[column_name] > value]
        prior_bet_occurrences = df_prior[df_prior[column_name] > value]
        third_bet_occurrences = df_third[df_third[column_name] > value]
        fourth_bet_occurrences = df_fourth[df_fourth[column_name] > value]
        previous_four_game_occurrences = last_four[last_four[column_name] > value]
        previous_eight_game_occurrences = last_eight[last_eight[column_name] > value]
        vs_opponent_occurrences = df_opponent[df_opponent[column_name] > value]
    else:
        total_bet_occurrences = df_logs[df_logs[column_name] <= value]
        prior_bet_occurrences = df_prior[df_prior[column_name] <= value]
        current_bet_occurrences = df_current[df_current[column_name] <= value]
        third_bet_occurrences = df_third[df_third[column_name] <= value]
        fourth_bet_occurrences = df_fourth[df_fourth[column_name] <= value]
        previous_four_game_occurrences = last_four[last_four[column_name] <= value]
        previous_eight_game_occurrences = last_eight[last_eight[column_name] <= value]
        vs_opponent_occurrences = df_opponent[df_opponent[column_name] > value]

    try:
        json_output.update(
            {'career_bet_occurrence': round((len(total_bet_occurrences.index) / total_games_played) * 100, 1)})
    except ZeroDivisionError:
        json_output.update( {'career_bet_occurrence': 0.0})
    try:
        json_output.update(
            {'current_bet_occurrence': round((len(current_bet_occurrences.index) / current_games_played) * 100, 1)})
    except ZeroDivisionError:
        json_output.update({'current_bet_occurrence': 0.0})
    try:
        json_output.update({'prior_bet_occurrence': round((len(prior_bet_occurrences.index) / prior_games_played) * 100, 1)})
    except ZeroDivisionError:
        json_output.update({'prior_bet_occurrence': 0.0})
    try:
        json_output.update({'third_bet_occurrence': round((len(third_bet_occurrences.index) / third_games_played) * 100, 1)})
    except ZeroDivisionError:
        json_output.update({'third_bet_occurrence': 0.0})
    try:
        json_output.update(
            {'fourth_bet_occurrence': round((len(fourth_bet_occurrences.index) / fourth_games_played) * 100, 1)})
    except ZeroDivisionError:
        json_output.update({'fourth_bet_occurrence': 0.0})
    try:
        json_output.update(
            {'last_four_game_bet_occurrence': round((len(previous_four_game_occurrences.index) / 4) * 100, 1)})
    except ZeroDivisionError:
        json_output.update({'last_four_game_bet_occurrence': 0.0})
    try:
        json_output.update(
            {'last_eight_game_bet_occurrence': round((len(previous_eight_game_occurrences.index) / 8) * 100, 1)})
    except ZeroDivisionError:
        json_output.update({'last_eight_game_bet_occurrence': 0.0})
    try:
        json_output.update(
            {'vs_opponent_occurrences': round((len(vs_opponent_occurrences.index) / 8) * 100, games_vs_opponent)})
    except ZeroDivisionError:
        json_output.update({'vs_opponent_occurrences': 0.0})

    # GET WEEKS BETWEEN BET OCCURRENCES
    for year in np.unique(df_logs['year'].values):
        df_year = df_logs[df_logs['year'] == year].reset_index(drop=True)
        df_year.index = df_year.index + 1

        if operator == 'over':
            df_year['bet_hit'] = np.where(df_year[column_name] > value, True, False)
        else:
            df_year['bet_hit'] =  np.where(df_year[column_name] <= value, True, False)

        weeks_bet_occurred = df_year[df_year['bet_hit'] == True].index.values
        last_game = df_year.tail(1).index.values[0]
        first_game = df_year.head(1).index.values[0]

        if first_game != weeks_bet_occurred[0]:
            weeks_bet_occurred = np.insert(weeks_bet_occurred, 0, first_game)
        if last_game != weeks_bet_occurred[-1]:
            weeks_bet_occurred = np.append(weeks_bet_occurred, last_game)
        time_btw_hits = np.diff(weeks_bet_occurred).mean()
        json_output.update({f"weeks_between_hits_{year_name_dict[year]}": round(time_btw_hits, 1)})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output

@nfl.route('/nfl/team/opponent_logs_and_occurrence')
def nfl_opponent_logs_and_occurrences():
    player_id = int(request.args.get('id', None))
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = int(request.args.get('value', None))
    opp_id = int(request.args.get('opp_id', None))
    json_output = {}


    limit_stat = limit_stat_dict[column_name]
    if column_name in ['pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest', 'int', 'sack']:
        columns = f'''pass_att, pass_comp, pass_yards, pass_td, pass_longest, int, sack'''
        df_columns = ['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'pass_att',
                      'pass_comp', 'pass_yards', 'pass_td', 'pass_longest', 'int', 'sack']
        limit_amount = 5
    elif column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest', 'fumbles']:
        columns = f'''rush_att, rush_yards, rush_td, rush_longest, fumbles'''
        df_columns = ['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'rush_att',
                      'rush_yards', 'rush_td', 'rush_longest', 'fumbles']
        limit_amount = 1
    else:
        columns = f'''targets, rec, rec_yards, rec_td, rec_longest'''
        df_columns = ['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'targets',
                      'rec', 'rec_yards', 'rec_td', 'rec_longest']
        limit_amount = 1


    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, game_id, player_id, team_id, opp_id, {columns}
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    WHERE nfl_games.year >= 2022 AND nfl_player_stats.opp_id = {opp_id}
                    AND nfl_player_stats.{limit_stat} >= {limit_amount}'''

    cursor.execute(player_query)
    results = list(cursor.fetchall())

    df_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)
    last_four_id = np.unique(df_logs['game_id'].values)[-4:]
    last_eight_id = np.unique(df_logs['game_id'].values)[-8:]

    # GET OPPONENT GAME LOGS
    opp_current_game_logs = df_logs[df_logs['year'] == nfl_current_year].reset_index(drop=True)
    opp_prior_game_logs = df_logs[df_logs['year'] == nfl_prior_year].reset_index(drop=True)
    opp_third_game_logs = df_logs[df_logs['year'] == nfl_third_year].reset_index(drop=True)
    opp_fourth_game_logs = df_logs[df_logs['year'] == nfl_fourth_year].reset_index(drop=True)
    opp_last_four_game_logs = df_logs[df_logs['game_id'].isin(last_four_id)].reset_index(drop=True)
    opp_last_eight_game_logs = df_logs[df_logs['game_id'].isin(last_eight_id)].reset_index(drop=True)

    # GET NUMBER OF WEEKS BET HIT
    total_games_played = len(np.unique(df_logs['game_id'].values))
    prior_games_played = len(np.unique(opp_prior_game_logs['game_id'].values))
    third_games_played = len(np.unique(opp_third_game_logs['game_id'].values))
    fourth_games_played = len(np.unique(opp_fourth_game_logs['game_id'].values))

    # GET BET OCCURRENCES VS OPPONENT
    if operator == 'over':
        total_bet_occurrences = df_logs[df_logs[column_name] > value]
        current_bet_occurrences = opp_current_game_logs[opp_current_game_logs[column_name] > value]
        prior_bet_occurrences = opp_prior_game_logs[opp_prior_game_logs[column_name] > value]
        third_bet_occurrences = opp_third_game_logs[opp_third_game_logs[column_name] > value]
        fourth_bet_occurrences = opp_fourth_game_logs[opp_fourth_game_logs[column_name] > value]
        last_four_bet_occurrences = opp_last_four_game_logs[opp_last_four_game_logs[column_name] > value]
        last_eight_bet_occurrences = opp_last_eight_game_logs[opp_last_eight_game_logs[column_name] > value]
    else:
        total_bet_occurrences = df_logs[df_logs[column_name] <= value]
        current_bet_occurrences = opp_current_game_logs[opp_current_game_logs[column_name] <= value]
        prior_bet_occurrences = opp_prior_game_logs[opp_prior_game_logs[column_name] <= value]
        third_bet_occurrences = opp_third_game_logs[opp_third_game_logs[column_name] <= value]
        fourth_bet_occurrences = opp_fourth_game_logs[opp_fourth_game_logs[column_name] <= value]
        last_four_bet_occurrences = opp_last_four_game_logs[opp_last_four_game_logs[column_name] <= value]
        last_eight_bet_occurrences = opp_last_eight_game_logs[opp_last_eight_game_logs[column_name] <= value]

    # PERCENTAGE OF WEEKS THAT BET HIT
    json_output.update(
        {'career_weekly_bet_occurrence': round(((len(np.unique(total_bet_occurrences['game_id'].values))) / total_games_played) * 100, 1)})
    json_output.update(
        {'prior_weekly_bet_occurrence': round(((len(np.unique(prior_bet_occurrences['game_id'].values))) / prior_games_played) * 100, 1)})
    json_output.update(
        {'third_weekly_bet_occurrence': round(((len(np.unique(third_bet_occurrences['game_id'].values))) / third_games_played) * 100, 1)})
    json_output.update(
        {'fourth_weekly_bet_occurrence': round(((len(np.unique(fourth_bet_occurrences['game_id'].values))) / fourth_games_played) * 100, 1)})
    json_output.update(
        {'last_four_weekly_bet_occurrence': round(((len(np.unique(last_four_bet_occurrences['game_id'].values))) / 4) * 100, 1)})
    json_output.update(
        {'last_eight_weekly_bet_occurrence': round(((len(np.unique(last_eight_bet_occurrences['game_id'].values))) / 8) * 100, 1)})

    # NUMBER OF PLAYERS FOR EACH TIME PERIOD THAT HIT BET EACH WEEK AGAINST OPPONENT
    current_player_count = current_bet_occurrences.groupby(by=['week']).agg(weekly_total=(column_name, "count"))
    current_weekly_player_counts = pd.Series(current_player_count['weekly_total'].values, index=current_player_count.index).to_dict()
    current_weekly_total_players_avg = round(current_player_count['weekly_total'].mean(), 1)
    json_output.update({'current_weekly_player_counts': current_weekly_player_counts})
    json_output.update({'current_weekly_total_players_avg': current_weekly_total_players_avg})

    prior_player_count = prior_bet_occurrences.groupby(by=['week']).agg(weekly_total=(column_name, "count"))
    prior_weekly_player_counts = pd.Series(prior_player_count['weekly_total'].values, index=prior_player_count.index).to_dict()
    prior_weekly_total_players_avg = round(prior_player_count['weekly_total'].mean(), 1)
    json_output.update({'prior_weekly_player_counts': prior_weekly_player_counts})
    json_output.update({'prior_weekly_total_players_avg': prior_weekly_total_players_avg})

    third_player_count = third_bet_occurrences.groupby(by=['week']).agg(weekly_total=(column_name, "count"))
    third_weekly_player_counts = pd.Series(third_player_count['weekly_total'].values, index=third_player_count.index).to_dict()
    third_weekly_total_players_avg = round(third_player_count['weekly_total'].mean(), 1)
    json_output.update({'third_weekly_player_counts': third_weekly_player_counts})
    json_output.update({'third_weekly_total_players_avg': third_weekly_total_players_avg})

    fourth_player_count = fourth_bet_occurrences.groupby(by=['week']).agg(weekly_total=(column_name, "count"))
    fourth_weekly_player_counts = pd.Series(fourth_player_count['weekly_total'].values, index=fourth_player_count.index).to_dict()
    fourth_weekly_total_players_avg = round(fourth_player_count['weekly_total'].mean(), 1)
    json_output.update({'fourth_weekly_player_counts': fourth_weekly_player_counts})
    json_output.update({'fourth_weekly_total_players_avg': fourth_weekly_total_players_avg})

    last_four_player_count = last_four_bet_occurrences.groupby(by=['game_id']).agg(weekly_total=(column_name, "count"))
    last_four_weekly_player_counts = pd.Series(last_four_player_count['weekly_total'].values,
                                            index=last_four_player_count.index).to_dict()
    last_four_weekly_total_players_avg = round(last_four_player_count['weekly_total'].mean(), 1)
    json_output.update({'last_four_weekly_player_counts': last_four_weekly_player_counts})
    json_output.update({'last_four_weekly_total_players_avg': last_four_weekly_total_players_avg})

    last_eight_player_count = last_eight_bet_occurrences.groupby(by=['game_id']).agg(weekly_total=(column_name, "count"))
    last_eight_weekly_player_counts = pd.Series(last_eight_player_count['weekly_total'].values,
                                            index=last_eight_player_count.index).to_dict()
    last_eight_weekly_total_players_avg = round(last_eight_player_count['weekly_total'].mean(), 1)
    json_output.update({'last_eight_weekly_player_counts': last_eight_weekly_player_counts})
    json_output.update({'last_eight_weekly_total_players_avg': last_eight_weekly_total_players_avg})


    # GET OPPONENT GAME LOGS VS SELECTED PLAYER
    opp_logs_vs_player = df_logs[df_logs['player_id'] == player_id].reset_index(drop=True)
    opp_games_vs_player_count = len(opp_logs_vs_player.index)
    if operator == 'over':
        vs_player_bet_occurrences = opp_logs_vs_player[opp_logs_vs_player[column_name] > value]
    else:
        vs_player_bet_occurrences = opp_logs_vs_player[opp_logs_vs_player[column_name] <= value]
    json_output.update({'vs_player_bet_occurrences': round(
        (len(vs_player_bet_occurrences.index) / opp_games_vs_player_count) * 100, 1)})
    json_output.update({'vs_player_game_logs': opp_logs_vs_player.to_json()})


    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output

@nfl.route('/nfl/stats/target_and_percentages', methods=['GET'])
def stat_and_target_percentages():
    team_id = request.args.get('team_id', None)
    player_id = request.args.get('id', None)
    column_name = request.args.get('stat', None)
    json_output = {}

    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                            player.position, player_id, team_id, game_id, {column_name}, targets
                        FROM
                        nfl_player_stats
                        JOIN
                        player ON player.id = nfl_player_stats.player_id
                        JOIN 
                        nfl_games on nfl_games.id = nfl_player_stats.game_id
                        WHERE nfl_games.year >=2022 AND nfl_player_stats.game_id IN 
                        (select nfl_player_stats.game_id from nfl_player_stats where nfl_player_stats.player_id = %s)
                         '''
    values = [player_id]
    cursor.execute(player_query, values)
    results = list(cursor.fetchall())

    df_columns = ['name', 'year', 'week', 'position', 'player_id', 'team_id', 'game_id', column_name, 'targets']
    df_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)

    loop_years = np.unique(df_logs['year'].values)
    for year in loop_years:
        df_year = df_logs[(df_logs['year'] == year) & (df_logs['team_id'] == int(team_id))]
        df_player = df_year[df_year['player_id'] == int(player_id)]

        grouped_week = df_year.groupby(['week'])[[column_name, 'targets']].sum()
        grouped_week['player_total'] = df_player[column_name].values
        grouped_week['player_targets'] = df_player['targets'].values
        grouped_week['percentage_of_total'] = round(((grouped_week['player_total'] / grouped_week[column_name]) * 100),
                                                    1)
        grouped_week['player_target_share'] = round(((grouped_week['player_targets'] / grouped_week['targets']) * 100),
                                                    1)

        # GET PLAYER AND TEAM STAT TOTALS
        team_weekly_stat_total = pd.Series(grouped_week[column_name].values, index=grouped_week.index).to_dict()
        player_weekly_stat_total = pd.Series(grouped_week['player_total'].values, index=grouped_week.index).to_dict()
        percentage_of_weekly_total = pd.Series(grouped_week['percentage_of_total'].values,
                                               index=grouped_week.index).to_dict()
        json_output.update(
                {f"team_weekly_stat_total_{year_name_dict[year]}": team_weekly_stat_total})
        json_output.update(
                {f"player_weekly_stat_total_{year_name_dict[year]}": player_weekly_stat_total})
        json_output.update(
                {f"percentage_of_weekly_total_{year_name_dict[year]}": percentage_of_weekly_total})


        # GET TEAM TARGETS AND PLAYER TARGET SHARE
        team_weekly_target_total = pd.Series(grouped_week['targets'].values, index=grouped_week.index).to_dict()
        player_weekly_target_total = pd.Series(grouped_week['player_targets'].values,
                                               index=grouped_week.index).to_dict()
        player_weekly_target_share = pd.Series(grouped_week['player_target_share'].values,
                                               index=grouped_week.index).to_dict()
        json_output.update(
                {f"team_weekly_target_total_{year_name_dict[year]}": team_weekly_target_total})
        json_output.update(
                {f"player_weekly_target_total_{year_name_dict[year]}": player_weekly_target_total})
        json_output.update(
                {f"player_weekly_target_share_{year_name_dict[year]}": player_weekly_target_share})


    # Enable Access-Control-Allow-Origin
    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")

    return json_output

@nfl.route('/nfl/player/home_road_splits', methods=['GET'])
def nfl_home_road_logs():
    player_id = int(request.args.get('id', None))
    column_name = request.args.get('stat', None)
    team_id = int(request.args.get('team_id', None))
    operator = request.args.get('operator', None)
    value = int(request.args.get('value', None))
    json_output = {}


    if column_name in ['pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest', 'int', 'sack']:
        columns = f'''pass_att, pass_comp, pass_yards, pass_td, pass_longest, int, sack'''
        df_columns = ['name', 'year', 'week', 'home_id', 'away_id', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'pass_att',
                      'pass_comp', 'pass_yards', 'pass_td', 'pass_longest', 'int', 'sack']
    elif column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest', 'fumbles']:
        columns = f'''rush_att, rush_yards, rush_td, rush_longest, fumbles'''
        df_columns = ['name', 'year', 'week', 'home_id', 'away_id', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'rush_att',
                      'rush_yards', 'rush_td', 'rush_longest', 'fumbles']
    else:
        columns = f'''targets, rec, rec_yards, rec_td, rec_longest'''
        df_columns = ['name', 'year', 'week', 'home_id', 'away_id', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'targets',
                      'rec', 'rec_yards', 'rec_td', 'rec_longest']


    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, 
                        nfl_games.week, nfl_games.home_id, nfl_games.away_id, player.position, game_id, player_id, team_id, opp_id, {columns}
                        FROM
                        nfl_player_stats
                        JOIN
                        player ON player.id = nfl_player_stats.player_id
                        JOIN 
                        nfl_games on nfl_games.id = nfl_player_stats.game_id
                        WHERE nfl_games.year >=2022 AND nfl_player_stats.player_id = {player_id}'''

    cursor.execute(player_query)
    results = list(cursor.fetchall())

    df_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)

    # SEPARATE OUT HOME AND AWAY LOGS
    df_home = df_logs[df_logs['home_id'] == team_id].reset_index(drop=True)
    df_away = df_logs[df_logs['away_id'] == team_id].reset_index(drop=True)

    total_home_games = len(df_home.index)
    total_away_games = len(df_away.index)
    prior_home_games = len(df_home[df_home['year'] == nfl_prior_year].index)
    third_home_games = len(df_home[df_home['year'] == nfl_third_year].index)
    fourth_home_games = len(df_home[df_home['year'] == nfl_fourth_year].index)
    prior_away_games = len(df_away[df_away['year'] == nfl_prior_year].index)
    third_away_games = len(df_away[df_away['year'] == nfl_third_year].index)
    fourth_away_games = len(df_away[df_away['year'] == nfl_fourth_year].index)

    if operator == 'over':
        home_bet_occurrences = df_home[df_home[column_name] > value]
        away_bet_occurrences = df_away[df_away[column_name] > value]
        home_bet_occurrences_prior = df_home[(df_home['year'] == nfl_prior_year) & (df_home[column_name] > value)]
        away_bet_occurrences_prior = df_away[(df_away['year'] == nfl_prior_year) & (df_away[column_name] > value)]
        home_bet_occurrences_third = df_home[(df_home['year'] == nfl_third_year) & (df_home[column_name] > value)]
        away_bet_occurrences_third = df_away[(df_away['year'] == nfl_third_year) & (df_away[column_name] > value)]
        home_bet_occurrences_fourth = df_home[(df_home['year'] == nfl_fourth_year) & (df_home[column_name] > value)]
        away_bet_occurrences_fourth = df_away[(df_away['year'] == nfl_fourth_year) & (df_away[column_name] > value)]
    else:
        home_bet_occurrences = df_home[df_home[column_name] <= value]
        away_bet_occurrences = df_away[df_away[column_name] <= value]
        home_bet_occurrences_prior = df_home[(df_home['year'] == nfl_prior_year) & (df_home[column_name] <= value)]
        away_bet_occurrences_prior = df_away[(df_away['year'] == nfl_prior_year) & (df_away[column_name] <= value)]
        home_bet_occurrences_third = df_home[(df_home['year'] == nfl_third_year) & (df_home[column_name] <= value)]
        away_bet_occurrences_third = df_away[(df_away['year'] == nfl_third_year) & (df_away[column_name] <= value)]
        home_bet_occurrences_fourth = df_home[(df_home['year'] == nfl_fourth_year) & (df_home[column_name] <= value)]
        away_bet_occurrences_fourth = df_away[(df_away['year'] == nfl_fourth_year) & (df_away[column_name] <= value)]
    json_output.update(
        {'home_game_bet_occurrence': round((len(home_bet_occurrences.index) / total_home_games) * 100, 1)})
    json_output.update(
        {'away_game_bet_occurrence': round((len(away_bet_occurrences.index) / total_away_games) * 100, 1)})
    json_output.update(
        {'home_bet_occurrences_prior': round((len(home_bet_occurrences_prior.index) / prior_home_games) * 100, 1)})
    json_output.update(
        {'away_bet_occurrences_prior': round((len(away_bet_occurrences_prior.index) / prior_away_games) * 100, 1)})
    json_output.update(
        {'home_bet_occurrences_third': round((len(home_bet_occurrences_third.index) / third_home_games) * 100, 1)})
    json_output.update(
        {'away_bet_occurrences_third': round((len(away_bet_occurrences_third.index) / third_away_games) * 100, 1)})
    json_output.update(
        {'home_bet_occurrences_fourth': round((len(home_bet_occurrences_fourth.index) / fourth_home_games) * 100, 1)})
    json_output.update(
        {'away_bet_occurrences_fourth': round((len(away_bet_occurrences_fourth.index) / fourth_away_games) * 100, 1)})



    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output



@nfl.route('/nfl/player_red_zone', methods=['GET'])
def nfl_get_player_redzone_stats():
    player_id = request.args.get('id', None)

    player_team_dict = nfl_info(player_id=player_id)['team']
    playing_years = list(player_team_dict.keys())

    json_output = {}

    # GET PLAYER RED ZONE STATS - Create a query, cursor and result list. Loop through list and merge to create 'df_red_zone'
    connection = create_connection()
    cursor = connection.cursor()

    player_rz_query = f'''SELECT CONCAT(player.first_name, ' ', player.last_name), nfl_redzone_stats.*
                FROM nfl_redzone_stats
                JOIN player ON player.id = nfl_redzone_stats.player_id
                WHERE nfl_redzone_stats.player_id = %s'''
    values = [player_id]
    cursor.execute(player_rz_query, values)
    rz_results = list(cursor.fetchall())


    rz_cols = ['name', 'id', 'player_id', 'year', 'rz_20_pass_att', 'rz_20_pass_comp', 'rz_20_pass_comp_percentage',
               'rz_20_pass_yard', 'rz_20_pass_td', 'rz_20_pass_int', 'rz_10_pass_att', 'rz_10_pass_comp',
               'rz_10_comp_percentage', 'rz_10_pass_yard', 'rz_10_pass_td', 'rz_10_pass_int', 'rz_20_targets',
               'rz_20_receptions', 'rz_20_rec_yards', 'rz_20_catch_percentage', 'rz_20_rec_td',
               'rz_20_target_percentage', 'rz_10_targets', 'rz_10_receptions', 'rz_10_rec_yards',
               'rz_10_catch_percentage', 'rz_10_rec_td', 'rz_10_target_percentage', 'rz_20_rush_att',
               'rz_20_rush_yards', 'rz_20_rush_td', 'rz_20_rush_percentage', 'rz_10_rush_att', 'rz_10_rush_yards',
               'rz_10_rush_td', 'rz_10_rush_percentage', 'rz_5_rush_att', 'rz_5_rush_yards', 'rz_5_rush_td',
               'rz_5_rush_percentage']
    df_red_zone = pd.DataFrame(rz_results, columns=rz_cols).reset_index(drop=True)


    # GET TEAM RED ZONE STATS - Create a query, cursor and result list. Loop through list and merge to create 'df_red_zone'
    connection = create_connection()
    cursor = connection.cursor()
    team_off_query = f'''SELECT id, team_id, year, games, rz_att, rz_td, rz_percentage FROM nfl_team_offense'''

    cursor.execute(team_off_query)
    results = list(cursor.fetchall())

    off_cols = ['id', 'team_id', 'year', 'games', 'rz_att', 'rz_td', 'rz_percentage']
    df_team_rz = pd.DataFrame(results, columns=off_cols).reset_index(drop=True)

    for year in playing_years[-3:]:
        df_player_yr_rz = df_red_zone.copy()
        df_player_yr_rz = df_player_yr_rz.loc[df_player_yr_rz['year'] == year]

        df_team_yr_rz = df_team_rz.copy()
        df_team_yr_rz = df_team_yr_rz.loc[df_team_yr_rz['team_id'] == player_team_dict[year]]
        team_rz_att = df_team_yr_rz.loc[df_team_yr_rz['year'] == year]['rz_att'].values.tolist()[0]
        json_output.update({f"team_total_rz_td_{year_name_dict[year]}": team_rz_att})

        # GET RZ PASSING TD AS PERCENTAGE OF RZ ATT
        total_rz_pass_td = (df_player_yr_rz['rz_20_pass_td'].values.tolist()[0] +
                            df_player_yr_rz['rz_10_pass_td'].values.tolist()[0])
        total_rz_pass_td_percentage = round(((total_rz_pass_td / team_rz_att) * 100), 1)
        json_output.update({f"team_pass_rz_td_{year_name_dict[year]}": total_rz_pass_td})
        json_output.update({f"rz_pass_td_percentage_{year_name_dict[year]}": total_rz_pass_td_percentage})

        # GET RZ RUSHING TD AS PERCENTAGE OF RZ ATT
        total_rz_rush_td = (df_player_yr_rz['rz_20_rush_td'].values.tolist()[0] +
                            df_player_yr_rz['rz_10_rush_td'].values.tolist()[0] +
                            df_player_yr_rz['rz_5_rush_td'].values.tolist()[0])
        total_rz_rush_td_percentage = round(((total_rz_rush_td / team_rz_att) * 100), 1)
        json_output.update({f"team_rush_rz_td_{year_name_dict[year]}": total_rz_rush_td})
        json_output.update({f"rz_rush_td_percentage_{year_name_dict[year]}": total_rz_rush_td_percentage})

        # GET RZ RECEIVING TD AS PERCENTAGE OF RZ ATT
        total_rz_rec_td = (df_player_yr_rz['rz_20_rec_td'].values.tolist()[0] +
                           df_player_yr_rz['rz_10_rec_td'].values.tolist()[0])
        total_rz_rec_td_percentage = round(((total_rz_rec_td / team_rz_att) * 100), 1)
        json_output.update({f"team_rec_rz_td_{year_name_dict[year]}": total_rz_rec_td})
        json_output.update({f"rz_rec_td_percentage_{year_name_dict[year]}": total_rz_rec_td_percentage})

        # GET TEAM RZ CONVERSION PERCENTAGE RANK
        df_team_rank = df_team_rz.copy().loc[df_team_rz['year'] == year]
        df_team_rank['rz_percentage_rank'] = df_team_rank['rz_percentage'].rank(ascending=False)

        team_rank =df_team_rank.loc[df_team_rank['team_id'] == player_team_dict[year]]['rz_percentage_rank'].values.tolist()[0]
        json_output.update({f"team_rz_percentage_rank_{year_name_dict[year]}": team_rank})

    return json_output


@nfl.route('/nfl/rankings', methods=['GET'])
def nfl_get_rankings():
    column_name = request.args.get('stat', None)
    player_id = request.args.get('id', None)

    player_info = nfl_info(player_id=player_id)
    team_opponent_dict = player_info['opponent']
    player_teams_dict = player_info['team']
    json_output = {}

    # GET WEEKLY RANK STATS - Create a query, cursor and result list. Loop through list and merge to create 'df_red_zone'
    if column_name in ['pass_att', 'pass_comp', 'pass_yards',	'pass_td']:
        other_cols = ['pyards_per_att', 'pass_yards_rank', 'pass_comp_rank', 'pass_td_rank',
                      'pass_yards_per_att_rank']
        wkly_cols_to_select = f"team_id, year, week, {column_name}, pyards_per_att, pass_yards_rank, pass_comp_rank, pass_td_rank, pass_yards_per_att_rank"
    elif column_name in ['rush_att', 'rush_yards',	'rush_td']:
        other_cols = ['ryards_per_att', 'rush_att_rank', 'rush_yards_rank', 'rush_td_rank',
                      'rush_yards_per_att_rank']
        wkly_cols_to_select = f"team_id, year, week, {column_name}, ryards_per_att, rush_att_rank, rush_yards_rank, rush_td_rank, rush_yards_per_att_rank"
    else:
        other_cols = ['rec_yards_rank', 'rec_td_rank', 'rec_rank', 'rec_yards_per_rec_rank']
        wkly_cols_to_select = f"team_id, year, week, {column_name}, rec_yards_rank, rec_td_rank, rec_rank, rec_yards_per_rec_rank"

    connection = create_connection()
    cursor = connection.cursor()
    weekly_rank_query = f'''SELECT {wkly_cols_to_select} FROM nfl_weekly_rank'''

    cursor.execute(weekly_rank_query)
    weekly_rank_results = list(cursor.fetchall())

    weekly_rank_cols = ['team_id', 'year', 'week', column_name] + other_cols
    df_weekly_rank = pd.DataFrame(weekly_rank_results, columns=weekly_rank_cols)

    # Get opponent ranks for specific stats
    rank_col = f"{column_name}_rank"
    for year in list(team_opponent_dict.keys())[-4:]:
        weeks_played = list(team_opponent_dict[year].keys())
        opp_rank_dict = {}
        opp_stat_total_dict = {}
        team_rank_dict = {}
        team_stat_total_dict = {}

        for week in weeks_played:
            df_year = df_weekly_rank.copy()
            df_opp = df_year.loc[(df_year['year'] == year) & (df_year['week'] == week) &
                                  (df_year['team_id'] == team_opponent_dict[year][week])]
            opponent_rank = df_opp[rank_col].values.tolist()[0]
            opp_rank_dict[week] = opponent_rank
            opp_stat_total_dict[week] = df_opp[column_name].values.tolist()[0]

            df_team_rank = df_year.loc[(df_year['year'] == year) & (df_year['week'] == week) &
                                  (df_year['team_id'] == player_teams_dict[year])]
            team_rank = df_team_rank[rank_col].values.tolist()[0]
            team_rank_dict[week] = team_rank
            team_stat_total_dict[week] = df_team_rank[column_name].values.tolist()[0]

            json_output.update({f"opponent_rank_z_coordinates_{year_name_dict[year]}": list(opp_stat_total_dict.values())})
            json_output.update({f"opponent_rank_y_coordinates_{year_name_dict[year]}": list(opp_rank_dict.values())})
            json_output.update({f"opponent_rank_x_coordinates_{year_name_dict[year]}": list(opp_rank_dict.keys())})

            json_output.update({f"team_rank_z_coordinates_{year_name_dict[year]}": list(team_stat_total_dict.values())})
            json_output.update({f"team_rank_y_coordinates_{year_name_dict[year]}": list(team_rank_dict.values())})
            json_output.update({f"team_rank_x_coordinates_{year_name_dict[year]}": list(team_rank_dict.keys())})

    # Enable Access-Control-Allow-Origin
    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")

    return json_output


# GET ROUTES - Team related bet data
@nfl.route('/nfl/team_stats', methods=['GET'])
def nfl_team_stats():
    team_id = int(request.args.get('team_id', None))
    connection = create_connection()
    cursor = connection.cursor()
    json_output = {}

    query = f'''SELECT * FROM nfl_team_offense
                WHERE nfl_team_offense.team_id = %s'''
    values = [team_id]
    cursor.execute(query, values)
    cols = ['id', 'team_id', 'year', 'games', 'dvoa', 'epa_per_play', 'success_rate', 'dropback_epa', 'dropback_sr',
        'rush_epa', 'rush_sr', 'pass_comp', 'pass_att', 'pass_comp_percentage', 'pass_yards', 'pass_td', 'pass_td_percentage',
        'yards_per_att', 'pass_yards_per_comp', 'pass_yards_per_game', 'passer_rating', 'sacks', 'ints', 'int_percentage',
        'rush_att', 'rush_yards', 'rush_td', 'rush_yards_per_att', 'rush_yards_per_game', 'fumbles', 'points_per_game',
        'total_points', 'drives', 'plays', 'scoring_percentage', 'to_percentage', 'plays_per_drive', 'yards_per_drive',
        'points_per_drive', 'third_down_att', 'third_down_conv', 'third_down_conv_rate', 'fourth_down_att', 'fourth_down_conv',
        'fourth_down_conv_rate', 'rz_att', 'rz_td', 'rz_percentage']
    results = list(cursor.fetchall())
    df_team_off_data = pd.DataFrame(results, columns=cols).reset_index(drop=True)


    # Get team passing data
    pass_comp = pd.Series(df_team_off_data['pass_comp'].values, index=df_team_off_data['year']).to_dict()
    pass_att = pd.Series(df_team_off_data['pass_att'].values, index=df_team_off_data['year']).to_dict()
    pass_comp_percentage = pd.Series(df_team_off_data['pass_comp_percentage'].values, index=df_team_off_data['year']).to_dict()
    pass_yards = pd.Series(df_team_off_data['pass_yards'].values, index=df_team_off_data['year']).to_dict()
    pass_td = pd.Series(df_team_off_data['pass_td'].values, index=df_team_off_data['year']).to_dict()
    pass_td_percentage = pd.Series(df_team_off_data['pass_td_percentage'].values, index=df_team_off_data['year']).to_dict()
    yards_per_att = pd.Series(df_team_off_data['yards_per_att'].values, index=df_team_off_data['year']).to_dict()
    pass_yards_per_game = pd.Series(df_team_off_data['pass_yards_per_game'].values, index=df_team_off_data['year']).to_dict()
    json_output.update({'team_pass_comp': pass_comp})
    json_output.update({'team_pass_att': pass_att})
    json_output.update({'team_pass_comp_percentage': pass_comp_percentage})
    json_output.update({'team_pass_yards': pass_yards})
    json_output.update({'team_pass_td': pass_td})
    json_output.update({'team_pass_td_percentage': pass_td_percentage})
    json_output.update({'team_yards_per_att': yards_per_att})
    json_output.update({'team_pass_yards_per_game': pass_yards_per_game})


    # Get teams scoring data
    pts_per_drive = pd.Series(df_team_off_data['points_per_drive'].values, index=df_team_off_data['year']).to_dict()
    pts_per_game = pd.Series(df_team_off_data['points_per_game'].values, index=df_team_off_data['year']).to_dict()
    scoring_percentage = pd.Series(df_team_off_data['scoring_percentage'].values, index=df_team_off_data['year']).to_dict()
    rz_att = pd.Series(df_team_off_data['rz_att'].values, index=df_team_off_data['year']).to_dict()
    rz_percentage = pd.Series(df_team_off_data['rz_percentage'].values, index=df_team_off_data['year']).to_dict()
    plays_per_drive = pd.Series(df_team_off_data['plays_per_drive'].values, index=df_team_off_data['year']).to_dict()
    yards_per_drive = pd.Series(df_team_off_data['yards_per_drive'].values, index=df_team_off_data['year']).to_dict()
    json_output.update({'pts_per_drive': pts_per_drive})
    json_output.update({'pts_per_game': pts_per_game})
    json_output.update({'scoring_percentage': scoring_percentage})
    json_output.update({'plays_per_drive': plays_per_drive})
    json_output.update({'yards_per_drive': yards_per_drive})
    json_output.update({'team_rz_att': rz_att})
    json_output.update({'team_rz_percentage': rz_percentage})


    # Get team rushing data
    rush_att = pd.Series(df_team_off_data['rush_att'].values, index=df_team_off_data['year']).to_dict()
    rush_yards = pd.Series(df_team_off_data['rush_yards'].values, index=df_team_off_data['year']).to_dict()
    rush_td = pd.Series(df_team_off_data['rush_td'].values, index=df_team_off_data['year']).to_dict()
    rush_yards_per_game = pd.Series(df_team_off_data['rush_yards_per_game'].values, index=df_team_off_data['year']).to_dict()
    rush_yards_per_att = pd.Series(df_team_off_data['rush_yards_per_att'].values, index=df_team_off_data['year']).to_dict()
    json_output.update({'team_rush_att': rush_att})
    json_output.update({'team_rush_yards': rush_yards})
    json_output.update({'team_rush_td': rush_td})
    json_output.update({'team_rush_yards_per_game': rush_yards_per_game})
    json_output.update({'team_rush_att_yards_per_att': rush_yards_per_att})


    # Get teams standings
    standings_query = f'''select * from nfl_standings
                where team_id = %s'''
    vals = [team_id]
    cursor.execute(standings_query, vals)

    standing_results = list(cursor.fetchall())
    standing_cols = ['id', 'year', 'team_id', 'wins', 'losses', 'ties', 'win_loss_percentage', 'points_for', 'points_against',
                     'point_diff', 'avg_margin_of_victory', 'strength_of_schedule']
    df_standings = pd.DataFrame(standing_results, columns=standing_cols).reset_index(drop=True)

    team_record_dict = {}
    for year in df_standings['year'].values.tolist():
        df_year = df_standings.loc[df_standings['year'] == year]
        record = f"{df_year['wins'].values.tolist()[0]}-{df_year['losses'].values.tolist()[0]}-{df_year['ties'].values.tolist()[0]}"
        team_record_dict[year] = record
    json_output.update({f"team_record": team_record_dict})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output


@nfl.route('/nfl/opponent_info', methods=['GET'])
def nfl_opponent_information():
    # initialize variables
    opp_id = int(request.args.get('opp_id', None))

    json_output = {}

    # Get team defense and rank stats
    connection = create_connection()
    cursor = connection.cursor()
    team_def_query = f'''SELECT * FROM nfl_team_defense'''

    cursor.execute(team_def_query)

    team_def_results = list(cursor.fetchall())
    cols = ['id', 'team_id', 'year', 'games', 'dvoa', 'epa_per_play', 'success_rate', 'dropback_epa', 'dropback_sr',
        'rush_epa', 'rush_sr', 'pass_comp', 'pass_att', 'pass_comp_percentage', 'pass_yards', 'pass_td', 'pass_td_percentage',
        'yards_per_att', 'pass_yards_per_comp', 'pass_yards_per_game', 'passer_rating', 'qb_hits', 'sacks', 'ints', 'int_percentage',
        'pass_deflections', 'rush_att', 'rush_yards', 'rush_td', 'rush_yards_per_att', 'rush_yards_per_game', 'points_per_game',
        'total_points', 'drives', 'plays', 'scoring_percentage', 'to_percentage', 'plays_per_drive', 'yards_per_drive',
        'points_per_drive', 'third_down_att', 'third_down_conv', 'third_down_conv_rate', 'fourth_down_att', 'fourth_down_conv',
        'fourth_down_conv_rate', 'rz_att', 'rz_td', 'rz_percentage', 'qb_rush_att', 'qb_rush_yards', 'qb_rush_td',
        'rb_att', 'rb_yards', 'rb_td', 'rb_targets', 'rb_rec', 'rb_rec_yards', 'rb_rec_td', 'wr_targets','wr_rec',
        'wr_yards', 'wr_td', 'te_targets', 'te_rec', 'te_yards', 'te_td']
    df_defense = pd.DataFrame(team_def_results, columns=cols).reset_index(drop=True)
    df_defense = df_defense.loc[df_defense['team_id'] == opp_id]

    # Vs position stats
    qb_rush_att = pd.Series(df_defense['qb_rush_att'].values, index=df_defense['year']).to_dict()
    qb_rush_yards = pd.Series(df_defense['qb_rush_yards'].values, index=df_defense['year']).to_dict()
    qb_rush_td = pd.Series(df_defense['qb_rush_td'].values, index=df_defense['year']).to_dict()
    rb_att = pd.Series(df_defense['rb_att'].values, index=df_defense['year']).to_dict()
    rb_yards = pd.Series(df_defense['rb_yards'].values, index=df_defense['year']).to_dict()
    rb_td = pd.Series(df_defense['rb_td'].values, index=df_defense['year']).to_dict()
    rb_targets = pd.Series(df_defense['rb_targets'].values, index=df_defense['year']).to_dict()
    rb_rec = pd.Series(df_defense['rb_rec'].values, index=df_defense['year']).to_dict()
    rb_rec_yards = pd.Series(df_defense['rb_rec_yards'].values, index=df_defense['year']).to_dict()
    rb_rec_td = pd.Series(df_defense['rb_rec_td'].values, index=df_defense['year']).to_dict()
    wr_targets = pd.Series(df_defense['wr_targets'].values, index=df_defense['year']).to_dict()
    wr_rec = pd.Series(df_defense['wr_rec'].values, index=df_defense['year']).to_dict()
    wr_yards = pd.Series(df_defense['wr_yards'].values, index=df_defense['year']).to_dict()
    wr_td = pd.Series(df_defense['wr_td'].values, index=df_defense['year']).to_dict()
    te_targets = pd.Series(df_defense['te_targets'].values, index=df_defense['year']).to_dict()
    te_rec = pd.Series(df_defense['te_rec'].values, index=df_defense['year']).to_dict()
    te_yards = pd.Series(df_defense['te_yards'].values, index=df_defense['year']).to_dict()
    te_td = pd.Series(df_defense['te_td'].values, index=df_defense['year']).to_dict()

    json_output.update({'qb_rush_att': qb_rush_att})
    json_output.update({'qb_rush_yards': qb_rush_yards})
    json_output.update({'qb_rush_td': qb_rush_td})
    json_output.update({'rb_att': rb_att})
    json_output.update({'rb_yards': rb_yards})
    json_output.update({'rb_td': rb_td})
    json_output.update({'rb_targets': rb_targets})
    json_output.update({'rb_rec': rb_rec})
    json_output.update({'rb_rec_yards': rb_rec_yards})
    json_output.update({'rb_rec_td': rb_rec_td})
    json_output.update({'wr_rec': wr_rec})
    json_output.update({'wr_targets': wr_targets})
    json_output.update({'wr_yards': wr_yards})
    json_output.update({'wr_td': wr_td})
    json_output.update({'te_targets': te_targets})
    json_output.update({'te_rec': te_rec})
    json_output.update({'te_yards': te_yards})
    json_output.update({'te_td': te_td})

    # Get team rushing data
    rush_att = pd.Series(df_defense['rush_att'].values, index=df_defense['year']).to_dict()
    rush_yards = pd.Series(df_defense['rush_yards'].values, index=df_defense['year']).to_dict()
    rush_td = pd.Series(df_defense['rush_td'].values, index=df_defense['year']).to_dict()
    rush_yards_per_game = pd.Series(df_defense['rush_yards_per_game'].values, index=df_defense['year']).to_dict()
    rush_yards_per_att = pd.Series(df_defense['rush_yards_per_att'].values, index=df_defense['year']).to_dict()
    json_output.update({'team_rush_att': rush_att})
    json_output.update({'team_rush_yards': rush_yards})
    json_output.update({'team_rush_td': rush_td})
    json_output.update({'team_rush_yards_per_game': rush_yards_per_game})
    json_output.update({'team_rush_att_yards_per_att': rush_yards_per_att})

    # Get teams scoring data
    pts_per_drive = pd.Series(df_defense['points_per_drive'].values, index=df_defense['year']).to_dict()
    pts_per_game = pd.Series(df_defense['points_per_game'].values, index=df_defense['year']).to_dict()
    scoring_percentage = pd.Series(df_defense['scoring_percentage'].values, index=df_defense['year']).to_dict()
    rz_att = pd.Series(df_defense['rz_att'].values, index=df_defense['year']).to_dict()
    rz_percentage = pd.Series(df_defense['rz_percentage'].values, index=df_defense['year']).to_dict()
    plays_per_drive = pd.Series(df_defense['plays_per_drive'].values, index=df_defense['year']).to_dict()
    yards_per_drive = pd.Series(df_defense['yards_per_drive'].values, index=df_defense['year']).to_dict()
    json_output.update({'pts_per_drive': pts_per_drive})
    json_output.update({'pts_per_game': pts_per_game})
    json_output.update({'scoring_percentage': scoring_percentage})
    json_output.update({'plays_per_drive': plays_per_drive})
    json_output.update({'yards_per_drive': yards_per_drive})
    json_output.update({'team_rz_att': rz_att})
    json_output.update({'team_rz_percentage': rz_percentage})

    # Get team passing data
    pass_comp = pd.Series(df_defense['pass_comp'].values, index=df_defense['year']).to_dict()
    pass_att = pd.Series(df_defense['pass_att'].values, index=df_defense['year']).to_dict()
    pass_comp_percentage = pd.Series(df_defense['pass_comp_percentage'].values, index=df_defense['year']).to_dict()
    pass_yards = pd.Series(df_defense['pass_yards'].values, index=df_defense['year']).to_dict()
    pass_td = pd.Series(df_defense['pass_td'].values, index=df_defense['year']).to_dict()
    pass_td_percentage = pd.Series(df_defense['pass_td_percentage'].values, index=df_defense['year']).to_dict()
    yards_per_att = pd.Series(df_defense['yards_per_att'].values, index=df_defense['year']).to_dict()
    pass_yards_per_game = pd.Series(df_defense['pass_yards_per_game'].values, index=df_defense['year']).to_dict()
    qb_hits = pd.Series(df_defense['qb_hits'].values, index=df_defense['year']).to_dict()
    int_percentage = pd.Series(df_defense['int_percentage'].values, index=df_defense['year']).to_dict()
    ints = pd.Series(df_defense['ints'].values, index=df_defense['year']).to_dict()
    json_output.update({'defense_pass_comp': pass_comp})
    json_output.update({'defense_pass_att': pass_att})
    json_output.update({'defense_pass_comp_percentage': pass_comp_percentage})
    json_output.update({'defense_pass_yards': pass_yards})
    json_output.update({'defense_pass_td': pass_td})
    json_output.update({'defense_pass_td_percentage': pass_td_percentage})
    json_output.update({'defense_yards_per_att': yards_per_att})
    json_output.update({'defense_pass_yards_per_game': pass_yards_per_game})
    json_output.update({'defense_qb_hits': qb_hits})
    json_output.update({'defense_int_percentage': int_percentage})
    json_output.update({'defense_ints': ints})




    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output










# UPLOAD/ADD ROUTES
@nfl.route('/nfl/games', methods=['POST', 'PUT'])
def nfl_game_info():
    file = request.files['nfl_game_info']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add Games:
        if flask.request.method == 'POST':
            json_dict = {'week': int(row['week']), 'year': int(row['year']), 'home_id': int(row['home_id']), 'home_score': int(row['home_score']),
                'away_id ': int(row['away_id']), 'away_score': int(row['away_score']), 'winner': int(row['winner']),
                'margin_of_victory': int(row['margin_of_victory']), 'weather_id': int(row['weather_id']), 'vegas_line': row['vegas_line'],
                'vegas_line_result': row['vegas_line_result'], 'over_under': float(row['over_under']), 'total_points': int(row['total_points']),
                'over_under_result': row['over_under_result']}
            values = list(json_dict.values())
            print(values)

            cursor.execute('''INSERT INTO nfl_games (week, year, home_id, home_score, away_id, away_score, winner, 
            margin_of_victory, weather_id, vegas_line, vegas_line_result, over_under, total_points, over_under_result) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (values))

        # Update Game Info:
        elif flask.request.method == 'PUT':
            json_dict = {'week': int(row['week']), 'year': int(row['year']), 'home_score': int(row['home_score']),
                     'away_score': int(row['away_score']), 'winner': int(row['winner']), 'margin_of_victory': int(row['margin_of_victory']),
                     'weather_id': int(row['weather_id']), 'vegas_line': row['vegas_line'], 'vegas_line_result': row['vegas_line_result'],
                     'over_under': float(row['over_under']), 'total_points': int(row['total_points']),
                     'over_under_result': row['over_under_result'], 'id': int(row['id']), 'home_id': int(row['home_id']),
                     'away_id': int(row['away_id'])}
            values = list(json_dict.values())

            cursor.execute('''UPDATE nfl_games
                    SET week = %s, year = %s, home_score = %s, away_score = %s, winner = %s, margin_of_victory = %s, weather_id = %s, vegas_line = %s,
                    vegas_line_result = %s, over_under = %s, total_points = %s, over_under_result = %s
                    WHERE nfl_games.id = %s AND nfl_games.home_id = %s AND nfl_games.away_id = %s''', (values))

        connection.commit()

    return f"nfl_games has been updated with the most recent game data."

@nfl.route('/nfl/team_defense', methods=['POST', 'PUT'])
def nfl_team_defense():
    file = request.files['nfl_team_defense']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add data
        if flask.request.method == 'POST':
            json_dict = {'team_id': row['team_id'], 'year': row['year'], 'games': row['games'],

                     'dvoa': row['dvoa'], 'epa_per_play': row['epa_per_play'], 'success_rate': row['success_rate'],
                     'dropback_epa': row['dropback_epa'], 'dropback_sr': row['dropback_sr'], 'rush_epa': row['rush_epa'],
                     'rush_sr': row['rush_sr'],

                     'pass_comp': row['pass_comp'], 'pass_att': row['pass_att'], 'pass_comp_percentage': row['pass_comp_percentage'],
                     'pass_yards': row['pass_yards'], 'pass_td': row['pass_td'], 'pass_td_percentage': row['pass_td_percentage'],
                     'yards_per_att': row['yards_per_att'],  'pass_yards_per_comp': row['pass_yards_per_comp'],
                     'pass_yards_per_game': row['pass_yards_per_game'], 'passer_rating': row['passer_rating'],
                     'qb_hits': row['qb_hits'], 'sacks': row['sacks'], 'ints': row['ints'], 'int_percentage': row['int_percentage'],
                     'pass_deflections': row['pass_deflections'],

                     'rush_att': row['rush_att'], 'rush_yards': row['rush_yards'], 'rush_td': row['rush_td'],
                     'rush_yards_per_att': row['rush_yards_per_att'], 'rush_yards_per_game': row['rush_yards_per_game'],

                     'points_per_game': row['points_per_game'], 'total_points': row['total_points'], 'drives': row['drives'],
                     'plays': row['plays'], 'scoring_percentage': row['scoring_percentage'], 'to_percentage': row['to_percentage'],
                     'plays_per_drive': row['plays_per_drive'], 'yards_per_drive': row['yards_per_drive'],
                     'points_per_drive': row['points_per_drive'],

                     'third_down_att': row['third_down_att'], 'third_down_conv': row['third_down_conv'],
                     'third_down_conv_rate': row['third_down_conv_rate'], 'fourth_down_att': row['fourth_down_att'],
                     'fourth_down_conv': row['fourth_down_conv'], 'fourth_down_conv_rate': row['fourth_down_conv_rate'],

                     'rz_att': row['rz_att'], 'rz_td': row['rz_td'], 'rz_percentage': row['rz_percentage'],

                     'qb_rush_att': row['qb_rush_att'], 'qb_rush_yards': row['qb_rush_yards'], 'qb_rush_td': row['qb_rush_td'],
                     'rb_att': row['rb_att'], 'rb_yards': row['rb_yards'], 'rb_td': row['rb_td'], 'rb_targets': row['rb_targets'],
                     'rb_rec': row['rb_rec'], 'rb_rec_yards': row['rb_rec_yards'], 'rb_rec_td': row['rb_rec_td'],
                     'wr_targets': row['wr_targets'], 'wr_rec': row['wr_rec'], 'wr_yards': row['wr_yards'], 'wr_td': row['wr_td'],
                     'te_targets': row['te_targets'], 'te_rec': row['te_rec'], 'te_yards': row['te_yards'], 'te_td': row['te_td']}
            values = list(json_dict.values())

            cursor.execute('''INSERT INTO nfl_team_defense (team_id, year, games, dvoa, epa_per_play, success_rate, dropback_epa, 
            dropback_sr, rush_epa, rush_sr, pass_comp, pass_att, pass_comp_percentage, pass_yards, pass_td, pass_td_percentage,
            yards_per_att, pass_yards_per_comp, pass_yards_per_game, passer_rating, qb_hits, sacks, ints, int_percentage, 
            pass_deflections, rush_att, rush_yards, rush_td, rush_yards_per_att, rush_yards_per_game, points_per_game, total_points, 
            drives, plays, scoring_percentage, to_percentage, plays_per_drive, yards_per_drive, points_per_drive, third_down_att,
            third_down_conv, third_down_conv_rate, fourth_down_att, fourth_down_conv, fourth_down_conv_rate, rz_att, rz_td, 
            rz_percentage, qb_rush_att, qb_rush_yards, qb_rush_td, rb_att, rb_yards, rb_td, rb_targets, rb_rec, rb_rec_yards,
            rb_rec_td, wr_targets, wr_rec, wr_yards, wr_td, te_targets, te_rec, te_yards, te_td) VALUES (%s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s)''', (values))

        # Update data
        elif flask.request.method == 'PUT':
            json_dict = {'games': row['games'],

                         'dvoa': row['dvoa'], 'epa_per_play': row['epa_per_play'], 'success_rate': row['success_rate'],
                         'dropback_epa': row['dropback_epa'], 'dropback_sr': row['dropback_sr'], 'rush_epa': row['rush_epa'],
                         'rush_sr': row['rush_sr'],

                         'pass_comp': row['pass_comp'], 'pass_att': row['pass_att'], 'pass_comp_percentage': row['pass_comp_percentage'],
                         'pass_yards': row['pass_yards'], 'pass_td': row['pass_td'], 'pass_td_percentage': row['pass_td_percentage'],
                         'yards_per_att': row['yards_per_att'], 'pass_yards_per_comp': row['pass_yards_per_comp'],
                         'pass_yards_per_game': row['pass_yards_per_game'], 'passer_rating': row['passer_rating'],
                         'qb_hits': row['qb_hits'], 'sacks': row['sacks'], 'ints': row['ints'], 'int_percentage': row['int_percentage'],
                         'pass_deflections': row['pass_deflections'],

                         'rush_att': row['rush_att'], 'rush_yards': row['rush_yards'], 'rush_td': row['rush_td'],
                         'rush_yards_per_att': row['rush_yards_per_att'], 'rush_yards_per_game': row['rush_yards_per_game'],

                         'points_per_game': row['points_per_game'], 'total_points': row['total_points'], 'drives': row['drives'],
                         'plays': row['plays'], 'scoring_percentage': row['scoring_percentage'], 'to_percentage': row['to_percentage'],
                         'plays_per_drive': row['plays_per_drive'], 'yards_per_drive': row['yards_per_drive'],
                         'points_per_drive': row['points_per_drive'],

                         'third_down_att': row['third_down_att'], 'third_down_conv': row['third_down_conv'],
                         'third_down_conv_rate': row['third_down_conv_rate'], 'fourth_down_att': row['fourth_down_att'],
                         'fourth_down_conv': row['fourth_down_conv'], 'fourth_down_conv_rate': row['fourth_down_conv_rate'],

                         'rz_att': row['rz_att'], 'rz_td': row['rz_td'], 'rz_percentage': row['rz_percentage'],

                         'qb_rush_att': row['qb_rush_att'], 'qb_rush_yards': row['qb_rush_yards'], 'qb_rush_td': row['qb_rush_td'],
                         'rb_att': row['rb_att'], 'rb_yards': row['rb_yards'], 'rb_td': row['rb_td'],'rb_targets': row['rb_targets'],
                         'rb_rec': row['rb_rec'], 'rb_rec_yards': row['rb_rec_yards'], 'rb_rec_td': row['rb_rec_td'],
                         'wr_targets': row['wr_targets'], 'wr_rec': row['wr_rec'], 'wr_yards': row['wr_yards'], 'wr_td': row['wr_td'],
                         'te_targets': row['te_targets'], 'te_rec': row['te_rec'], 'te_yards': row['te_yards'], 'te_td': row['te_td'],

                         'team_id': row['team_id'], 'year': row['year']}
            values = list(json_dict.values())
            print(values)

            cursor.execute("""UPDATE nfl_team_defense
                SET games = %s, dvoa = %s, epa_per_play = %s, success_rate = %s, dropback_epa = %s, dropback_sr = %s, rush_epa = %s, 
                rush_sr = %s, pass_comp = %s, pass_att = %s, pass_comp_percentage = %s, pass_yards = %s, pass_td = %s, 
                pass_td_percentage = %s, yards_per_att = %s, pass_yards_per_comp = %s, pass_yards_per_game = %s, passer_rating = %s, 
                qb_hits = %s, sacks = %s, ints = %s, int_percentage = %s, pass_deflections = %s, rush_att = %s, rush_yards = %s,
                rush_td = %s, rush_yards_per_att = %s, rush_yards_per_game = %s, points_per_game = %s, total_points = %s, drives = %s, 
                plays = %s, scoring_percentage = %s, to_percentage = %s, plays_per_drive = %s, yards_per_drive = %s, points_per_drive = %s,
                third_down_att = %s, third_down_conv = %s, third_down_conv_rate = %s, fourth_down_att = %s, fourth_down_conv = %s,
                fourth_down_conv_rate = %s, rz_att = %s, rz_td = %s, rz_percentage = %s, qb_rush_att = %s, qb_rush_yards = %s,
                qb_rush_td = %s, rb_att = %s, rb_yards = %s, rb_td = %s, rb_targets = %s, rb_rec = %s, rb_rec_yards = %s,
                rb_rec_td = %s, wr_targets = %s, wr_rec = %s, wr_yards = %s, wr_td = %s, te_targets = %s, te_rec = %s, te_yards = %s, te_td = %s
                WHERE nfl_team_defense.team_id = %s AND nfl_team_defense.year = %s""", (values))

        connection.commit()

    return f"nfl_team_defense has been updated with the most recent years data."

@nfl.route('/nfl/team_offense', methods=['POST', 'PUT'])
def nfl_team_offense():
    file = request.files['nfl_team_offense']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add data
        if flask.request.method == 'POST':
            json_dict = {'team_id': row['team_id'],
                         'year': row['year'],
                         'games': row['games'],
                         'dvoa': row['dvoa'],
                         'epa_per_play': row['epa_per_play'],
                         'success_rate': row['success_rate'],
                         'dropback_epa': row['dropback_epa'],
                         'dropback_sr': row['dropback_sr'],
                         'rush_epa': row['rush_epa'],
                         'rush_sr': row['rush_sr'],
                         'pass_comp': row['pass_comp'],
                         'pass_att': row['pass_att'],
                         'pass_comp_percentage': row['pass_comp_percentage'],
                         'pass_yards': row['pass_yards'],
                         'pass_td': row['pass_td'],
                         'pass_td_percentage': row['pass_td_percentage'],
                         'yards_per_att': row['yards_per_att'],
                         'pass_yards_per_comp': row['pass_yards_per_comp'],
                         'pass_yards_per_game': row['pass_yards_per_game'],
                         'passer_rating': row['passer_rating'],
                         'sacks': row['sacks'],
                         'ints': row['ints'],
                         'int_percentage': row['int_percentage'],
                         'rush_att': row['rush_att'],
                         'rush_yards': row['rush_yards'],
                         'rush_td': row['rush_td'],
                         'rush_yards_per_att': row['rush_yards_per_att'],
                         'rush_yards_per_game': row['rush_yards_per_game'],
                         'fumbles': row['fumbles'],
                         'points_per_game': row['points_per_game'],
                         'total_points': row['total_points'],
                         'drives': row['drives'],
                         'plays': row['plays'],
                         'scoring_percentage': row['scoring_percentage'],
                         'to_percentage': row['to_percentage'],
                         'plays_per_drive': row['plays_per_drive'],
                         'yards_per_drive': row['yards_per_drive'],
                         'points_per_drive': row['points_per_drive'],
                         'third_down_att': row['third_down_att'],
                         'third_down_conv': row['third_down_conv'],
                         'third_down_conv_rate': row['third_down_conv_rate'],
                         'fourth_down_att': row['fourth_down_att'],
                         'fourth_down_conv': row['fourth_down_conv'],
                         'fourth_down_conv_rate': row['fourth_down_conv_rate'],
                         'rz_att': row['rz_att'],
                         'rz_td': row['rz_td'],
                         'rz_percentage': row['rz_percentage']}
            values = list(json_dict.values())

            cursor.execute("""INSERT INTO nfl_team_offense (team_id, year, games, dvoa, epa_per_play, success_rate, dropback_epa,
             dropback_sr, rush_epa, rush_sr, pass_comp, pass_att, pass_comp_percentage, pass_yards, pass_td, pass_td_percentage, 
             yards_per_att, pass_yards_per_comp, pass_yards_per_game, passer_rating, sacks, ints, int_percentage, 
             rush_att, rush_yards, rush_td, rush_yards_per_att, rush_yards_per_game, fumbles, points_per_game, total_points,
             drives, plays, scoring_percentage, to_percentage, plays_per_drive, yards_per_drive, points_per_drive, third_down_att,
             third_down_conv, third_down_conv_rate, fourth_down_att, fourth_down_conv, fourth_down_conv_rate, rz_att, rz_td, rz_percentage) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

        # Update Data
        elif flask.request.method == 'PUT':
            json_dict = {'games': row['games'],
                         'dvoa': row['dvoa'],
                         'epa_per_play': row['epa_per_play'],
                         'success_rate': row['success_rate'],
                         'dropback_epa': row['dropback_epa'],
                         'dropback_sr': row['dropback_sr'],
                         'rush_epa': row['rush_epa'],
                         'rush_sr': row['rush_sr'],
                         'pass_comp': row['pass_comp'],
                         'pass_att': row['pass_att'],
                         'pass_comp_percentage': row['pass_comp_percentage'],
                         'pass_yards': row['pass_yards'],
                         'pass_td': row['pass_td'],
                         'pass_td_percentage': row['pass_td_percentage'],
                         'yards_per_att': row['yards_per_att'],
                         'pass_yards_per_comp': row['pass_yards_per_comp'],
                         'pass_yards_per_game': row['pass_yards_per_game'],
                         'passer_rating': row['passer_rating'],
                         'sacks': row['sacks'],
                         'ints': row['ints'],
                         'int_percentage': row['int_percentage'],
                         'rush_att': row['rush_att'],
                         'rush_yards': row['rush_yards'],
                         'rush_td': row['rush_td'],
                         'rush_yards_per_att': row['rush_yards_per_att'],
                         'rush_yards_per_game': row['rush_yards_per_game'],
                         'fumbles': row['fumbles'],
                         'points_per_game': row['points_per_game'],
                         'total_points': row['total_points'],
                         'drives': row['drives'],
                         'plays': row['plays'],
                         'scoring_percentage': row['scoring_percentage'],
                         'to_percentage': row['to_percentage'],
                         'plays_per_drive': row['plays_per_drive'],
                         'yards_per_drive': row['yards_per_drive'],
                         'points_per_drive': row['points_per_drive'],
                         'third_down_att': row['third_down_att'],
                         'third_down_conv': row['third_down_conv'],
                         'third_down_conv_rate': row['third_down_conv_rate'],
                         'fourth_down_att': row['fourth_down_att'],
                         'fourth_down_conv': row['fourth_down_conv'],
                         'fourth_down_conv_rate': row['fourth_down_conv_rate'],
                         'rz_att': row['rz_att'],
                         'rz_td': row['rz_td'],
                         'rz_percentage': row['rz_percentage'],
                         'team_id': row['team_id'],
                         'year': row['year']}
            values = list(json_dict.values())

            cursor.execute("""UPDATE nfl_team_offense 
                    SET games = %s, dvoa = %s, epa_per_play = %s, success_rate = %s, dropback_epa = %s, dropback_sr = %s, 
                    rush_epa = %s, rush_sr = %s, pass_comp = %s, pass_att = %s, pass_comp_percentage = %s, pass_yards = %s, 
                    pass_td = %s, pass_td_percentage = %s, yards_per_att = %s, pass_yards_per_comp = %s, pass_yards_per_game = %s,
                    passer_rating = %s, sacks = %s, ints = %s, int_percentage = %s, rush_att = %s, rush_yards = %s, 
                    rush_td = %s, rush_yards_per_att = %s, rush_yards_per_game = %s, fumbles = %s, points_per_game = %s,
                    total_points = %s,, drives = %s, plays = %s, scoring_percentage = %s, to_percentage = %s, plays_per_drive = %s, 
                    yards_per_drive = %s, points_per_drive = %s, third_down_att = %s, third_down_conv = %s, third_down_conv_rate = %s, 
                    fourth_down_att = %s, fourth_down_conv = %s, fourth_down_conv_rate = %s, rz_att = %s, rz_td = %s, rz_percentage = %s
                    WHERE nfl_team_offense.team_id = %s AND nfl_team_offense.year = %s""",(values))

        connection.commit()

    return f"nfl_team_offense has been updated with the most recent years data."

@nfl.route('/nfl/standings', methods=['POST', 'PUT'])
def nfl_standings():
    file = request.files['nfl_standings']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add data
        if flask.request.method == 'POST':
            json_dict = {'year': row['year'],
                         'team_id': row['team_id'],
                         'wins': row['wins'],
                         'losses': row['losses'],
                         'ties': row['ties'],
                         'win_loss_percentage': row['win_loss_percentage'],
                         'points_for': row['points_for'],
                         'points_against': row['points_against'],
                         'point_diff': row['point_diff'],
                         'avg_margin_of_victory': row['avg_margin_of_victory'],
                         'strength_of_schedule': row['strength_of_schedule']}
            values = list(json_dict.values())

            cursor.execute("""INSERT INTO nfl_standings (year, team_id, wins, losses, ties, win_loss_percentage, points_for, 
                            points_against, point_diff,
                            avg_margin_of_victory, strength_of_schedule) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (values))
        # Update Data
        elif flask.request.method == 'PUT':
            json_dict = {'wins': row['wins'],
                         'losses': row['losses'],
                         'ties': row['ties'],
                         'win_loss_percentage': row['win_loss_percentage'],
                         'points_for': row['points_for'],
                         'points_against': row['points_against'],
                         'point_diff': row['point_diff'],
                         'avg_margin_of_victory': row['avg_margin_of_victory'],
                         'strength_of_schedule': row['strength_of_schedule'],
                         'team_id': row['team_id'],
                         'year': row['year']}
            values = list(json_dict.values())

            cursor.execute("""UPDATE  nfl_standings 
                        SET wins = %s, losses = %s, ties = %s, win_loss_percentage = %s, points_for = %s,
                         points_against = %s, point_diff = %s, avg_margin_of_victory = %s, strength_of_schedule = %s
                        WHERE nfl_standings.team_id = %s and nfl_standings.year = %s""", (values))

        connection.commit()

    return f"nfl_team_offense has been updated with the most recent years data."

@nfl.route('/nfl/red_zone', methods=['POST', 'PUT'])
def nfl_red_zone():
    file = request.files['nfl_red_zone']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add data
        if flask.request.method == 'POST':
            json_dict = {'player_id': row['player_id'],
                         'year': row['year'],
                         'rz_20_pass_att': row['rz_20_pass_att'],
                         'rz_20_pass_comp': row['rz_20_pass_comp'],
                         'rz_20_comp_percentage': row['rz_20_comp_percentage'],
                         'rz_20_pass_yards': row['rz_20_pass_yards'],
                         'rz_20_pass_td': row['rz_20_pass_td'],
                         'rz_20_pass_int': row['rz_20_pass_int'],
                         'rz_10_pass_att': row['rz_10_pass_att'],
                         'rz_10_pass_comp': row['rz_10_pass_comp'],
                         'rz_10_comp_percentage': row['rz_10_comp_percentage'],
                         'rz_10_pass_yards': row['rz_10_pass_yards'],
                         'rz_10_pass_td': row['rz_10_pass_td'],
                         'rz_10_pass_int': row['rz_10_pass_int'],
                         'rz_20_targets': row['rz_20_targets'],
                         'rz_20_receptions': row['rz_20_receptions'],
                         'rz_20_rec_yards': row['rz_20_rec_yards'],
                         'rz_20_catch_percentage': row['rz_20_catch_percentage'],
                         'rz_20_rec_td': row['rz_20_rec_td'],
                         'rz_20_target_percentage': row['rz_20_target_percentage'],
                         'rz_10_targets': row['rz_10_targets'],
                         'rz_10_receptions': row['rz_10_receptions'],
                         'rz_10_rec_yards': row['rz_10_rec_yards'],
                         'rz_10_catch_percentage': row['rz_10_catch_percentage'],
                         'rz_10_rec_td': row['rz_10_rec_td'],
                         'rz_10_target_percentage': row['rz_10_target_percentage'],
                         'rz_20_rush_att': row['rz_20_rush_att'],
                         'rz_20_rush_yards': row['rz_20_rush_yards'],
                         'rz_20_rush_td': row['rz_20_rush_td'],
                         'rz_20_rush_percentage': row['rz_20_rush_percentage'],
                         'rz_10_rush_att': row['rz_10_rush_att'],
                         'rz_10_rush_yards': row['rz_10_rush_yards'],
                         'rz_10_rush_td': row['rz_10_rush_td'],
                         'rz_10_rush_percentage': row['rz_10_rush_percentage'],
                         'rz_5_rush_att': row['rz_5_rush_att'],
                         'rz_5_rush_yards': row['rz_5_rush_yards'],
                         'rz_5_rush_td': row['rz_5_rush_td'],
                         'rz_5_rush_percentage': row['rz_5_rush_percentage']}
            values = list(json_dict.values())

            cursor.execute("""INSERT INTO nfl_redzone_stats (player_id, year, rz_20_pass_att, rz_20_pass_comp, rz_20_comp_percentage,
                 rz_20_pass_yards, rz_20_pass_td, rz_20_pass_int, rz_10_pass_att, rz_10_pass_comp, rz_10_comp_percentage, 
                 rz_10_pass_yards, rz_10_pass_td, rz_10_pass_int, rz_20_targets, rz_20_receptions, rz_20_rec_yards, 
                 rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions, rz_10_rec_yards,
                 rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_yards, rz_20_rush_td,
                 rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_yards, rz_10_rush_td, rz_10_rush_percentage, rz_5_rush_att, 
                 rz_5_rush_yards, rz_5_rush_td, rz_5_rush_percentage) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

        # Update Data
        elif flask.request.method == 'PUT':
            json_dict = {'rz_20_pass_att': row['rz_20_pass_att'],
                         'rz_20_pass_comp': row['rz_20_pass_comp'],
                         'rz_20_comp_percentage': row['rz_20_comp_percentage'],
                         'rz_20_pass_yards': row['rz_20_pass_yards'],
                         'rz_20_pass_td': row['rz_20_pass_td'],
                         'rz_20_pass_int': row['rz_20_pass_int'],
                         'rz_10_pass_att': row['rz_10_pass_att'],
                         'rz_10_pass_comp': row['rz_10_pass_comp'],
                         'rz_10_comp_percentage': row['rz_10_comp_percentage'],
                         'rz_10_pass_yards': row['rz_10_pass_yards'],
                         'rz_10_pass_td': row['rz_10_pass_td'],
                         'rz_10_pass_int': row['rz_10_pass_int'],
                         'rz_20_targets': row['rz_20_targets'],
                         'rz_20_receptions': row['rz_20_receptions'],
                         'rz_20_rec_yards': row['rz_20_rec_yards'],
                         'rz_20_catch_percentage': row['rz_20_catch_percentage'],
                         'rz_20_rec_td': row['rz_20_rec_td'],
                         'rz_20_target_percentage': row['rz_20_target_percentage'],
                         'rz_10_targets': row['rz_10_targets'],
                         'rz_10_receptions': row['rz_10_receptions'],
                         'rz_10_rec_yards': row['rz_10_rec_yards'],
                         'rz_10_catch_percentage': row['rz_10_catch_percentage'],
                         'rz_10_rec_td': row['rz_10_rec_td'],
                         'rz_10_target_percentage': row['rz_10_target_percentage'],
                         'rz_20_rush_att': row['rz_20_rush_att'],
                         'rz_20_rush_yards': row['rz_20_rush_yards'],
                         'rz_20_rush_td': row['rz_20_rush_td'],
                         'rz_20_rush_percentage': row['rz_20_rush_percentage'],
                         'rz_10_rush_att': row['rz_10_rush_att'],
                         'rz_10_rush_yards': row['rz_10_rush_yards'],
                         'rz_10_rush_td': row['rz_10_rush_td'],
                         'rz_10_rush_percentage': row['rz_10_rush_percentage'],
                         'rz_5_rush_att': row['rz_5_rush_att'],
                         'rz_5_rush_yards': row['rz_5_rush_yards'],
                         'rz_5_rush_td': row['rz_5_rush_td'],
                         'rz_5_rush_percentage': row['rz_5_rush_percentage'],
                         'player_id': row['player_id'],
                         'year': row['year']}
            values = list(json_dict.values())

            cursor.execute("""UPDATE nfl_redzone_stats 
                    SET rz_20_pass_att = %s, rz_20_pass_comp = %s, rz_20_comp_percentage = %s, rz_20_pass_yards = %s, rz_20_pass_td = %s, rz_20_pass_int = %s,
                        rz_10_pass_att = %s, rz_10_pass_comp = %s, rz_10_comp_percentage = %s, rz_10_pass_yards = %s, rz_10_pass_td = %s, 
                        rz_10_pass_int = %s, rz_20_targets = %s, rz_20_receptions = %s, rz_20_rec_yards = %s, rz_20_catch_percentage = %s, 
                        rz_20_rec_td = %s, rz_20_target_percentage = %s, rz_10_targets = %s, rz_10_receptions = %s, rz_10_rec_yards = %s, 
                        rz_10_catch_percentage = %s, rz_10_rec_td = %s, rz_10_target_percentage = %s, rz_20_rush_att = %s, rz_20_rush_td = %s,
                        rz_20_rush_yards = %s, rz_20_rush_percentage = %s, rz_10_rush_att = %s, rz_10_rush_td = %s, rz_10_rush_yards = %s, 
                        rz_10_rush_percentage = %s, rz_5_rush_att = %s, rz_5_rush_td = %s, rz_5_rush_yards = %s, rz_5_rush_percentage = %s 
                    WHERE nfl_redzone_stats.player_id = %s AND nfl_redzone_stats.year = %s""", (values))

        connection.commit()

    return f"nfl_redzone_stats has been updated with the most recent years data."

@nfl.route('/nfl/player_stats', methods=['POST'])
def nfl_player_stats():
    file = request.files['nfl_game_log']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        json_dict = {'game_id': int(row['game_id']),
                     'player_id': int(row['player_id']),
                     'team_id': int(row['team_id']),
                     'opp_id': int(row['opp_id']),
                     'pass_att': int(row['pass_att']),
                     'pass_comp': int(row['pass_comp']),
                     'pass_yards': int(row['pass_yards']),
                     'pass_td': int(row['pass_td']),
                     'pass_longest': int(row['pass_longest']),
                     'int': int(row['int']),
                     'sacks': int(row['sacks']),
                     'rush_att': int(row['rush_att']),
                     'rush_yards': int(row['rush_yards']),
                     'rush_td': int(row['rush_td']),
                     'rush_longest': int(row['rush_longest']),
                     'targets': int(row['targets']),
                     'rec': int(row['rec']),
                     'rec_yards': int(row['rec_yards']),
                     'rec_td': int(row['rec_td']),
                     'rec_longest': int(row['rec_longest']),
                     'fumbles': int(row['fumbles'])}
        values = list(json_dict.values())

        cursor.execute("""INSERT INTO nfl_player_stats (game_id, player_id, team_id, opp_id, pass_att, pass_comp, pass_yards, pass_td, pass_longest, 
                        ints, sacks, rush_att, rush_yards, rush_td, rush_longest, targets, rec, rec_yards, rec_td, rec_longest, fumbles) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       (values))

        connection.commit()
        print(f"game_stats have been added to nfl_player_stats table.")


    return f"nfl_player_stats has been u[dated ."


@nfl.route('/nfl/weekly_rank', methods=['POST'])
def nfl_weekly_ranks():
    file = request.files['nfl_weekly_rank']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        json_dict = {'team_id': int(row['team_id']),
                     'year': int(row['year']),
                     'week': int(row['week']),
                     'pass_att': int(row['pass_att']),
                     'pass_comp': int(row['pass_comp']),
                     'pass_yards': int(row['pass_yards']),
                     'pass_td': int(row['pass_td']),
                     'rush_att': int(row['rush_att']),
                     'rush_yards': int(row['rush_yards']),
                     'rush_td': int(row['rush_td']),
                     'targets': int(row['targets']),
                     'rec': int(row['rec']),
                     'rec_yards': int(row['rec_yards']),
                     'rec_td': int(row['rec_td']),
                     'pyards_per_att': float(row['pyards_per_att']),
                     'ryards_per_att': float(row['ryards_per_att']),
                     'ryards_per_recs': float(row['ryards_per_recs']),
                     'pass_yards_rank': int(row['pass_yards_rank']),
                     'rush_yards_rank': int(row['rush_yards_rank']),
                     'rec_yards_rank': int(row['rec_yards_rank']),
                     'pass_td_rank': int(row['pass_td_rank']),
                     'rush_td_rank': int(row['rush_td_rank']),
                     'rec_td_rank': int(row['rec_td_rank']),
                     'pass_comp_rank': int(row['pass_comp_rank']),
                     'rush_att_rank': int(row['rush_att_rank']),
                     'rec_rank': int(row['rec_rank']),
                     'pass_yards_per_att_rank': int(row['pass_yards_per_att_rank']),
                     'rush_yards_per_att_rank': int(row['rush_yards_per_att_rank']),
                     'rec_yards_per_rec_rank': int(row['rec_yards_per_rec_rank'])}
        values = list(json_dict.values())

        cursor.execute("""INSERT INTO nfl_weekly_rank (team_id, year, week, pass_att, pass_comp, pass_yards,
         pass_td, rush_att, rush_yards, rush_td, targets, rec, rec_yards, rec_td, pyards_per_att, 
         ryards_per_att, ryards_per_recs, pass_yards_rank, rush_yards_rank, rec_yards_rank, pass_td_rank, rush_td_rank,
         rec_td_rank, pass_comp_rank, rush_att_rank, rec_rank, pass_yards_per_att_rank, rush_yards_per_att_rank, rec_yards_per_rec_rank) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, %s)""",
           (values))

        connection.commit()
        print(f"game_stats have been added to nfl_player_stats table.")


    return f"nfl_weekly_rank has been updated ."
