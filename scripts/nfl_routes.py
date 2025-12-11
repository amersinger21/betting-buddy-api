import pandas as pd
import numpy as np
import statistics

from .db import create_connection
import flask
from flask import Blueprint, request, jsonify

nfl = Blueprint("nfl", __name__)
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 1000)

nfl_fifth_year = 2021
nfl_fourth_year = 2022
nfl_third_year = 2023
nfl_prior_year = 2024
nfl_current_year = 2025
nfl_current_week = 11
nfl_next_week = nfl_current_week + 1

year_name_dict = {2019: 'six_years_ago', 2020: 'five_years_ago' , 2021: 'fifth',
                  2022: 'fourth', 2023: 'third', 2024: 'prior', 2025: 'current'}
limit_stat_dict = {'pass_att': 'pass_att', 'pass_yards': 'pass_att', 'pass_td': 'pass_att', 'pass_comp': 'pass_att',
                   'pass_longest': 'pass_att',
                   'rush_att': 'rush_att', 'rush_yards': 'rush_att', 'rush_td': 'rush_att', 'rush_longest': 'rush_att',
                   'rec': 'targets', 'targets': 'targets', 'rec_yards': 'targets', 'rec_td': 'targets',
                   'rec_longest': 'targets'}
pass_stat_list = ['pass_att', 'pass_yards', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest']

# GET ROUTES (PLAYER DATA)
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

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
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

    # GET BIN AND RANGE DICT BASED ON COLUMN NAME
    if column_name in ['pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest']:
        bins = [0, 150, 175, 200, 225, 250, 275, 300, 350, 400, 10000]
        range_dict = {'0-150yds': 0, '151-175yds': 0, '176-200yds': 0, '201-225yds': 0, '226-250yds': 0,
                      '251-275yds': 0,
                      '276-300yds': 0, '301-350yds': 0, '351-400yds': 0, '401+': 0}
    else:
        bins = [0, 10, 25, 40, 50, 60, 70, 80, 90, 100, 10000]
        range_dict = {'0-10yds': 0, '11-25yds': 0, '26-40yds': 0, '41-50yds': 0, '51-60yds': 0, '61-70yds': 0,
                      '71-80yds': 0, '81-90yds': 0, '91-100yds': 0, '101+': 0}
    yardage_ranges_total = df_logs[column_name].value_counts(bins=bins, sort=False)
    json_output.update({f"yardage_ranges_total": dict(zip(list(range_dict.keys()), list(yardage_ranges_total)))})

    for year in np.unique(df_logs['year'].values):
        # GET WEEKS BETWEEN BET OCCURRENCES
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

        # GROUP PLAYER TOTAL STAT AMOUNTS IN RANGES
        yardage_ranges = df_year[column_name].value_counts(bins=bins, sort=False)
        json_output.update(
            {f"yardage_ranges_{year_name_dict[year]}": dict(zip(list(range_dict.keys()), list(yardage_ranges)))})


    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output

# @nfl.route('/nfl/player/home_road_splits', methods=['GET'])


@nfl.route('/nfl/player/red_zone', methods=['GET'])
def nfl_get_player_redzone_stats():
    player_id = request.args.get('id', None)
    column_name = request.args.get('stat', None)
    json_output = {}

    if column_name in ['pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest', 'int', 'sack']:
        columns = f'''player_id, rz_20_pass_att, rz_20_pass_td'''
        df_columns = ['name', 'year', 'pos', 'player_id', 'rz_20_pass_att', 'rz_20_pass_td']
    elif column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest', 'fumbles']:
        columns = f'''player_id, rz_20_rush_att, rz_20_rush_td, rz_20_rush_percentage, rz_10_rush_percentage,
                      rz_5_rush_percentage'''
        df_columns = ['name', 'year', 'pos', 'player_id', 'rz_20_rush_att', 'rz_20_rush_td', 'rz_20_rush_percentage',
                      'rz_10_rush_percentage', 'rz_5_rush_percentage']
    else:
        columns = f'''player_id, rz_20_targets, rz_20_receptions, rz_20_rec_td, rz_20_target_percentage'''
        df_columns = ['name', 'year', 'pos', 'player_id', 'rz_20_targets', 'rz_20_receptions', 'rz_20_rec_td',
        'rz_20_target_percentage',]

    connection = create_connection()
    cursor = connection.cursor()

    player_rz_query = f'''SELECT CONCAT(player.first_name, ' ', player.last_name), nfl_redzone_stats.year, player.position, {columns}
                FROM nfl_redzone_stats
                JOIN player ON player.id = nfl_redzone_stats.player_id
                WHERE nfl_redzone_stats.player_id = {player_id}'''
    cursor.execute(player_rz_query)
    rz_results = list(cursor.fetchall())

    df_rz_player = pd.DataFrame(rz_results, columns=df_columns).reset_index(drop=True)

    if column_name in ['pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest', 'int', 'sack']:
        json_output.update({f"rz_pass_att_total": int(df_rz_player['rz_20_pass_att'].values.sum())})
        json_output.update({f"rz_pass_td_total": int(df_rz_player['rz_20_pass_td'].values.sum())})
    elif column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest', 'fumbles']:
        json_output.update({f"rz_rush_att_total": int(df_rz_player['rz_20_rush_att'].values.sum())})
        json_output.update({f"rush_td_total": int(df_rz_player['rz_20_rush_td'].values.sum())})
        json_output.update(
            {f"rush_percentage_total": round(float(df_rz_player['rz_20_rush_percentage'].values.mean()), 1)})
        json_output.update(
            {f"rush_percentage_10_yds": round(float(df_rz_player['rz_10_rush_percentage'].values.mean()), 1)})
        json_output.update(
            {f"rush_percentage_5_yds": round(float(df_rz_player['rz_5_rush_percentage'].values.mean()), 1)})
    else:
        json_output.update({f"rz_targets_total": int(df_rz_player['rz_20_targets'].values.sum())})
        json_output.update(
            {f"rz_tgt_percentage_total": round(float(df_rz_player['rz_20_target_percentage'].values.mean()), 1)})
        json_output.update({f"rz_rec_total": int(df_rz_player['rz_20_receptions'].values.sum())})
        json_output.update({f"rz_td_total": int(df_rz_player['rz_20_rec_td'].values.sum())})

    for year in np.unique(df_rz_player['year'].values):
        df_year = df_rz_player[df_rz_player['year'] == year]

        if column_name in ['pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest', 'int', 'sack']:
            json_output.update({f"rz_pass_att_{year_name_dict[year]}": int(df_year['rz_20_pass_att'].values)})
            json_output.update({f"rz_pass_td_{year_name_dict[year]}": int(df_year['rz_20_pass_td'].values)})
        elif column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest', 'fumbles']:
            json_output.update({f"rz_rush_att_{year_name_dict[year]}": int(df_year['rz_20_rush_att'].values)})
            json_output.update({f"rush_td_{year_name_dict[year]}": int(df_year['rz_20_rush_td'].values)})
            json_output.update(
                {f"rush_percentage_{year_name_dict[year]}": float(df_year['rz_20_rush_percentage'].values)})
            json_output.update(
                {f"rush_percentage_10_yds_{year_name_dict[year]}": round(float(df_rz_player['rz_10_rush_percentage'].values.mean()), 1)})
            json_output.update(
                {f"rush_percentage_5_yds_{year_name_dict[year]}": round(float(df_rz_player['rz_5_rush_percentage'].values.mean()), 1)})
        else:
            json_output.update({f"rz_targets_{year_name_dict[year]}": int(df_year['rz_20_targets'].values)})
            json_output.update(
                {f"rz_tgt_percentage_{year_name_dict[year]}": float(df_year['rz_20_target_percentage'].values)})
            json_output.update({f"rz_rec_{year_name_dict[year]}": int(df_year['rz_20_receptions'].values)})
            json_output.update({f"rz_td_{year_name_dict[year]}": int(df_year['rz_20_rec_td'].values)})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output



# GET ROUTES (TEAM DATA)
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
    try:
        json_output.update({'vs_player_bet_occurrences': round(
            (len(vs_player_bet_occurrences.index) / opp_games_vs_player_count) * 100, 1)})
        json_output.update({'vs_player_game_logs': opp_logs_vs_player.to_json()})
    except ZeroDivisionError:
        json_output.update({'vs_player_bet_occurrences': 0})
        json_output.update({'vs_player_game_logs': 0})


    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output

@nfl.route('/nfl/team/target_and_percentages', methods=['GET'])
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

@nfl.route('/nfl/team/stats', methods=['GET'])
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
        df_year = df_standings[df_standings['year'] == year]
        record = f"{df_year['wins'].values.tolist()[0]}-{df_year['losses'].values.tolist()[0]}-{df_year['ties'].values.tolist()[0]}"
        team_record_dict[year] = record
    json_output.update({f"team_record": team_record_dict})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output

@nfl.route('/nfl/team/results', methods=['GET'])
def nfl_team_results():
    team_id = int(request.args.get('team_id', None))
    connection = create_connection()
    cursor = connection.cursor()
    json_output = {}

    query = f'''SELECT week, year, home_id, home_score, away_id, away_score, winner, margin_of_victory, vegas_line,
    vegas_line_result, over_under, total_points, over_under_result
                FROM nfl_games
                WHERE nfl_games.home_id = {team_id} OR nfl_games.away_id = {team_id} AND nfl_games.year >= 2022'''
    cursor.execute(query)
    cols = ['week', 'year', 'home_id', 'home_score', 'away_id', 'away_score', 'winner', 'margin_of_victory', 'vegas_line',
            'vegas_line_result', 'over_under', 'total_points', 'over_under_result']
    results = list(cursor.fetchall())
    df_results = pd.DataFrame(results, columns=cols).reset_index(drop=True)

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output

@nfl.route('/nfl/team/opponent_info', methods=['GET'])
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




@nfl.route('/nfl/team/defense_rankings', methods=['GET'])
def nfl_get_rankings():
    column_name = request.args.get('stat', None)
    player_id = request.args.get('id', None)
    json_output = {}

    # GET DATA FROM DB WITH SQL QUERY AND MAKE DF OUT OF IT
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, game_id, player_id, team_id, opp_id
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN 
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    WHERE nfl_games.year >= 2022 AND nfl_player_stats.player_id = {player_id}'''
    cursor.execute(player_query)
    results = list(cursor.fetchall())

    df_columns = ['name', 'year', 'week', 'position', 'game_id', 'player_id', 'team_id', 'opp_id']
    df_player_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)

    df_current = df_player_logs[df_player_logs['year'] == nfl_current_year]
    current_opponents = pd.Series(df_current['opp_id'].values, index=df_current['week']).to_dict()

    df_prior = df_player_logs[df_player_logs['year'] == nfl_prior_year]
    prior_opponents = pd.Series(df_prior['opp_id'].values, index=df_prior['week']).to_dict()

    df_third = df_player_logs[df_player_logs['year'] == nfl_third_year]
    third_opponents = pd.Series(df_third['opp_id'].values, index=df_third['week']).to_dict()

    df_fourth = df_player_logs[df_player_logs['year'] == nfl_fourth_year]
    fourth_opponents = pd.Series(df_fourth['opp_id'].values, index=df_fourth['week']).to_dict()

    # GET WEEKLY RANK STAT DATA
    if column_name in ['rec', 'rec_yards', 'rec_td']:
        columns = f"team_id, year, week, {limit_stat_dict[column_name]}, {column_name}, {column_name}_rank"
        rank_cols = ['team_id', 'year', 'week', f"{limit_stat_dict[column_name]}", f"{column_name}", f"{column_name}_rank"]
    else:
        columns = f"team_id, year, week, {limit_stat_dict[column_name]}, {limit_stat_dict[column_name]}_rank, {column_name}, {column_name}_rank"
        rank_cols = ['team_id', 'year', 'week', f"{limit_stat_dict[column_name]}", f"{limit_stat_dict[column_name]}_rank", f"{column_name}",
                   f"{column_name}_rank"]

    # GET DATA FROM DB WITH SQL QUERY AND MAKE DF OUT OF IT
    connection = create_connection()
    cursor = connection.cursor()
    weekly_rank_query = f'''SELECT {columns} FROM nfl_weekly_rank'''

    cursor.execute(weekly_rank_query)
    weekly_rank_results = list(cursor.fetchall())

    df_weekly_rank = pd.DataFrame(weekly_rank_results, columns=rank_cols)

    # Get opponent ranks for specific stats
    rank_col = f"{column_name}_rank"
    for opp_dict in [current_opponents, prior_opponents, third_opponents, fourth_opponents]:
        if opp_dict == current_opponents:
            df_year = df_weekly_rank[df_weekly_rank['year'] == nfl_current_year]
            year = nfl_current_year
        elif opp_dict == prior_opponents:
            df_year = df_weekly_rank[df_weekly_rank['year'] == nfl_prior_year]
            year = nfl_prior_year
        elif opp_dict == third_opponents:
            df_year = df_weekly_rank[df_weekly_rank['year'] == nfl_third_year]
            year = nfl_third_year
        else:
            df_year = df_weekly_rank[df_weekly_rank['year'] == nfl_fourth_year]
            year = nfl_fourth_year

        opponent_rank_dict = {}
        opponent_total_dict = {}
        for key, val in opp_dict.items():
            opponent_rank_dict[key] = int(df_year[
                                              (df_year['week'] == key) & (df_year['team_id'] == val)][rank_col].values)
            opponent_total_dict[key] = int(df_year[
                                               (df_year['week'] == key) & (df_year['team_id'] == val)][column_name].values)

        json_output.update( {f"opponents_weekly_rank_{year_name_dict[year]}": opponent_rank_dict})
        json_output.update({f"opponents_season_total_{year_name_dict[year]}": opponent_total_dict})

    # Enable Access-Control-Allow-Origin
    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output


# GET ROUTES - Team related bet data


@nfl.route('/nfl/team/starting_qb', methods=['GET'])
def nfl_team_starting_qb():
    team_id = request.args.get('team_id', None)
    json_output = {}

    # GET DATA FROM DB WITH SQL QUERY AND MAKE DF OUT OF IT
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT team.name, team_id, player_id, position
                    FROM
                    nfl_starting_lineups
                    JOIN
                    team ON team.id = nfl_starting_lineups.team_id
                    WHERE nfl_starting_lineups.team_id = {team_id} and nfl_starting_lineups.position = "QB"'''
    cursor.execute(player_query)
    results = list(cursor.fetchall())

    df_columns = ['name', 'team_id', 'player_id', 'position']
    df_qb = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)
    starting_qb = int(df_qb['player_id'].values[0])
    json_output.update({f"starting_qb": starting_qb})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output

@nfl.route('/nfl/player/qb_breakdown', methods=['GET'])
def nfl_qb_breakdown():
    qb_id = request.args.get('qb_id', None)
    column_name = request.args.get('stat', None)
    team_id = int(request.args.get('team_id', None))

    json_output = {}

    limit_stat = limit_stat_dict[column_name]
    df_columns = ['name', 'year', 'week', 'position', 'player_id', 'team_id', 'game_id', column_name, limit_stat]

    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()
    player_query = f'''SELECT CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                            player.position, player_id, team_id, game_id, {column_name}, {limit_stat}
                        FROM
                        nfl_player_stats
                        JOIN
                        player ON player.id = nfl_player_stats.player_id
                        JOIN 
                        nfl_games on nfl_games.id = nfl_player_stats.game_id
                        WHERE nfl_games.year >=2022 AND nfl_player_stats.game_id IN 
                        (select nfl_player_stats.game_id from nfl_player_stats where nfl_player_stats.player_id = {qb_id})'''
    cursor.execute(player_query)
    results = list(cursor.fetchall())

    df_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)

    # GET PLAYERS PREVIOUS TEAMS
    try:
        prior_team = int(np.unique(df_logs[(df_logs['year'] == nfl_prior_year) & (
                                                    df_logs['player_id'] == int(qb_id))]['team_id'].values))
    except ValueError:
        prior_team = 0
    try:
        third_team = int(np.unique(df_logs[(df_logs['year'] == nfl_third_year) & (
                                                    df_logs['player_id'] == int(qb_id))]['team_id'].values))
    except ValueError:
        third_team = 0
    try:
        fourth_team = int(np.unique(df_logs[(df_logs['year'] == nfl_fourth_year) & (
                                                    df_logs['player_id'] == int(qb_id))]['team_id'].values))
    except ValueError:
        fourth_team = 0

    player_teams = {
        nfl_current_year: team_id,
        nfl_prior_year: prior_team,
        nfl_third_year: third_team,
        nfl_fourth_year: fourth_team
    }
    year_dict = {
        0: {'json': 'current', 'year': nfl_current_year},
        1: {'json': 'prior', 'year': nfl_prior_year},
        2: {'json': 'third', 'year': nfl_third_year},
        3: {'json': 'fourth', 'year': nfl_fourth_year}
    }

    # CREATE LIST OF DATAFRAMES TO LOOP THROUGH
    current_games = df_logs[(df_logs['year'] == nfl_current_year) & (df_logs['team_id'] == player_teams[nfl_current_year])]
    prior_games = df_logs[(df_logs['year'] == nfl_prior_year) & (df_logs['team_id'] == player_teams[nfl_prior_year])]
    third_games = df_logs[(df_logs['year'] == nfl_third_year) & (df_logs['team_id'] == player_teams[nfl_third_year])]
    fourth_games = df_logs[(df_logs['year'] == nfl_fourth_year) & (df_logs['team_id'] == player_teams[nfl_fourth_year])]

    # CREATE A DF OF TOTAL GAMES
    total_games = pd.concat([current_games, prior_games])
    total_games = pd.concat([total_games, third_games])
    total_games = pd.concat([total_games, fourth_games])

    # GROUP GAMES BY GAME_ID TO THEN APPLY PERCENTAGE MATH AND CREATE NEW COLUMNS
    grouped_games = total_games.groupby(['game_id', 'week', 'year', 'position'])[[limit_stat, column_name]].sum()
    grouped_games = grouped_games.reset_index()

    game_group = grouped_games.groupby(['game_id'])[[limit_stat, column_name]].sum()
    grouped_games['att_share_percentage'] = round((grouped_games[limit_stat] / game_group.loc[grouped_games['game_id'].values[0]][limit_stat]) * 100, 1)
    grouped_games['percent_of_stat_total'] = round((grouped_games[column_name] / game_group.loc[grouped_games['game_id'].values[0]][column_name]) * 100, 1)

    current_test = grouped_games[grouped_games['year'] == nfl_current_year]
    prior_test = grouped_games[grouped_games['year'] == nfl_prior_year]
    third_test = grouped_games[grouped_games['year'] == nfl_third_year]
    fourth_test = grouped_games[grouped_games['year'] == nfl_fourth_year]

    list_df = [current_test, prior_test, third_test, fourth_test]
    for i in range(len(list_df)):
        df = list_df[i]
        print(df)
        year = year_dict[i]['json']
        yearly_total_targets = df[limit_stat].sum()
        yearly_total_stats = df[column_name].sum()


        df_rb = df[df['position'] == 'RB']
        # GET YEARLY TOTAL DOWN
        pos_yearly_targets = df_rb[limit_stat].sum()
        pos_yearly_totals = df_rb[column_name].sum()
        json_output.update({f"rb_limit_stat_percentage_{year}": round((pos_yearly_targets / yearly_total_targets) * 100, 1)})
        json_output.update({f"rb_limit_stat_total_{year}": round((pos_yearly_totals / yearly_total_stats) * 100, 1)})

        # GET WEEKLY BREAKDOWN
        rb_limit_stat_dict = dict(zip(df_rb['week'].values.tolist(), df_rb[limit_stat].values.tolist()))
        rb_target_percentage_dict = dict(zip(df_rb['week'].values.tolist(), df_rb['att_share_percentage'].values.tolist()))
        rb_stat_total_dict = dict(zip(df_rb['week'].values.tolist(), df_rb[column_name].values.tolist()))
        rb_stat_percentage_dict = dict(zip(df_rb['week'].values.tolist(), df_rb['percent_of_stat_total'].values.tolist()))

        json_output.update({f"rb_limit_stat_dict_{year}": rb_limit_stat_dict})
        json_output.update({f"rb_att_share_percentage_dict_{year}": rb_target_percentage_dict})
        json_output.update({f"rb_stat_total_dict_{year}": rb_stat_total_dict})
        json_output.update({f"rb_stat_percentage_dict_{year}": rb_stat_percentage_dict})

        df_wr = df[df['position'] == 'WR']
        # GET YEARLY TOTAL DOWN
        pos_yearly_targets = df_wr[limit_stat].sum()
        pos_yearly_totals = df_wr[column_name].sum()
        json_output.update({f"wr_limit_stat_percentage_{year}": round((pos_yearly_targets / yearly_total_targets) * 100, 1)})
        json_output.update({f"wr_limit_stat_total_{year}": round((pos_yearly_totals / yearly_total_stats) * 100, 1)})

        # GET WEEKLY BREAKDOWN
        wr_limit_stat_dict = dict(zip(df_wr['week'].values.tolist(), df_wr['targets'].values.tolist()))
        wr_target_percentage_dict = dict(zip(df_wr['week'].values.tolist(), df_wr['att_share_percentage'].values.tolist()))
        wr_stat_total_dict = dict(zip(df_wr['week'].values.tolist(), df_wr[column_name].values.tolist()))
        wr_stat_percentage_dict = dict(zip(df_wr['week'].values.tolist(), df_wr['percent_of_stat_total'].values.tolist()))

        json_output.update({f"wr_limit_stat_dict_{year}": wr_limit_stat_dict})
        json_output.update({f"wr_att_share_percentage_dict_{year}": wr_target_percentage_dict})
        json_output.update({f"wr_stat_total_dict_{year}": wr_stat_total_dict})
        json_output.update({f"wr_stat_percentage_dict_{year}": wr_stat_percentage_dict})

        df_te = df[df['position'] == 'TE']
        # GET YEARLY TOTAL DOWN
        pos_yearly_targets = df_te[limit_stat].sum()
        pos_yearly_totals = df_te[column_name].sum()
        json_output.update({f"te_limit_stat_percentage_{year}": round((pos_yearly_targets / yearly_total_targets) * 100, 1)})
        json_output.update({f"te_limit_stat_total_{year}": round((pos_yearly_totals / yearly_total_stats) * 100, 1)})

        # GET WEEKLY BREAKDOWN
        te_limit_stat_dict = dict(zip(df_te['week'].values.tolist(), df_te['targets'].values.tolist()))
        te_target_percentage_dict = dict(zip(df_te['week'].values.tolist(), df_te['att_share_percentage'].values.tolist()))
        te_stat_total_dict = dict(zip(df_te['week'].values.tolist(), df_te[column_name].values.tolist()))
        te_stat_percentage_dict = dict(zip(df_te['week'].values.tolist(), df_te['percent_of_stat_total'].values.tolist()))

        json_output.update({f"te_limit_stat_dict_{year}": te_limit_stat_dict})
        json_output.update({f"te_att_share_percentage_dict_{year}": te_target_percentage_dict})
        json_output.update({f"te_stat_total_dict_{year}": te_stat_total_dict})
        json_output.update({f"te_stat_percentage_dict_{year}": te_stat_percentage_dict})

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
            json_dict = {'home_score': int(row['home_score']),
                     'away_score': int(row['away_score']), 'winner': int(row['winner']), 'margin_of_victory': int(row['margin_of_victory']),
                     'weather_id': int(row['weather_id']), 'vegas_line': row['vegas_line'], 'vegas_line_result': row['vegas_line_result'],
                     'over_under': float(row['over_under']), 'total_points': int(row['total_points']),
                     'over_under_result': row['over_under_result'], 'week': int(row['week']),
                     'year': int(row['year']),  'home_id': int(row['home_id']), 'away_id': int(row['away_id'])}
            values = list(json_dict.values())

            cursor.execute('''UPDATE nfl_games
                    SET home_score = %s, away_score = %s, winner = %s, margin_of_victory = %s, weather_id = %s, vegas_line = %s,
                    vegas_line_result = %s, over_under = %s, total_points = %s, over_under_result = %s
                    WHERE week = %s AND year = %s AND nfl_games.home_id = %s AND nfl_games.away_id = %s''', (values))

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
        print(row)
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
                    total_points = %s, drives = %s, plays = %s, scoring_percentage = %s, to_percentage = %s, plays_per_drive = %s, 
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
                     'fumbles': int(row['fumbles']),
                     'home_id': int(row['home_id'])}
        values = list(json_dict.values())

        cursor.execute("""INSERT INTO nfl_player_stats (game_id, player_id, team_id, opp_id, pass_att, pass_comp, pass_yards, pass_td, pass_longest, 
                        ints, sacks, rush_att, rush_yards, rush_td, rush_longest, targets, rec, rec_yards, rec_td, rec_longest, fumbles, home_id) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
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
                     'pass_att_rank': int(row['pass_att_rank']),
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
         rec_td_rank, pass_att_rank, pass_comp_rank, rush_att_rank, rec_rank, pass_yards_per_att_rank, rush_yards_per_att_rank, rec_yards_per_rec_rank) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, %s, %s)""",
           (values))

        connection.commit()
        print(f"game_stats have been added to nfl_player_stats table.")


    return f"nfl_weekly_rank has been updated ."




# STARTING LINEUP ROUTES
@nfl.route('/nfl/team/starting_lineup_qb', methods=['PUT'])
def nfl_update_starting_lineup_qb():
    file = request.files['nfl_starting_lineup_qb']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        json_dict = {'player_id': int(row['player_id']),
                     'team_id': int(row['team_id']),
                     'position': f"'{row['position']}'"}

        cursor.execute(f"""UPDATE nfl_starting_lineups 
                SET player_id = {json_dict['player_id']}
                WHERE nfl_starting_lineups.team_id = {json_dict['team_id']} AND 
                nfl_starting_lineups.position = {json_dict['position']}""")

        connection.commit()
        print(f"game_stats have been added to nfl_player_stats table.")


    return f"nfl_weekly_rank has been updated ."

@nfl.route('/nfl/team/starting_lineup_wr', methods=['PUT'])
def nfl_update_starting_lineup_wr():
    file = request.files['nfl_starting_lineup_wr']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        json_dict = {'player_id': int(row['player_id']),
                     'team_id': int(row['team_id']),
                     'position': f"'{row['position']}'"}

        cursor.execute(f"""UPDATE nfl_starting_lineups 
                SET player_id = {json_dict['player_id']}
                WHERE nfl_starting_lineups.team_id = {json_dict['team_id']} AND 
                nfl_starting_lineups.position = {json_dict['position']}""")

        connection.commit()
        print(f"game_stats have been added to nfl_player_stats table.")


    return f"nfl_weekly_rank has been updated ."

@nfl.route('/nfl/team/starting_lineup_rb', methods=['PUT'])
def nfl_update_starting_lineup_rb():
    file = request.files['nfl_starting_lineup_rb']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        json_dict = {'player_id': int(row['player_id']),
                     'team_id': int(row['team_id']),
                     'position': f"'{row['position']}'"}

        cursor.execute(f"""UPDATE nfl_starting_lineups 
                SET player_id = {json_dict['player_id']}
                WHERE nfl_starting_lineups.team_id = {json_dict['team_id']} AND 
                nfl_starting_lineups.position = {json_dict['position']}""")

        connection.commit()
        print(f"game_stats have been added to nfl_player_stats table.")


    return f"nfl_weekly_rank has been updated ."

@nfl.route('/nfl/team/starting_lineup_te', methods=['PUT'])
def nfl_update_starting_lineup_te():
    file = request.files['nfl_starting_lineup_te']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        json_dict = {'player_id': int(row['player_id']),
                     'team_id': int(row['team_id']),
                     'position': f"'{row['position']}'"}

        cursor.execute(f"""UPDATE nfl_starting_lineups 
                SET player_id = {json_dict['player_id']}
                WHERE nfl_starting_lineups.team_id = {json_dict['team_id']} AND 
                nfl_starting_lineups.position = {json_dict['position']}""")

        connection.commit()
        print(f"game_stats have been added to nfl_player_stats table.")


    return f"nfl_weekly_rank has been updated ."


@nfl.route('/nfl/player/next_game', methods=['GET'])
def nfl_player_next_game():
    team_id = int(request.args.get('team_id', None))
    json_output = {}

    # SQL Query that returns the player information
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT id, week, year, home_id, away_id FROM nfl_games 
                        WHERE (home_id ={team_id} OR away_id = {team_id}) AND week = {nfl_next_week}
                        AND year = {nfl_current_year}'''
    cursor.execute(player_query)
    results = cursor.fetchone()

    home_id = results[3]
    if home_id == team_id:
        json_output.update({'next_game_loc': 'home'})
        json_output.update({'next_opp': results[-1]})
    else:
        json_output.update({'next_game_loc': 'away'})
        json_output.update({'next_opp': home_id})


    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output



# SUMMARY SECTION ROUTES
@nfl.route('/nfl/summary/player_info', methods=['GET'])
def nfl_player_info():
    player_id = int(request.args.get('id', None))
    json_output = {}

    # SQL Query that returns the player information
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT player.id, CONCAT(player.first_name, ' ', player.last_name) AS player_name, player.position,
                    player.image, player.current_team, team.id FROM player
                    JOIN 
                    team ON team.name = player.current_team
                    WHERE player.id = {player_id} and team.sport_id = 1'''
    cursor.execute(player_query)
    results = cursor.fetchone()

    # Add player data to JSON output
    json_output.update({'player_position': str(results[2])})
    json_output.update({'player_name': str(results[1])})
    json_output.update({'player_team_name': str(results[4])})
    json_output.update({'player_team_id': int(results[5])})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", '*')
    return json_output
@nfl.route('/nfl/summary/team_summary', methods=['GET'])
def nfl_team_summary():
    team_id = int(request.args.get('team_id', None))
    column_name = request.args.get('stat', None)
    json_output = {}

    if column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        columns = '''nfl_team_offense.rush_att, nfl_team_offense.rush_yards, nfl_team_offense.rush_td, 
                    nfl_team_offense.rush_yards_per_att, nfl_team_offense.rush_yards_per_game'''
    else:
        columns = '''nfl_team_offense.pass_att, nfl_team_offense.pass_comp, nfl_team_offense.pass_yards, nfl_team_offense.pass_td, 
                    nfl_team_offense.yards_per_att, nfl_team_offense.pass_yards_per_game'''


    # SQL Query that returns the player information
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT nfl_team_offense.year, nfl_team_offense.team_id, {columns}, team.id, team.name
                    FROM nfl_team_offense
                    JOIN 
                    team ON team.id = nfl_team_offense.team_id
                    WHERE nfl_team_offense.team_id = {team_id} and nfl_team_offense.year = {nfl_current_year} and team.sport_id = 1'''
    cursor.execute(player_query)
    results = cursor.fetchone()
    print(results)

    if column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        # Add player data to JSON output
        json_output.update({'team_name': str(results[-1])})
        json_output.update({'team_rush_yards': int(results[3])})
        json_output.update({'team_rush_att': int(results[2])})
        json_output.update({'team_touchdowns': int(results[4])})
        json_output.update({'team_rush_yards_per_att': float(results[5])})
        json_output.update({'team_rush_yards_per_game': float(results[6])})
    else:
        # Add player data to JSON output
        json_output.update({'team_name': str(results[-1])})
        json_output.update({'team_pass_att': int(results[2])})
        json_output.update({'team_pass_comp': int(results[3])})
        json_output.update({'team_pass_yards': int(results[4])})
        json_output.update({'team_pass_td': int(results[5])})
        json_output.update({'team_pass_yards_per_att': float(results[6])})
        json_output.update({'team_pass_yards_per_game': float(results[7])})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output
@nfl.route('/nfl/summary/team_rank_summary', methods=['GET'])
def nfl_team_rank_summary():
    team_id = int(request.args.get('team_id', None))
    column_name = request.args.get('stat', None)
    json_output = {}

    if column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        columns = '''nfl_team_offense.rush_att, nfl_team_offense.rush_yards, nfl_team_offense.rush_td,
                    nfl_team_offense.rush_yards_per_att, nfl_team_offense.rush_yards_per_game'''
        cols = ['year', 'team_id', 'rush_att', 'rush_yards', 'rush_td', 'rush_yards_per_att', 'rush_yards_per_game']
        rank_cols = ['rush_att', 'rush_yards', 'rush_td', 'rush_yards_per_att', 'rush_yards_per_game']
    else:
        columns = '''nfl_team_offense.pass_att, nfl_team_offense.pass_comp, nfl_team_offense.pass_yards, nfl_team_offense.pass_td, 
                    nfl_team_offense.yards_per_att, nfl_team_offense.pass_yards_per_game'''
        cols = ['year', 'team_id', 'pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_yards_per_att',
                'pass_yards_per_game']
        rank_cols = ['pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_yards_per_att', 'pass_yards_per_game']

    # SQL Query that returns the player information
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT nfl_team_offense.year, nfl_team_offense.team_id, {columns}
                    FROM nfl_team_offense
                    WHERE nfl_team_offense.year = {nfl_current_year}'''
    cursor.execute(player_query)
    results = list(cursor.fetchall())

    df_teams = pd.DataFrame(results, columns=cols).reset_index(drop=True)
    for rank_col in rank_cols:
        df_teams[f'{rank_col}_rank'] = df_teams[rank_col].rank(ascending=True)

    # # Filter to get team ranks
    df_team = df_teams[df_teams['team_id'] == team_id]
    for rank_col in rank_cols:
        json_output.update({f"{rank_col}_rank": df_team[f"{rank_col}_rank"].values[0]})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output
@nfl.route('/nfl/summary/opponent_summary', methods=['GET'])
def nfl_opponent_summary():
    opp_id = int(request.args.get('opp_id', None))
    column_name = request.args.get('stat', None)
    json_output = {}

    if column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        columns = '''nfl_team_defense.rush_att, nfl_team_defense.rush_yards, nfl_team_defense.rush_td,
                    nfl_team_defense.rush_yards_per_att, nfl_team_defense.rush_yards_per_game'''
    else:
        columns = '''nfl_team_defense.pass_att, nfl_team_defense.pass_comp, nfl_team_defense.pass_yards, nfl_team_defense.pass_td, 
                    nfl_team_defense.yards_per_att, nfl_team_defense.pass_yards_per_game'''

    # SQL Query that returns the player information
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT nfl_team_defense.year, nfl_team_defense.team_id, {columns}, team.id, team.name
                    FROM nfl_team_defense
                    JOIN 
                    team ON team.id = nfl_team_defense.team_id
                    WHERE nfl_team_defense.team_id = {opp_id} and nfl_team_defense.year = {nfl_current_year} and team.sport_id = 1'''
    cursor.execute(player_query)
    results = cursor.fetchone()
    print(results)

    if column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        # Add player data to JSON output
        json_output.update({'team_name': str(results[-1])})
        json_output.update({'team_rush_yards': int(results[3])})
        json_output.update({'team_rush_att': int(results[2])})
        json_output.update({'team_touchdowns': int(results[4])})
        json_output.update({'team_rush_yards_per_att': float(results[5])})
        json_output.update({'team_rush_yards_per_game': float(results[6])})
    else:
        # Add player data to JSON output
        json_output.update({'team_name': str(results[-1])})
        json_output.update({'team_pass_att': int(results[2])})
        json_output.update({'team_pass_comp': int(results[3])})
        json_output.update({'team_pass_yards': int(results[4])})
        json_output.update({'team_pass_td': int(results[5])})
        json_output.update({'team_pass_yards_per_att': float(results[6])})
        json_output.update({'team_pass_yards_per_game': float(results[7])})


    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output
@nfl.route('/nfl/summary/opponent_rank_summary', methods=['GET'])
def nfl_opponent_rank_summary():
    opp_id = int(request.args.get('opp_id', None))
    column_name = request.args.get('stat', None)
    json_output = {}

    if column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        columns = '''nfl_team_defense.rush_att, nfl_team_defense.rush_yards, nfl_team_defense.rush_td,
                    nfl_team_defense.rush_yards_per_att, nfl_team_defense.rush_yards_per_game'''
        cols = ['year', 'team_id', 'rush_att', 'rush_yards', 'rush_td', 'rush_yards_per_att', 'rush_yards_per_game']
        rank_cols = ['rush_att', 'rush_yards', 'rush_td', 'rush_yards_per_att', 'rush_yards_per_game']
    else:
        columns = '''nfl_team_defense.pass_att, nfl_team_defense.pass_comp, nfl_team_defense.pass_yards, nfl_team_defense.pass_td, 
                    nfl_team_defense.yards_per_att, nfl_team_defense.pass_yards_per_game'''
        cols = ['year', 'team_id', 'pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_yards_per_att',
                'pass_yards_per_game']
        rank_cols = ['pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_yards_per_att', 'pass_yards_per_game']

    # SQL Query that returns the player information
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT nfl_team_defense.year, nfl_team_defense.team_id, {columns}
                    FROM nfl_team_defense
                    WHERE nfl_team_defense.year = {nfl_current_year}'''
    cursor.execute(player_query)
    results = list(cursor.fetchall())

    df_teams = pd.DataFrame(results, columns=cols).reset_index(drop=True)
    for rank_col in rank_cols:
        df_teams[f'{rank_col}_rank'] = df_teams[rank_col].rank(ascending=True)

    # # Filter to get team ranks
    df_team = df_teams[df_teams['team_id'] == opp_id]
    for rank_col in rank_cols:
        json_output.update({f"{rank_col}_rank": df_team[f"{rank_col}_rank"].values[0]})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output
@nfl.route('/nfl/summary/game_logs_summary', methods=['GET'])
def nfl_game_log_summary():
    player_id = int(request.args.get('id', None))
    column_name = request.args.get('stat', None)
    json_output = {}

    if column_name in ['pass_att', 'pass_yards', 'pass_td', 'pass_comp', 'pass_longest']:
        columns = 'pass_att, pass_yards, pass_td, pass_comp, pass_longest'
    elif column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        columns = 'rush_att, rush_yards, rush_td, rush_longest, fumbles'
    else:
        columns = 'rec, targets, rec_yards, rec_td, rec_longest'


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
                    WHERE nfl_games.year >= {nfl_current_year} AND nfl_player_stats.player_id = {player_id}'''
    cursor.execute(player_query)

    raw_results = list(cursor.fetchall())
    results = raw_results[(len(raw_results) - 5):]

    # Build table data in JSON format
    row_indicator = 1
    for tup in results:
        if column_name in ['pass_att', 'pass_yards', 'pass_td', 'pass_comp', 'pass_longest']:
            row_dict_temp = {'name': '', 'year': '', 'week': '', 'pos': '', 'game_id': '', 'player_id': '',
                             'team_id': '', 'opp_id': '', 'pass_att': '', 'pass_yards': '', 'pass_td': '', 'pass_comp': '',
                             'pass_longest': ''}
        elif column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
            row_dict_temp = {'name': '', 'year': '', 'week': '', 'pos': '', 'game_id': '', 'player_id': '',
                             'team_id': '', 'opp_id': '', 'rush_att': '', 'rush_yards': '', 'rush_td': '',
                             'rush_longest': '', 'fumbles': ''}
        else:
            row_dict_temp = {'name': '', 'year': '', 'week': '', 'pos': '', 'game_id': '', 'player_id': '', 'team_id': '',
                             'opp_id': '', 'rec': '', 'targets': '', 'rec_yards': '', 'rec_td': '', 'rec_longest': ''}
        index = 0
        row_dict = row_dict_temp

        for key in row_dict.keys():
            row_dict[key] = tup[index]
            index +=1
        json_output[row_indicator] = row_dict
        row_indicator += 1

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output
@nfl.route('/nfl/summary/bet_occurrence_summary', methods=['GET'])
def nfl_bet_occurrence_summary():
    # Initialize variables
    player_id = int(request.args.get('id', None))
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = int(request.args.get('value', None))
    opp_id = int(request.args.get('opp_id', None))
    location = request.args.get('loc', None)
    start_qb = int(request.args.get('qb', None))
    json_output = {}

    # Set home/away variable
    if location == 'home':
        loc_id = 'home_id'
    else:
        loc_id = 'away_id'

    limit_stat = limit_stat_dict[column_name]
    columns = f'''{limit_stat}, {column_name}'''
    df_columns = ['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'home_id', 'away_id',
                  limit_stat, column_name]

    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, game_id, player_id, team_id, opp_id, nfl_games.home_id, nfl_games.away_id, {columns}
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    WHERE nfl_games.year >= 2020 AND nfl_player_stats.player_id = {player_id}'''

    cursor.execute(player_query)
    results = list(cursor.fetchall())

    # Create game log from returned sql query
    df_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)

    # Create a dictionary of games played each year
    df_log_years = df_logs.groupby(by=['year']).count()['week'].reset_index()
    games_dict = dict(zip(df_log_years['year'].values.tolist(), df_log_years['week'].values.tolist()))

    # Game logs versus opponents
    df_opponent = df_logs[df_logs['opp_id'] == opp_id].reset_index(drop=True)

    # Bet occurrences at home/away depending on if player is away or home
    df_loc = df_logs[df_logs[loc_id].isin(df_logs['team_id'].values.tolist())].reset_index(drop=True)
    df_loc_years = df_loc.groupby(by=['year']).count()['week'].reset_index()
    loc_games_dict = dict(zip(df_loc_years['year'].values.tolist(), df_loc_years['week'].values.tolist()))

    if column_name not in pass_stat_list:
        # GET ALL GAME LOGS W/ STARTING QB - Create a query, cursor and result list
        start_qb_connection = create_connection()
        start_qb_cursor = start_qb_connection.cursor()

        qb_query = f'''SELECT
                        CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                        player.position, game_id, player_id, team_id, opp_id, nfl_games.home_id, nfl_games.away_id, {columns}
                            FROM
                            nfl_player_stats
                            JOIN
                            player ON player.id = nfl_player_stats.player_id
                            JOIN 
                            nfl_games on nfl_games.id = nfl_player_stats.game_id
                            WHERE nfl_games.year >=2024 AND nfl_player_stats.game_id IN 
                            (select nfl_player_stats.game_id from nfl_player_stats where nfl_player_stats.player_id = {player_id}) 
                            AND (nfl_player_stats.player_id = {player_id} or nfl_player_stats.player_id = {start_qb})'''
        start_qb_cursor.execute(qb_query)
        qb_results = list(start_qb_cursor.fetchall())

        # Create player/qb game log from returned sql query
        df_qb_logs = pd.DataFrame(qb_results, columns=df_columns).reset_index(drop=True)
        df_qb_logs = df_qb_logs[df_qb_logs['player_id'] == player_id]
    else:
        df_qb_logs = pd.DataFrame()

    if operator == 'over':
        df_bet = df_logs[df_logs[column_name] > value]
        vs_opponent = df_opponent[df_opponent[column_name] > value]
        df_bet_loc = df_loc[df_loc[column_name] > value]
        if column_name not in pass_stat_list:
            df_qb = df_qb_logs[df_qb_logs[column_name] > value]
    else:
        df_bet = df_logs[df_logs[column_name] <= value]
        vs_opponent = df_opponent[df_opponent[column_name] <= value]
        df_bet_loc = df_loc[df_loc[column_name] <= value]
        if column_name not in pass_stat_list:
            df_qb = df_qb_logs[df_qb_logs[column_name] <= value]


    # Create a dictionary of number of times bet hit each year
    df_bet_years = df_bet.groupby(by=['year']).count()['week'].reset_index()
    bet_dict = dict(zip(df_bet_years['year'].values.tolist(), df_bet_years['week'].values.tolist()))

    for tag in [nfl_prior_year, nfl_current_year]:
        df_limit_years = df_bet.groupby(by=['year']).sum()[f"{limit_stat}"].reset_index()
        prior_limit = df_limit_years[df_limit_years['year'] == tag].values.tolist()[0][1]
        prior_avg = prior_limit / bet_dict[tag]
        json_output.update({f'{year_name_dict[tag]}_avg_limit': prior_avg})


    # Create a dictionary of games played each year for location (home/away)
    df_bet_loc_years = df_bet_loc.groupby(by=['year']).count()['week'].reset_index()
    bet_loc_dict = dict(zip(df_bet_loc_years['year'].values.tolist(), df_bet_loc_years['week'].values.tolist()))

    # Get the total number of games vs opponent
    vs_opp_games = len(df_opponent)
    vs_opp_hits = len(vs_opponent)

    if column_name not in pass_stat_list:
        # Get the total number of games with starting QB - (For non-QB players)
        start_qb_games = len(df_qb_logs)
        start_qb_hits = len(df_qb)

    # Update JSON with hits/total games
    json_output.update({'player_total_games': games_dict})
    json_output.update({'player_total_hits': bet_dict})
    json_output.update({'player_total_loc_games': loc_games_dict})
    json_output.update({'player_hits_location': bet_loc_dict})
    json_output.update({'vs_opponent_games': vs_opp_games})
    json_output.update({'vs_opponent_hits': vs_opp_hits})
    if column_name not in pass_stat_list:
        json_output.update({'start_qb_games': start_qb_games})
        json_output.update({'start_qb_hits': start_qb_hits})

    for year_element in [nfl_fifth_year, nfl_fourth_year, nfl_third_year, nfl_prior_year, nfl_current_year]:
        try:
            json_output.update({year_name_dict[year_element]:
                                    round((bet_dict[year_element] / games_dict[year_element]) * 100, 1)})
        except ZeroDivisionError:
            json_output.update({year_name_dict[year_element]: 0.0})

        try:
            json_output.update({f'loc_{year_name_dict[year_element]}': round(
                (bet_loc_dict[year_element] / loc_games_dict[year_element]) * 100, 1)})
        except ZeroDivisionError:
            json_output.update({'loc_current': 0.0})

    try:
        json_output.update({'vs_opponent': round((len(vs_opponent) / len(df_opponent)) * 100, 1)})
    except ZeroDivisionError:
        json_output.update({'vs_opponent': 0.0})

    if column_name not in pass_stat_list:
        try:
            json_output.update({'qb_player_data': round(
                (start_qb_hits / start_qb_games) * 100, 1)})
        except ZeroDivisionError:
            json_output.update({'qb_player_data': 0.0})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output

@nfl.route('/nfl/summary/player_summary', methods=['GET'])
def nfl_player_stat_summary():
    # Initialize variables
    player_id = int(request.args.get('id', None))
    column_name = request.args.get('stat', None)
    opp_id = int(request.args.get('opp_id', None))
    json_output = {}

    if column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        query_cols = 'rush_att, rush_yards, rush_td, rush_longest'
        cols =  ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']
    elif column_name in ['pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest']:
        query_cols = 'pass_att, pass_comp, pass_yards, pass_td, pass_longest'
        cols = ['pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest']
    else:
        query_cols = 'rec, targets, rec_yards, rec_td, rec_longest'
        cols = ['rec', 'targets', 'rec_yards', 'rec_td', 'rec_longest']

    limit_stat = limit_stat_dict[column_name]

    df_columns = ['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'home_id', 'away_id'] + cols

    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, game_id, player_id, team_id, opp_id, nfl_games.home_id, nfl_games.away_id, {query_cols}
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    WHERE nfl_games.year >= 2025 AND nfl_player_stats.player_id = {player_id}'''

    cursor.execute(player_query)
    results = list(cursor.fetchall())

    # Create game log from returned sql query
    df_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)

    df_home = df_logs[df_logs['home_id'].isin(df_logs['team_id'].values.tolist())]
    df_away = df_logs[df_logs['away_id'].isin(df_logs['team_id'].values.tolist())]

    if column_name in ['rec', 'targets', 'rec_yards', 'rec_td', 'rec_longest']:
        stat_avg_dict = {'avg_rec': round(df_logs['rec'].mean(),1),
                         'avg_targets': round(df_logs['targets'].mean(), 1),
                         'avg_rec_yards': round(df_logs['rec_yards'].mean(),1),
                         'avg_rec_td': round(df_logs['rec_td'].mean(), 1),
                         'avg_rec_longest': round(df_logs['rec_longest'].mean(), 1)}
        stat_home_dict = {'home_rec': round(df_home['rec'].mean(),1),
                         'home_targets': round(df_home['targets'].mean(), 1),
                         'home_rec_yards': round(df_home['rec_yards'].mean(),1),
                         'home_rec_td': round(df_home['rec_td'].mean(), 1),
                         'home_rec_longest': round(df_home['rec_longest'].mean(), 1)}
        stat_away_dict = {'away_rec': round(df_away['rec'].mean(),1),
                         'away_targets': round(df_away['targets'].mean(), 1),
                         'away_rec_yards': round(df_away['rec_yards'].mean(),1),
                         'away_rec_td': round(df_away['rec_td'].mean(), 1),
                         'away_rec_longest': round(df_away['rec_longest'].mean(), 1)}
    elif column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        stat_avg_dict = {'avg_rush_att': round(df_logs['rush_att'].mean(), 1),
                         'avg_rush_yards': round(df_logs['rush_yards'].mean(), 1),
                         'avg_rush_td': round(df_logs['rush_td'].mean(), 1),
                         'avg_rush_longest': round(df_logs['rush_longest'].mean(), 1)}
        stat_home_dict = {'home_rush_att': round(df_home['pass_att'].mean(),1),
                         'home_rush_yards': round(df_home['pass_yards'].mean(),1),
                         'home_rush_td': round(df_home['pass_td'].mean(), 1),
                         'home_rush_longest': round(df_home['pass_longest'].mean(), 1)}
        stat_away_dict = {'away_rush_att': round(df_away['pass_att'].mean(),1),
                         'away_rush_yards': round(df_away['pass_yards'].mean(),1),
                         'away_rush_td': round(df_away['pass_td'].mean(), 1),
                         'away_rush_longest': round(df_away['pass_longest'].mean(), 1)}
    else:
        stat_avg_dict = {'avg_pass_att': round(df_logs['pass_att'].mean(),1),
                         'avg_pass_comp': round(df_logs['pass_comp'].mean(), 1),
                         'avg_pass_yards': round(df_logs['pass_yards'].mean(),1),
                         'avg_pass_td': round(df_logs['pass_td'].mean(), 1),
                         'avg_pass_longest': round(df_logs['pass_longest'].mean(), 1)}
        stat_home_dict = {'home_pass_att': round(df_home['pass_att'].mean(),1),
                         'home_pass_comp': round(df_home['pass_comp'].mean(), 1),
                         'home_pass_yards': round(df_home['pass_yards'].mean(),1),
                         'home_pass_td': round(df_home['pass_td'].mean(), 1),
                         'home_pass_longest': round(df_home['pass_longest'].mean(), 1)}
        stat_away_dict = {'away_pass_att': round(df_away['pass_att'].mean(),1),
                         'away_pass_comp': round(df_away['pass_comp'].mean(), 1),
                         'away_pass_yards': round(df_away['pass_yards'].mean(),1),
                         'away_pass_td': round(df_away['pass_td'].mean(), 1),
                         'away_pass_longest': round(df_away['pass_longest'].mean(), 1)}

    json_output.update({'player_avg_stats': stat_avg_dict})
    json_output.update({'player_home_avg': stat_home_dict})
    json_output.update({'player_away_avgs': stat_away_dict})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output




# PLAYER SECTION ROUTES
@nfl.route('/nfl/player/home_road', methods=['GET'])
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
    current_home_games = len(df_home[df_home['year'] == nfl_current_year].index)
    prior_home_games = len(df_home[df_home['year'] == nfl_prior_year].index)
    third_home_games = len(df_home[df_home['year'] == nfl_third_year].index)
    fourth_home_games = len(df_home[df_home['year'] == nfl_fourth_year].index)
    current_away_games = len(df_away[df_away['year'] == nfl_current_year].index)
    prior_away_games = len(df_away[df_away['year'] == nfl_prior_year].index)
    third_away_games = len(df_away[df_away['year'] == nfl_third_year].index)
    fourth_away_games = len(df_away[df_away['year'] == nfl_fourth_year].index)

    if operator == 'over':
        home_bet_occurrences = df_home[df_home[column_name] > value]
        away_bet_occurrences = df_away[df_away[column_name] > value]
        home_bet_occurrences_current = df_home[(df_home['year'] == nfl_current_year) & (df_home[column_name] > value)]
        away_bet_occurrences_current = df_away[(df_away['year'] == nfl_current_year) & (df_away[column_name] > value)]
        home_bet_occurrences_prior = df_home[(df_home['year'] == nfl_prior_year) & (df_home[column_name] > value)]
        away_bet_occurrences_prior = df_away[(df_away['year'] == nfl_prior_year) & (df_away[column_name] > value)]
        home_bet_occurrences_third = df_home[(df_home['year'] == nfl_third_year) & (df_home[column_name] > value)]
        away_bet_occurrences_third = df_away[(df_away['year'] == nfl_third_year) & (df_away[column_name] > value)]
        home_bet_occurrences_fourth = df_home[(df_home['year'] == nfl_fourth_year) & (df_home[column_name] > value)]
        away_bet_occurrences_fourth = df_away[(df_away['year'] == nfl_fourth_year) & (df_away[column_name] > value)]
    else:
        home_bet_occurrences = df_home[df_home[column_name] <= value]
        away_bet_occurrences = df_away[df_away[column_name] <= value]
        home_bet_occurrences_current = df_home[(df_home['year'] == nfl_current_year) & (df_home[column_name] <= value)]
        away_bet_occurrences_current = df_away[(df_away['year'] == nfl_current_year) & (df_away[column_name] <= value)]
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
        {'home_bet_occurrences_current': round((len(home_bet_occurrences_current.index) / current_home_games) * 100, 1)})
    json_output.update(
        {'away_bet_occurrences_current': round((len(away_bet_occurrences_current.index) / current_away_games) * 100, 1)})
    json_output.update(
        {'away_bet_occurrences_prior': round((len(away_bet_occurrences_prior.index) / prior_away_games) * 100, 1)})
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




# def nfl_player_info():
#     player_id = int(request.args.get('id', None))
#     json_output = {}
#
#     # SQL Query that returns the player information
#     connection = create_connection()
#     cursor = connection.cursor()
#
#     player_query = f'''SELECT player.id, CONCAT(player.first_name, ' ', player.last_name) AS player_name, player.position,
#                     player.image, player.current_team, team.id FROM player
#                     JOIN
#                     team ON team.name = player.current_team
#                     WHERE player.id = {player_id} and team.sport_id = 1'''
#     cursor.execute(player_query)
#     results = cursor.fetchone()
#
#     # Add player data to JSON output
#     json_output.update({'player_position': str(results[2])})
#     json_output.update({'player_name': str(results[1])})
#     json_output.update({'player_team_name': str(results[4])})
#     json_output.update({'player_team_id': int(results[5])})
#
#     json_output = jsonify(json_output)
#     json_output.headers.add("Access-Control-Allow-Origin", "*")
#     return json_output