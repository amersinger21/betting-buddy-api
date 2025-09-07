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

year_name_dict = {2022: 'fourth', 2023: 'third', 2024: 'prior', 2025: 'current'}
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


@nfl.route('/nfl/player_bet_data', methods=['GET'])
def nfl_player_bet_data():
    player_id = int(request.args.get('id', None))
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = int(request.args.get('value', None))
    opp_id = int(request.args.get('opp_id', None))

    limit_stat = limit_stat_dict[column_name]
    columns = '''game_id, player_id, team_id, opp_id, pass_att, pass_yards, pass_td, pass_comp, pass_longest, rush_att,
         rush_yards, rush_td, rush_longest, rec, targets, rec_yards, rec_td, rec_longest, fumbles'''
    df_columns = ['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', 'pass_att', 'pass_yards', 'pass_td', 'pass_comp', 'pass_longest',
                  'rush_att', 'rush_yards', 'rush_td', 'rush_longest', 'rec', 'targets', 'rec_yards', 'rec_td',
                  'rec_longest', 'fumbles']

    json_output = {}

    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, {columns}
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    WHERE nfl_games.year >= 2022'''
    cursor.execute(player_query)

    results = list(cursor.fetchall())

    df_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)
    df_player_bet_logs = df_logs.loc[df_logs['player_id'] == player_id]
    df_player_bet_logs = df_player_bet_logs [['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id',
                                              'opp_id', limit_stat, column_name]]

    # This block gets players most recent information
    df_player_info = df_player_bet_logs.tail(1)
    player_pos = df_player_info['pos'].values.tolist()[0]
    json_output.update({'player_position': player_pos})
    json_output.update({'player_name': df_player_info['name'].values.tolist()[0]})
    json_output.update({'player_team': df_player_info['team_id'].values.tolist()[0]})

    if operator == 'over':
        df_total_occurrence = df_player_bet_logs.loc[df_player_bet_logs[column_name] > value]
    else:
        df_total_occurrence = df_player_bet_logs.loc[df_player_bet_logs[column_name] <= value]
    total_occurrence_percentage = round((len(df_total_occurrence) / len(df_player_bet_logs) * 100), 1)
    json_output.update({'career_bet_occurrence': total_occurrence_percentage})

    # CURRENT BET OCCURRENCE INFORMATION
    try:
        total_current_games = len(df_player_bet_logs.loc[df_player_bet_logs['year'] == nfl_current_year])
        if operator == 'over':
            df_current_occurrences = df_player_bet_logs.loc[
                (df_player_bet_logs[column_name] > value) & (df_player_bet_logs['year'] == nfl_current_year)]
        else:
            df_current_occurrences = df_player_bet_logs.loc[
                (df_player_bet_logs[column_name] <= value) & (df_player_bet_logs['year'] == nfl_current_year)]
        current_occurrence_percentage = round(((len(df_current_occurrences) / total_current_games) * 100), 1)
    except ZeroDivisionError:
        current_occurrence_percentage = 0.0
    json_output.update({'current_bet_occurrence': current_occurrence_percentage})

    # PRIOR BET OCCURRENCE INFORMATION
    total_prior_games = len(df_player_bet_logs.loc[df_player_bet_logs['year'] == nfl_prior_year])
    if operator == 'over':
        df_prior_occurrences = df_player_bet_logs.loc[
            (df_player_bet_logs[column_name] > value) & (df_player_bet_logs['year'] == nfl_prior_year)]
    else:
        df_prior_occurrences = df_player_bet_logs.loc[
            (df_player_bet_logs[column_name] <= value) & (df_player_bet_logs['year'] == nfl_prior_year)]
    prior_occurrence_percentage = round(((len(df_prior_occurrences) / total_prior_games) * 100), 1)
    json_output.update({'prior_bet_occurrence': prior_occurrence_percentage})

    # THIRD BET OCCURRENCE INFORMATION
    total_third_games = len(df_player_bet_logs.loc[df_player_bet_logs['year'] == nfl_third_year])
    if operator == 'over':
        df_third_occurrences = df_player_bet_logs.loc[
            (df_player_bet_logs[column_name] > value) & (df_player_bet_logs['year'] == nfl_third_year)]
    else:
        df_third_occurrences = df_player_bet_logs.loc[
            (df_player_bet_logs[column_name] <= value) & (df_player_bet_logs['year'] == nfl_third_year)]
    third_occurrence_percentage = round(((len(df_third_occurrences) / total_third_games) * 100), 1)
    json_output.update({'third_bet_occurrence': third_occurrence_percentage})

    # FOURTH BET OCCURRENCE INFORMATION
    total_fourth_games = len(df_player_bet_logs.loc[df_player_bet_logs['year'] == nfl_fourth_year])
    if operator == 'over':
        df_fourth_occurrences = df_player_bet_logs.loc[
            (df_player_bet_logs[column_name] > value) & (df_player_bet_logs['year'] == nfl_fourth_year)]
    else:
        df_fourth_occurrences = df_player_bet_logs.loc[
            (df_player_bet_logs[column_name] <= value) & (df_player_bet_logs['year'] == nfl_fourth_year)]
    fourth_occurrence_percentage = round(((len(df_fourth_occurrences) / total_fourth_games) * 100), 1)
    json_output.update({'third_bet_occurrence': fourth_occurrence_percentage})

    # LAST FOUR BET OCCURRENCE INFORMATION
    df_last_four = df_player_bet_logs.tail(4)
    if operator == 'over':
        df_last_four_occurrence = df_last_four.loc[df_last_four[column_name] > value]
    else:
        df_last_four_occurrence = df_last_four.loc[ df_player_bet_logs[column_name] <= value]
    last_four_occur_percentage = round(((len(df_last_four_occurrence) / 4) * 100), 1)
    json_output.update({'last_four_bet_occurrence': last_four_occur_percentage})

    # LAST EIGHT BET OCCURRENCE INFORMATION
    df_last_eight = df_player_bet_logs.tail(8)
    if operator == 'over':
        df_last_eight_occurrence = df_last_eight.loc[df_last_eight[column_name] > value]
    else:
        df_last_eight_occurrence = df_last_eight.loc[ df_last_eight[column_name] <= value]
    last_eight_occur_percentage = round(((len(df_last_eight_occurrence) / 8) * 100), 1)
    json_output.update({'last_eight_bet_occurrence': last_eight_occur_percentage})


    # PLAYER GAME LOG INFORMATION
    df_player_game_logs = df_player_bet_logs.copy()
    json_output.update({'current_game_logs': df_player_game_logs.loc[
                                                        df_player_game_logs['year'] == nfl_current_year].to_json()})
    json_output.update({'prior_game_logs': df_player_game_logs.loc[
                                                        df_player_game_logs['year'] == nfl_prior_year].to_json()})
    json_output.update({'third_game_logs': df_player_game_logs.loc[
                                                        df_player_game_logs['year'] == nfl_third_year].to_json()})
    json_output.update({'fourth_game_logs': df_player_game_logs.loc[
                                                        df_player_game_logs['year'] == nfl_fourth_year].to_json()})
    json_output.update({'last_four_game_logs': df_player_game_logs.tail(4).to_json()})
    json_output.update({'last_eight_game_logs': df_player_game_logs.tail(8).to_json()})

    if operator == 'over':
        json_output.update({'current_bet_logs': df_player_game_logs.loc[
            (df_player_game_logs['year'] == nfl_current_year) & (df_player_game_logs[column_name] > value)].to_json()})
        json_output.update({'prior_bet_logs': df_player_game_logs.loc[
            (df_player_game_logs['year'] == nfl_prior_year) & (df_player_game_logs[column_name] > value)].to_json()})
        json_output.update({'third_bet_logs': df_player_game_logs.loc[
            (df_player_game_logs['year'] == nfl_third_year) & (df_player_game_logs[column_name] > value)].to_json()})
        json_output.update({'fourth_bet_logs': df_player_game_logs.loc[
            (df_player_game_logs['year'] == nfl_fourth_year) & (df_player_game_logs[column_name] > value)].to_json()})
    else:
        json_output.update({'current_bet_logs': df_player_game_logs.loc[
            (df_player_game_logs['year'] == nfl_current_year) & (df_player_game_logs[column_name] <= value)].to_json()})
        json_output.update({'prior_bet_logs': df_player_game_logs.loc[
            (df_player_game_logs['year'] == nfl_prior_year) & (df_player_game_logs[column_name] <= value)].to_json()})
        json_output.update({'third_bet_logs': df_player_game_logs.loc[
            (df_player_game_logs['year'] == nfl_third_year) & (df_player_game_logs[column_name] <= value)].to_json()})
        json_output.update({'third_bet_logs': df_player_game_logs.loc[
            (df_player_game_logs['year'] == nfl_fourth_year) & (df_player_game_logs[column_name] <= value)].to_json()})

    # GET OPPONENT GAME LOGS AND BET OCCURRENCE VS SPECIFIED BET
    if column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        limit_stat = 'rush_att'
        limit_amount = 5
    elif column_name in ['pass_att', 'pass_yards', 'pass_td', 'pass_longest']:
        limit_stat = 'pass_att'
        limit_amount = 20
    else:
        limit_stat = 'targets'
        limit_amount = 3

    for year in sorted(list(set(df_player_bet_logs['year'].values.tolist()))):
        df_log_vs_opp = df_logs.loc[
            (df_logs['year'] == year) & (df_logs['opp_id'] == opp_id) & (df_logs['pos'] == player_pos)]
        json_output.update({f"game_logs_vs_opponent_{year_name_dict[year]}": df_log_vs_opp.to_json()})

        # GET OPPONENT DATA VS SPECIFIC BET
        total_pos_players_faced = len(df_log_vs_opp)
        opp_games_total = len((list(set(df_logs['week'].values.tolist())))) - 1

        if operator == 'under':
            df_bet = df_log_vs_opp.loc[
                (df_log_vs_opp[column_name] < value) & (df_log_vs_opp[limit_stat] >= limit_amount)]
        else:
            df_bet = df_log_vs_opp.loc[
                (df_log_vs_opp[column_name] > value) & (df_log_vs_opp[limit_stat] >= limit_amount)]

        weeks_bet_hit_count = len(list(set(df_bet['week'].values.tolist())))
        players_hit_bet = len(df_bet)

        opp_plyr_bet_allowed_percentage = round(((players_hit_bet / total_pos_players_faced) *100), 1)
        opp_week_bet_allowed_percentage = round(((weeks_bet_hit_count / opp_games_total) * 100), 1)

        json_output.update({f"opp_player_bet_percentage_{year_name_dict[year]}": opp_plyr_bet_allowed_percentage})
        json_output.update({f"opp_week_bet_percentage_{year_name_dict[year]}": opp_week_bet_allowed_percentage})

        # GET OPPONENT TD VS POSITIONS
        if column_name in ['rush_td', 'rec_td']:
            td_dict = {'rush_td': int(df_log_vs_opp['rush_td'].sum()),
                       'rec_td': int(df_log_vs_opp['rec_td'].sum()),
                       'total_td': int(df_log_vs_opp['rec_td'].sum()) + int(df_log_vs_opp['rec_td'].sum())}
            json_output.update({f"opp_vs_rb_data_{year_name_dict[year]}": td_dict})


    # GET GAME LOGS WHERE PLAYER PREVIOUSLY PLAYED OPPONENT
    df_player_vs_opp = df_player_bet_logs.loc[df_player_bet_logs['opp_id'] == opp_id]
    games_vs_opp = len(df_player_vs_opp)
    if operator == 'over':
        bet_occurrences_vs_opp = len(df_player_vs_opp.loc[df_player_vs_opp[column_name] > value])
    else:
        bet_occurrences_vs_opp = len(df_player_vs_opp.loc[df_player_vs_opp[column_name] <= value])
    hits_vs_opp = round(((bet_occurrences_vs_opp / games_vs_opp) * 100), 1)
    json_output.update({f"game_log_vs_opponent": df_player_vs_opp.to_json()})
    json_output.update({f"bet_occurrences_vs_opponent": bet_occurrences_vs_opp})
    json_output.update({f"bet_occurrences_vs_opponent_percentage": hits_vs_opp})


    # Get time between bets
    df_bet_occurrence = df_player_bet_logs.copy()
    df_bet_occurrence = df_bet_occurrence[['name', 'year', 'week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id',
                                           limit_stat, column_name]]

    loop_years = get_years_played(df_bet_occurrence)[-4:]
    for year in loop_years:
        weeks_played = get_weeks_played(df_bet_occurrence, year)

        if operator == 'over':
            df_bet_occurrences = df_bet_occurrence.loc[
                (df_bet_occurrence[column_name] > value) & (df_bet_occurrence['year'] == year)]
        else:
            df_bet_occurrences = df_bet_occurrence.loc[
                (df_bet_occurrence[column_name] <= value) & (df_bet_occurrence['year'] == year)]

        weeks_bet_hit = df_bet_occurrences['week'].values.tolist()

        first_occurrence = df_bet_occurrences.head(1)['week'].values.tolist()[0]
        first_week_played = weeks_played[0]

        last_occurrence = df_bet_occurrences.tail(1)['week'].values.tolist()[0]
        last_week_played = weeks_played[-1]

        if (first_occurrence != 1) and (first_week_played == 1):
            first_num_to_subtract = 1
        else:
            first_num_to_subtract = first_week_played

        if (last_occurrence != 18) and (last_week_played == 18):
            final_num_to_subtract = 18
        else:
            final_num_to_subtract =  last_week_played


        # GET THE NUMBER OF WEEKS BETWEEN BET OCCURRENCES AND ADD TO LIST
        weeks_btw_hits = []
        for i in range(len(weeks_bet_hit) + 1):
            if i == 0:
                time_btw = weeks_bet_hit[i] - first_num_to_subtract
            elif i == len(weeks_bet_hit):
                time_btw = final_num_to_subtract - weeks_bet_hit[i - 1]
            else:
                time_btw = weeks_bet_hit[i] - (weeks_bet_hit[i-1] + 1)

            weeks_btw_hits.append(time_btw)
        json_output.update({f"avg_weeks_between_occurrence_{year_name_dict[year]}": statistics.mean(weeks_btw_hits)})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output

@nfl.route('/nfl/player_data', methods=['GET'])
def nfl_player_data():
    player_id = request.args.get('id', None)
    column_name = request.args.get('stat', None)

    limit_stat = limit_stat_dict[column_name]

    cols_to_select = f'''game_id, player_id, team_id, opp_id, pass_att, pass_yards, pass_td, pass_comp, pass_longest, rush_att,
         rush_yards, rush_td, rush_longest, rec, targets, rec_yards, rec_td, rec_longest, fumbles'''
    json_output = {}

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
                        WHERE nfl_games.year >= 2022'''
    cursor.execute(player_query)
    results = list(cursor.fetchall())

    df_columns = ['name', 'year', 'week', 'position', 'game_id', 'player_id', 'team_id', 'opp_id', 'pass_att', 'pass_yards',
                  'pass_td', 'pass_comp', 'pass_longest', 'rush_att', 'rush_yards', 'rush_td', 'rush_longest', 'rec',
                  'targets', 'rec_yards', 'rec_td', 'rec_longest', 'fumbles']
    df_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)
    df_logs = df_logs[['name', 'year', 'week', 'position', 'game_id', 'player_id', 'team_id', 'opp_id', limit_stat, column_name]]

    df_player_logs = df_logs.loc[df_logs['player_id'] == int(player_id)]
    player_name = df_player_logs.loc[df_logs['player_id'] == int(player_id)].head(1)['name'].values.tolist()[0]

    loop_years = get_years_played(df_player_logs)[-4:]
    weeks_played_dict = {nfl_fourth_year: get_weeks_played(df_player_logs, nfl_fourth_year),
                         nfl_third_year: get_weeks_played(df_player_logs, nfl_third_year),
                         nfl_prior_year: get_weeks_played(df_player_logs, nfl_prior_year),
                         nfl_current_year: get_weeks_played(df_player_logs, nfl_current_year)}
    player_teams_dict = nfl_info(player_id=int(player_id), df=df_player_logs)['team']

    for year in loop_years:
        try:
            weeks = weeks_played_dict[year]
            player_team = player_teams_dict[year]
        except KeyError:
            print(f"{year} not in {loop_years}")
            continue
        percent_of_total_dict = {}
        player_stat_total_dict = {}
        for week in weeks:
            # Get team total
            df = df_logs.loc[(df_logs['team_id'] == player_team) & (df_logs['year'] == year) & (df_logs['week'] == week)]
            team_total = df[column_name].sum()

            # Get player total
            df_player_week = df_player_logs.loc[(df_player_logs['year'] == year) & (df_player_logs['week'] == week)]
            player_total = df_player_week[column_name].values.tolist()[0]

            percent_of_total_dict[week] = round((player_total/team_total) * 100, 1)
            player_stat_total_dict[week] = player_total

        json_output.update(
            {f"player_percent_of_total_{year_name_dict[year]}": percent_of_total_dict})
        json_output.update(
            {f"player_stat_total_{year_name_dict[year]}": player_stat_total_dict})

    # Get team target share for players team
    df_targets = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)
    df_targets = df_targets[['name', 'year', 'week', 'position', 'game_id', 'player_id', 'team_id',
                                 'opp_id', 'targets', 'rec_yards']]

    for year in loop_years:
        try:
            team_id = player_teams_dict[year]
        except KeyError:
            print(f"{year} not in {loop_years}")
            continue
        df_team_targets = df_targets.loc[(df_targets['team_id'] == team_id) & (df_targets['year'] == year)]
        total_team_targets = df_team_targets['targets'].sum()

        team_target_breakdown = df_team_targets.groupby(by=['name']).agg(targets=('targets', 'sum')).reset_index()
        team_target_breakdown['target_percent_of_total'] = round(((team_target_breakdown['targets'] / total_team_targets) * 100), 1)
        team_target_breakdown  = team_target_breakdown.sort_values(by=['targets'], ascending=False)
        team_target_breakdown = team_target_breakdown.loc[team_target_breakdown['targets'] > 0]

        player_target_share = team_target_breakdown.loc[
                                team_target_breakdown['name'] == player_name]['target_percent_of_total'].values.tolist()[0]
        player_targets = team_target_breakdown.loc[
                                team_target_breakdown['name'] == player_name]['targets'].values.tolist()[0]
        json_output.update(
            {f"player_target_share_{year_name_dict[year]}": player_target_share})
        json_output.update({f"player_targets_{year_name_dict[year]}": player_targets})
        json_output.update({f"team_target_breakdown_{year_name_dict[year]}": team_target_breakdown.to_json()})


    # Enable Access-Control-Allow-Origin
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




















# @nfl.route('nfl/bet_occurrence', methods=['GET'])
# def nfl_get_bet_occurrences():
#     player_id = request.args.get('id', None)
#     column_name = request.args.get('stat', None)
#     operator = request.args.get('operator', None)
#     value = int(request.args.get('value', None))
#
#     limit_stat = limit_stat_dict[column_name]
#     cols_to_select = f"game_id, player_id, team_id, opp_id, {limit_stat}, {column_name}"
#     json_output = {}
#
#     # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
#     connection = create_connection()
#     cursor = connection.cursor()
#
#     player_query = f'''SELECT
#                     CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
#                     player.position, {cols_to_select}
#                     FROM
#                     nfl_player_stats
#                     JOIN
#                     player ON player.id = nfl_player_stats.player_id
#                     JOIN
#                     nfl_games on nfl_games.id = nfl_player_stats.game_id
#                     WHERE nfl_games.year >= 2019 AND nfl_player_stats.player_id = %s'''
#     values = [player_id]
#     cursor.execute(player_query, values)
#
#     results = list(cursor.fetchall())
#
#     df_columns = ['name', 'Year', 'Week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', limit_stat, column_name]
#     df_player_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)
#
#     # Total Bet Occurrences
#     if operator == 'over':
#         df_total_occurrence = df_player_logs.loc[df_player_logs[column_name] > value]
#     else:
#         df_total_occurrence = df_player_logs.loc[df_player_logs[column_name] <= value]
#     total_occurrence_percentage = round((len(df_total_occurrence) / len(df_player_logs) * 100), 1)
#     json_output.update({'career_bet_occur_percentage': total_occurrence_percentage})
#     json_output.update({'career_bet_occurrences': len(df_total_occurrence)})
#
#
#     # Prior Year Occurrences
#     total_prior_games = len(df_player_logs.loc[df_player_logs['Year'] == 2024])
#     if operator == 'over':
#         df_prior_occurrences = df_player_logs.loc[
#             (df_player_logs[column_name] > value) & (df_player_logs['Year'] == 2024)]
#     else:
#         df_prior_occurrences = df_player_logs.loc[
#             (df_player_logs[column_name] <= value) & (df_player_logs['Year'] == 2024)]
#     prior_occurrence_percentage = round(((len(df_prior_occurrences) / total_prior_games) * 100), 1)
#     json_output.update({'prior_bet_occur_percentage': prior_occurrence_percentage})
#     json_output.update({'prior_bet_occurrences': len(df_prior_occurrences)})
#
#
#     total_third_games = len(df_player_logs.loc[df_player_logs['Year'] == 2023])
#     if operator == 'over':
#         df_third_occurrences = df_player_logs.loc[
#             (df_player_logs[column_name] > value) & (df_player_logs['Year'] == 2023)]
#     else:
#         df_third_occurrences = df_player_logs.loc[
#             (df_player_logs[column_name] <= value) & (df_player_logs['Year'] == 2023)]
#     third_occurrence_percentage = round(((len(df_third_occurrences) / total_third_games) * 100), 1)
#     json_output.update({'third_bet_occur_percentage': third_occurrence_percentage})
#     json_output.update({'third_bet_occurrences': len(df_third_occurrences)})
#
#
#     df_last_four = df_player_logs.tail(4)
#     if operator == 'over':
#         df_last_four_occurrence = df_last_four.loc[df_last_four[column_name] > value]
#     else:
#         df_last_four_occurrence = df_last_four.loc[ df_player_logs[column_name] <= value]
#     last_four_occur_percentage = round(((len(df_last_four_occurrence) / 4) * 100), 1)
#     json_output.update({'last_four_bet_occur_percentage': last_four_occur_percentage})
#     json_output.update({'last_four_bet_occurrences': len(df_last_four_occurrence)})
#
#
#     df_last_eight = df_player_logs.tail(8)
#     if operator == 'over':
#         df_last_eight_occurrence = df_last_eight.loc[df_last_eight[column_name] > value]
#     else:
#         df_last_eight_occurrence = df_last_eight.loc[ df_last_eight[column_name] <= value]
#     last_eight_occur_percentage = round(((len(df_last_eight_occurrence) / 8) * 100), 1)
#     json_output.update({'last_eight_bet_occur_percentage': last_eight_occur_percentage})
#     json_output.update({'last_eight_bet_occurrences': len(df_last_eight_occurrence)})
#
#
#     json_output = jsonify(json_output)
#     json_output.headers.add("Access-Control-Allow-Origin", "*")
#     return json_output