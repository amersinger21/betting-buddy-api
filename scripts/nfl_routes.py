import pandas as pd

from .db import create_connection
from flask import Blueprint, request, jsonify

nfl = Blueprint("nfl", __name__)

@nfl.route('nfl/player_logs', methods=['GET'])
def nfl_player_logs():
    player_id = request.args.get('id', None)
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = float(request.args.get('value', None))
    connection = create_connection()
    cursor = connection.cursor()
    print(f"player_id = {player_id}")
    print(f"value = {value}")
    print(f"operator = {operator}")

    # initialize the query and vals variables
    query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, nfl_player_stats.*
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN 
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    WHERE player.id = %s'''
    vals = [player_id]

    # use the query to get player game logs
    cursor.execute(query, vals)

    # data returned from query as a list
    results = list(cursor.fetchall())

    df_final = pd.DataFrame()
    for result in results:
        item = {'name': result[0], 'Year': result[1], 'Week': result[2], 'pos': result[3], 'id': result[4],
                'game_id': result[5], 'player_id': result[6], 'team_id': result[7], 'opp_id': result[8],
                'pass_att': result[9], 'pass_comp': result[10], 'pass_yards': result[11], 'pass_td': result[12],
                'pass_longest': result[13], 'ints': result[14], 'sacks': result[15], 'rush_att': result[16],
                'rush_yards': result[17], 'rush_td': result[18], 'rush_longest': result[19], 'targets': result[20],
                'rec': result[21], 'rec_yards': result[22], 'rec_td': result[23], 'rec_longest': result[24],
                'fumbles': result[25]}

        df_merge = pd.DataFrame(item, index=[0])  # CREATE THE DATAFRAME THAT WILL BE MERGED
        df_final = pd.concat([df_final, df_merge])

    # get the number of games played total/current/prior/third
    total_player_games = len(df_final)
    current_total_games = len(df_final.loc[df_final['Year'] == 2024])
    prior_total_games = len(df_final.loc[df_final['Year'] == 2023])
    third_total_games = len(df_final.loc[df_final['Year'] == 2022])

    # initialize the json_output dict variable
    json_output = {}

    # get the occurrence in the previous four games
    df_last_four = df_final.sort_values(by=['Year', 'Week'], ascending=False)  # sort values by most recent games
    # select last four games
    df_last_four = df_last_four.head(4)
    if operator == 'over':
        df_last_four = df_last_four.loc[df_last_four[column_name] > value]
    else:
        df_last_four = df_last_four.loc[df_last_four[column_name] <= value]
    last_four_bet_occurrence = len(df_last_four)
    last_four_percentage = str(round(((last_four_bet_occurrence/4) *100))) + '%'
    json_output['occurrence_last_four'] = last_four_percentage

    # get the occurrence in the previous eight games
    df_last_eight = df_final.sort_values(by=['Year', 'Week'], ascending=False)  # sort values by most recent games
    # select last eight games
    df_last_eight = df_last_eight.head(8)
    if operator == 'over':
        df_last_eight = df_last_eight.loc[df_last_eight[column_name] > value]
    else:
        df_last_eight = df_last_eight.loc[df_last_eight[column_name] <= value]
    last_eight_bet_occurrence = len(df_last_eight)
    last_eight_percentage = str(round(((last_eight_bet_occurrence/8) *100))) + '%'
    json_output['occurrence_last_eight'] = last_eight_percentage


    # determine what df_final will be for the total/current/prior/third dataframes
    if operator == '>':
        df_final = df_final.loc[df_final[column_name] > value]
    else:
        df_final = df_final.loc[df_final[column_name] <= value]

    # get total bet occurrence
    df_total_occurrence = df_final
    total_bet_occurrence = len(df_total_occurrence)
    total_percentage = str(round(((total_bet_occurrence/total_player_games) *100))) + '%'
    json_output['occurrence_total'] = total_percentage
    json_output['total_player_games'] = total_player_games

    # get the bet current year occurrence
    df_current_occurrence = df_final
    current_bet_occurrence = len(df_current_occurrence)
    # current_percentage = str(round(((current_bet_occurrence/current_total_games) *100), 2)) + '%'
    # json_output['occurrence_current'] = current_percentage

    # get the bet prior year occurrence
    df_prior_year = df_final.loc[df_final['Year'] == 2023]
    prior_bet_occurrence = len(df_prior_year)
    prior_percentage = str(round(((prior_bet_occurrence/prior_total_games) *100))) + '%'
    json_output['occurrence_prior'] = prior_percentage
    json_output['prior_total_games'] = prior_total_games

    # get the bet third year occurrence
    df_third_year = df_final.loc[df_final['Year'] == 2022]
    third_bet_occurrence = len(df_third_year)
    third_percentage = str(round(((third_bet_occurrence/third_total_games) *100))) + '%'
    json_output['occurrence_third'] = third_percentage
    json_output['third_total_games'] = third_total_games


    # Enable Access-Control-Allow-Origin
    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output



@nfl.route('/nfl/games', methods=['GET'])
def nfl_get_games():
    id = request.args.get('id', None)
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM nfl_games
                    WHERE home_id = %s OR away_id = %s ''',
                   [id, id])
    results = list(cursor.fetchall())
    result_list = []
    for result in results:
        player_dict = {'id': result[0], 'week': result[1], 'year': result[2], 'home_id': result[3], 'home_score': result[4],
                       'away_team_id': result[5], 'away_score': result[6], 'winner': result[7], 'margin_of_victory': result[8],
                       'weather': result[9], 'vegas_line': result[10], 'vegas_line_result': result[11], 'over_under': result[12],
                       'over_under_result': result[13]}
        result_list.append(player_dict)
    # Enable Access-Control-Allow-Origin
    result_list = jsonify(result_list)
    result_list.headers.add("Access-Control-Allow-Origin", "*")
    return result_list



@nfl.route('/nfl/rz_stat', methods=['GET'])
def nfl_get_rz_stat():
    player_id = request.args.get('player_id', None)
    year = request.args.get('year', None)
    # prior_yr = int(year) - 2
    connection = create_connection()
    cursor = connection.cursor()

    query = f'''SELECT CONCAT(player.first_name, ' ', player.last_name), nfl_redzone_stats.*
                FROM nfl_redzone_stats
                JOIN player ON player.id = nfl_redzone_stats.player_id
                WHERE nfl_redzone_stats.player_id = %s AND nfl_redzone_stats.year = %s'''

    vals = [player_id, year]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())

    output = []
    for result in results:
        item = {'name': result[0], 'id': result[1], 'player_id': result[2], 'year': result[3],
        'rz_20_pass_att': result[4], 'rz_20_pass_comp': result[5],  'rz_20_pass_comp_percentage': result[6], 'rz_20_pass_yard': result[7],
                'rz_20_pass_td': result[8], 'rz_20_pass_int': result[9],
        'rz_10_pass_att': result[10], 'rz_10_pass_comp': result[11], 'rz_10_comp_percentage': result[12], 'rz_10_pass_yard': result[13],
                'rz_10_pass_td': result[14], 'rz_10_pass_int': result[15],
        'rz_20_targets': result[16], 'rz_20_receptions': result[17], 'rz_20_rec_yards': result[18], 'rz_20_catch_percentage': result[19],
                'rz_20_rec_td': result[20], 'rz_20_target_percentage': result[21],
        'rz_10_targets': result[22], 'rz_10_receptions': result[23], 'rz_10_rec_yards': result[24], 'rz_10_catch_percentage': result[25],
              'rz_10_rec_td': result[26], 'rz_10_target_percentage': result[27],
        'rz_20_rush_att': result[28], 'rz_20_rush_yards': result[29], 'rz_20_rush_td': result[30], 'rz_20_rush_percentage': result[31],
        'rz_10_rush_att': result[32], 'rz_10_rush_yards': result[33], 'rz_10_rush_td': result[34], 'rz_10_rush_percentage': result[35],
        'rz_5_rush_att': result[36], 'rz_5_rush_yards': result[37], 'rz_5_rush_td': result[38], 'rz_5_rush_percentage': result[39]}
        if item not in output:
            output.append(item)

    # Enable Access-Control-Allow-Origin
    output = jsonify(output)
    output.headers.add("Access-Control-Allow-Origin", "*")
    return output


@nfl.route('/nfl/team_stats', methods=['GET'])
def nfl_get_team_stats():
    team_id = request.args.get('id', None)

    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name,  nfl_team_offense.*, nfl_team_defense.*
                FROM nfl_team_offense
                JOIN team ON team.id = nfl_team_offense.team_id
                JOIN nfl_team_defense ON (nfl_team_defense.team_id =  nfl_team_offense.team_id) AND (nfl_team_defense.year =  nfl_team_offense.year)
                WHERE team.id = %s'''
    vals = [team_id]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())
    output = []
    for result in results:
        item = {'name': result[0], 'id': result[1], 'team_id': result[2], 'year': result[3], 'games': result[4], 'off_dvoa': result[5],
                'off_epa': result[6], 'dropback_epa': result[7], 'dropback_sr': result[8], 'rush_epa': result[9], 'rush_sr': result[10],
                'pass_att': result[11], 'pass_comp': result[12], 'pass_yards': result[13], 'pass_td': result[14], 'int_thrown': result[15],
                'pass_yard_att': result[16], 'pass_yards_per_game': result[17], 'sacks_taken': result[18], 'rush_att': result[19],
                'rush_yards': result[20], 'rush_td': result[21], 'rush_yards_per_att': result[22], 'rush_yards_per_game': result[23],
                'fumbles_lost': result[24], 'points_scored': result[25], 'points_scored_per_game': result[26], 'off_rz_plays': result[27],
                'off_rz_td': result[28], 'total_drives': result[29], 'total_plays': result[30],  'scoring_percentage': result[31],
                'to_percentage': result[32], 'avg_drive_play': result[33], 'avg_drive_points': result[34], 'avg_drive_yards': result[35], 'def_id': result[36],
                'def_dvoa': result[40], 'def_epa': result[41], 'def_dropback_epa': result[42], 'def_dropback_sr': result[43], 'def_rush_epa': result[44],
                'def_rush_sr': result[45], 'pass_comp_allowed': result[46], 'pass_att_faced': result[47], 'pass_yards_allowed': result[48],
                'pass_td_allowed': result[49], 'allowed_pyards_per_att': result[50], 'allowed_pyards_per_game': result[51], 'qb_hits': result[52],
                'qb_sacks': result[53], 'ints': result[54], 'rush_att_faced': result[55], 'rush_yards_allowed': result[56], 'rush_td_allowed': result[57],
                'allowed_ryards_per_att': result[58], 'allowed_ryards_per_game': result[59], 'rec_allowed': result[60], 'rec_td_allowed': result[61],
                'points_allowed': result[62], 'points_per_game_allowed': result[63], 'rz_att_faced': result[64], 'rz_td_allowed': result[65],
                'rz_td_allowed_percentage': result[66], 'drives_faced': result[67], 'plays_faced': result[68], 'score_against_percentage': result[69],
                'def_to_percentage': result[70], 'plays_faced_per_drive': result[71], 'yards_allowed_per_drive': result[72], 'points_allowed_per_drive': result[73],
                'TE_targets': result[74], 'TE_rec': result[75], 'TE_yards': result[76], 'TE_td': result[77], 'WR_targets': result[78],
                'WR_rec': result[79], 'WR_yards': result[80], 'WR_td': result[81], 'RB_targets': result[82], 'RB_rec': result[83],
                'RB_rec_yards': result[84], 'RB_rec_td': result[85], 'RB_att': result[86], 'RB_rush_yards': result[87], 'RB_rush_td': result[88],
                'QB_completions': result[89], 'QB_att': result[90], 'QB_yards': result[91], 'QB_rush_att': result[92], 'QB_rush_yards': result[93],
                'QB_rush_td': result[94]}
        if item not in output:
            output.append(item)

    # Enable Access-Control-Allow-Origin
    output = jsonify(output)
    output.headers.add("Access-Control-Allow-Origin", "*")
    return output


@nfl.route('/nfl/team_offense', methods=['GET'])
def nfl_get_off_stats():
    team_id = request.args.get('id', None)
    year = request.args.get('year', None)
    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name,  nfl_team_offense.*
                FROM nfl_team_offense
                JOIN team ON team.id = nfl_team_offense.team_id 
                WHERE team.id = %s AND nfl_team_offense.year = %s'''
    vals = [team_id, year]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())
    output = []
    for result in results:
        item = {'name': result[0], 'id': result[1], 'team_id': result[2], 'year': result[3], 'games': result[4], 'dvoa': result[5],
        'epa_per_play': result[6], 'success_rate': result[7], 'dropback_epa': result[8], 'dropback_sr': result[9], 'rush_epa': result[10],
        'rush_sr': result[11], 'pass_comp': result[12], 'pass_att': result[13], 'pass_comp_percentage': result[14], 'pass_yards': result[15],
        'pass_td': result[16], 'pass_td_percentage': result[17], 'yards_per_att': result[18], 'pass_yards_per_comp': result[19],
        'pass_yards_per_game': result[20], 'passer_rating': result[21], 'sacks': result[22], 'ints': result[23], 'int_percentage': result[24],
        'rush_att': result[25], 'rush_yards': result[26], 'rush_td': result[27], 'rush_yards_per_att': result[28], 'rush_yards_per_game': result[29],
        'fumbles': result[30], 'total_points': result[31], 'points_per_game': result[32], 'drives': result[33], 'plays': result[34],
        'scoring_percentage': result[35], 'to_percentage': result[36], 'plays_per_drive': result[37], 'yards_per_drive': result[38],
        'points_per_drive': result[39], 'third_down_att': result[40], 'third_down_conv': result[41], 'third_down_conv_rate': result[42],
        'fourth_down_att': result[43], 'fourth_down_conv': result[44], 'fourth_down_conv_rate': result[45], 'rz_att': result[46],
        'rz_td':result[47], 'rz_percentage': result[48]}
        if item not in output:
            output.append(item)

    # Enable Access-Control-Allow-Origin
    output = jsonify(output)
    output.headers.add("Access-Control-Allow-Origin", "*")
    return output


@nfl.route('/nfl/team_defense', methods=['GET'])
def nfl_get_team_def_stats():
    team_id = request.args.get('id', None)
    year = request.args.get('year', None)
    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name,  nfl_team_defense.*
                FROM nfl_team_defense
                JOIN team ON team.id = nfl_team_defense.team_id
                WHERE team.id = %s AND nfl_team_defense.year = %s'''
    vals = [team_id, year]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())

    output = []
    for result in results:
        item = {'name': result[0], 'id': result[1], 'team_id': result[2], 'year': result[3], 'games': result[4], 'dvoa': result[5],
                'epa_per_play': result[6], 'success_rate': result[7], 'dropback_epa': result[8], 'dropback_sr': result[9],
                'rush_epa': result[10], 'rush_sr': result[11], 'pass_comp': result[12], 'pass_att': result[13],
                'pass_comp_percentage': result[14], 'pass_yards': result[15], 'pass_td': result[16], 'pass_td_percentage':result[17],
                'yards_per_att': result[18], 'pass_yards_per_comp': result[19], 'pass_yards_per_game': result[20], 'passer_rating': result[21],
                'qb_hits': result[22], 'sacks': result[23], 'ints': result[24],
                'int_percentage': result[25], 'pass_deflections': result[26], 'rush_att': result[27], 'rush_yards': result[28],
                'rush_td': result[29], 'rush_yards_per_att': result[30], 'rush_yards_per_game': result[31], 'points_per_game': result[32],
                'total_points': result[33], 'drives': result[34], 'plays': result[35], 'scoring_percentage': result[36],
                'to_percentage': result[37], 'plays_per_drive': result[38], 'yards_per_drive': result[39],
                'points_per_drive': result[40], 'third_down_att': result[41], 'third_down_conv': result[42], 'third_down_conv_rate': result[43], 'fourth_down_att': result[44],
                'fourth_down_conv': result[45], 'fourth_down_conv_rate': result[46], 'rz_att': result[47], 'rz_td': result[48], 'rz_percentage': result[49],
                'qb_rush_att': result[50], 'qb_rush_yards': result[51], 'qb_rush_td': result[52], 'rb_att': result[53], 'rb_yards': result[54],
                'rb_td': result[55], 'rb_targets': result[56], 'rb_rec': result[57], 'rb_rec_yards': result[58], 'rb_rec_td': result[59],
                'wr_targets': result[60], 'wr_rec': result[61],  'wr_yards': result[62],  'wr_td': result[63],  'te_targets': result[64],
                'te_rec': result[65],  'te_yards': result[66],  'te_td': result[67]}

        if item not in output:
            output.append(item)

    # Enable Access-Control-Allow-Origin
    output = jsonify(output)
    output.headers.add("Access-Control-Allow-Origin", "*")
    return output

# GET PLAYERS TOTAL GAMES
@nfl.route('nfl/player_total_games', methods=['GET'])
def nfl_player_total_games():
    player_id = request.args.get('id', None)
    connection = create_connection()
    cursor = connection.cursor()
    print(f"player_id = {player_id}")

    query = f'''SELECT COUNT(game_id) AS game_count 
                FROM nfl_player_stats
                WHERE player_id = %s'''
    vals = [player_id]
    cursor.execute(query, vals)

    result = cursor.fetchone()[0]
    output = jsonify({'total_games': result})
    return output
# GET NFL STAT RANK
@nfl.route('nfl/stat_rank', methods=['GET'])
def nfl_stat_rank():
    # INITIALIZE VARIABLES
    team_id = int(request.args.get('id', None))
    table_name = request.args.get('table_name', None)
    stat = request.args.get('stat', None)
    connection = create_connection()
    cursor = connection.cursor()
    rank_col = stat + '_rank'
    years = list(range(2019, 2024))

    output = []
    for year in years:
        query = f"""SELECT id, team_id, year, {stat},RANK() 
                    OVER (ORDER BY {stat}) as {rank_col} 
                    FROM {table_name}
                    WHERE year = %s"""
        vals = [year]
        cursor.execute(query, vals)

        results = cursor.fetchall()

        for result in results:
            if result[1] == team_id:
                item = {'team_id': result[1], 'year': result[2], stat: result[3], rank_col: result[4]}
                output.append(item)

    return jsonify(output)



@nfl.route('/nfl/standings', methods=['GET'])
def nfl_get_standings():
    team_id = request.args.get('id', None)
    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT * FROM nfl_standings
                WHERE team_id = %s'''
    vals = [team_id]
    cursor.execute(query, vals)

    results = cursor.fetchall()

    output = []
    for result in results:
        result = {'id': result[0], 'year': result[1] , 'team_id': result[2], 'wins': result[3], 'losses': result[4], 'ties': result[5],
                  'win_loss_percentage': result[6], 'points_for': result[7], 'points_against': result[8], 'point_diff': result[9],
                  'avg_margin_of_victory': result[10], 'strength_of_schedule': result[11]}
        output.append(result)

    # Enable Access-Control-Allow-Origin
    output = jsonify(output)
    output.headers.add("Access-Control-Allow-Origin", "*")
    return output
