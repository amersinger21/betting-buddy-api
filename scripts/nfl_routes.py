from .db import create_connection
from flask import Blueprint, request, jsonify

nfl = Blueprint("nfl", __name__)

@nfl.route('/nfl/player_stats', methods=['POST'])
def nfl_add_player_stats(json_dict):
    game_id = json_dict['game_id']
    player_id = json_dict['player_id']
    team_id = json_dict['team_id']
    opp_id = json_dict['opp_id']
    pass_att = json_dict['pass_att']
    pass_comp = json_dict['pass_comp']
    pass_yards = json_dict['pass_yards']
    pass_td = json_dict['pass_td']
    pass_longest = json_dict['pass_longest']
    ints = json_dict['ints']
    sacks = json_dict['sacks']
    rush_att = json_dict['rush_att']
    rush_yards = json_dict['rush_yards']
    rush_td = json_dict['rush_td']
    rush_longest = json_dict['rush_longest']
    targets = json_dict['targets']
    rec = json_dict['rec']
    rec_yards = json_dict['rec_yards']
    rec_td = json_dict['rec_td']
    rec_longest = json_dict['rec_longest']
    fumbles = json_dict['fumbles']


    values = (game_id, player_id, team_id, opp_id, pass_att, pass_comp, pass_yards, pass_td, pass_longest, ints,
              sacks, rush_att, rush_yards, rush_td, rush_longest, targets, rec, rec_yards, rec_td, rec_longest, fumbles)

    connection = create_connection()
    cursor=connection.cursor()

    cursor.execute("""INSERT INTO nfl_player_stats (game_id, player_id, team_id, opp_id, pass_att, pass_comp, pass_yards, pass_td, pass_longest, 
                    ints, sacks, rush_att, rush_yards, rush_td, rush_longest, targets, rec, rec_yards, rec_td, rec_longest, fumbles) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))

    connection.commit()
    print(f"Game has been added to games tabel.")


    result = {'game_id': game_id, 'player_id': player_id,'team_id': team_id, 'opp_id': opp_id, 'pass_att': pass_att,
              'pass_comp': pass_comp, 'pass_yards': pass_yards, 'pass_td': pass_td, 'pass_longest':pass_longest, 'ints': ints,
              'sacks': sacks, 'rush_att': rush_att, 'rush_yards': rush_yards, 'rush_td': rush_td, 'rush_longest': rush_longest,
              'targets': targets, 'rec': rec, 'rec_yards': rec_yards, 'rec_td': rec_td, 'rec_longest': rec_longest, 'fumbles':fumbles}

    return result
@nfl.route('/nfl/player_stats', methods=['GET'])
def nfl_get_player_stats():
    player_id = request.args.get('id', None)
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = float(request.args.get('value', None))
    connection = create_connection()
    cursor = connection.cursor()
    print(f"player_id = {player_id}")
    print(f"value = {value}")
    print(f"operator = {operator}")

    column = 'nfl_player_stats.' + column_name
    print(f"column = {column}")

    if operator == 'over':
        op_val = '>'
    else:
        op_val = '<'

    query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name,
                    player.position, nfl_player_stats.*
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    WHERE player.id = %s AND {column} {op_val} %s'''
    vals = [player_id, value]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())
    # print(f"This bet hit {len(results)} times.")
    occurrence_dict = {'total_hits': len(results)}
    # return results
    output = [occurrence_dict]
    for result in results:
        item = {}
        item['name'] = result[0]
        item['pos'] = result[1]
        item['id'] = result[2]
        item['game_id'] = result[3]
        item['player_id'] = result[4]
        item['team_id'] = result[5]
        item['opp_id'] = result[6]
        item['pass_att'] = result[7]
        item['pass_comp'] = result[8]
        item['pass_yards'] = result[9]
        item['pass_td'] = result[10]
        item['pass_longest'] = result[11]
        item['ints'] = result[12]
        item['sacks'] = result[13]
        item['rush_att'] = result[14]
        item['rush_yards'] = result[15]
        item['rush_td'] = result[16]
        item['rush_longest'] = result[17]
        item['targets'] = result[18]
        item['rec'] = result[19]
        item['rec_yards'] = result[20]
        item['rec_td'] = result[21]
        item['rec_longest'] = result[22]
        item['fumbles'] = result[23]
        output.append(item)

    return output


@nfl.route('/nfl/team', methods=['GET'])
def nfl_get_team():
    team_id = request.args.get('id', None)
    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name,  fb_off_stats.*, fb_def_stats.*
                FROM fb_off_stats
                JOIN team ON team.id = fb_off_stats.team_id 
                JOIN fb_def_stats ON (fb_def_stats.team_id =  fb_off_stats.team_id) AND (fb_def_stats.year =  fb_off_stats.year)
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

    return output

# GAME INFO ROUTES
@nfl.route('/nfl/games', methods=['POST'])
def nfl_add_game(json_dict):
    week = json_dict['week']
    year = json_dict['year']
    home_id = json_dict['home_id']
    home_score = json_dict['home_score']
    away_id = json_dict['away_id']
    away_score = json_dict['away_score']
    winner = json_dict['winner']
    margin_of_victory = json_dict['margin_of_victory']
    weather_id = json_dict['weather_id']
    vegas_line = json_dict['vegas_line']
    vegas_line_result = json_dict['vegas_line_result']
    over_under = json_dict['over_under']
    over_under_result = json_dict['over_under_result']

    values = (week, year, home_id, home_score, away_id, away_score, winner, margin_of_victory, weather_id, vegas_line,
              vegas_line_result, over_under, over_under_result)

    connection = create_connection()
    cursor=connection.cursor()

    cursor.execute('''INSERT INTO nfl_games (week, year, home_id, home_score, away_id, away_score, winner, margin_of_victory, weather_id, vegas_line,
              vegas_line_result, over_under, over_under_result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                   (values))
    connection.commit()

    result = { 'week': week, 'year': year, 'home_team': home_id, 'home_score': home_score, 'away_team': away_id, 'away_score': away_score,
               'winner': winner, 'margin_of_victory': margin_of_victory, 'weather_id': weather_id, 'vegas_line': vegas_line,
               'vegas_line_result': vegas_line_result,'over_under': over_under, 'over_under_result': over_under_result}

    return result
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
    return result_list


# RED ZONE STATS:
@nfl.route('/nfl/rz_stat', methods=['POST'])
def nfl_add_rz_stat(json_dict):
    player_id = json_dict['player_id']
    year = json_dict['year']
    rz_20_pass_att = json_dict['rz_20_pass_att']
    rz_20_pass_comp = json_dict['rz_20_pass_comp']
    rz_20_comp_percentage = json_dict['rz_20_comp_percentage']
    rz_20_pass_yards = json_dict['rz_20_pass_yards']
    rz_20_pass_td = json_dict['rz_20_pass_td']
    rz_20_pass_int = json_dict['rz_20_pass_int']
    rz_10_pass_att = json_dict['rz_10_pass_att']
    rz_10_pass_comp = json_dict['rz_10_pass_comp']
    rz_10_comp_percentage = json_dict['rz_10_comp_percentage']
    rz_10_pass_yards = json_dict['rz_10_pass_yards']
    rz_10_pass_td = json_dict['rz_10_pass_td']
    rz_10_pass_int = json_dict['rz_10_pass_int']
    rz_20_targets = json_dict['rz_20_targets']
    rz_20_receptions = json_dict['rz_20_receptions']
    rz_20_rec_yards = json_dict['rz_20_rec_yards']
    rz_20_catch_percentage = json_dict['rz_20_catch_percentage']
    rz_20_rec_td = json_dict['rz_20_rec_td']
    rz_20_target_percentage = json_dict['rz_20_target_percentage']
    rz_10_targets = json_dict['rz_10_targets']
    rz_10_receptions = json_dict['rz_10_receptions']
    rz_10_rec_yards = json_dict['rz_10_rec_yards']
    rz_10_catch_percentage = json_dict['rz_10_catch_percentage']
    rz_10_rec_td = json_dict['rz_10_rec_td']
    rz_10_target_percentage = json_dict['rz_10_target_percentage']
    rz_20_rush_att = json_dict['rz_20_rush_att']
    rz_20_rush_yards = json_dict['rz_20_rush_yards']
    rz_20_rush_td = json_dict['rz_20_rush_td']
    rz_20_rush_percentage = json_dict['rz_20_rush_percentage']
    rz_10_rush_att = json_dict['rz_10_rush_att']
    rz_10_rush_yards = json_dict['rz_10_rush_yards']
    rz_10_rush_td = json_dict['rz_10_rush_td']
    rz_10_rush_percentage = json_dict['rz_10_rush_percentage']
    rz_5_rush_att = json_dict['rz_5_rush_att']
    rz_5_rush_yards = json_dict['rz_5_rush_yards']
    rz_5_rush_td = json_dict['rz_5_rush_td']
    rz_5_rush_percentage = json_dict['rz_5_rush_percentage']

    values = (player_id, year, rz_20_pass_att, rz_20_pass_comp, rz_20_comp_percentage, rz_20_pass_yards, rz_20_pass_td, rz_20_pass_int,
              rz_10_pass_att, rz_10_pass_comp, rz_10_comp_percentage, rz_10_pass_yards, rz_10_pass_td, rz_10_pass_int, rz_20_targets, rz_20_receptions,
              rz_20_rec_yards, rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions,
              rz_10_rec_yards, rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_yards,
              rz_20_rush_td, rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_yards, rz_10_rush_td, rz_10_rush_percentage,
              rz_5_rush_att, rz_5_rush_yards, rz_5_rush_td, rz_5_rush_percentage)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO nfl_redzone_stats (player_id, year, rz_20_pass_att, rz_20_pass_comp, rz_20_comp_percentage, rz_20_pass_yards, rz_20_pass_td, rz_20_pass_int,
              rz_10_pass_att, rz_10_pass_comp, rz_10_comp_percentage, rz_10_pass_yards, rz_10_pass_td, rz_10_pass_int, rz_20_targets, rz_20_receptions,
              rz_20_rec_yards, rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions,
              rz_10_rec_yards, rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_yards,
              rz_20_rush_td, rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_yards, rz_10_rush_td, rz_10_rush_percentage,
              rz_5_rush_att, rz_5_rush_yards, rz_5_rush_td, rz_5_rush_percentage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))
    connection.commit()
    print(f"Game has been added to games table.")


    result = {'player_id':player_id, 'year': year, 'rz_20_pass_att': rz_20_pass_att, 'rz_20_pass_comp': rz_20_pass_comp,  'rz_20_pass_comp_percentage': rz_20_comp_percentage,
              'rz_20_pass_yard': rz_20_pass_yards, 'rz_20_pass_td': rz_20_pass_td, 'rz_20_pass_int': rz_20_pass_int,
              'rz_10_pass_att': rz_10_pass_att, 'rz_10_pass_comp': rz_10_pass_comp, 'rz_10_comp_percentage': rz_10_comp_percentage,
              'rz_10_pass_yard': rz_10_pass_yards, 'rz_10_pass_td': rz_10_pass_td, 'rz_10_pass_int': rz_10_pass_int,
              'rz_20_targets': rz_20_targets, 'rz_20_receptions': rz_20_receptions,
              'rz_20_rec_yards': rz_20_rec_yards, 'rz_20_catch_percentage': rz_20_catch_percentage, 'rz_20_rec_td': rz_20_rec_td, 'rz_20_target_percentage': rz_20_target_percentage,
              'rz_10_targets': rz_10_targets, 'rz_10_receptions': rz_10_targets, 'rz_10_rec_yards': rz_10_rec_yards, 'rz_10_catch_percentage': rz_10_catch_percentage,
              'rz_10_rec_td': rz_10_rec_td, 'rz_10_target_percentage': rz_10_target_percentage, 'rz_20_rush_att': rz_10_target_percentage, 'rz_20_rush_td': rz_20_rush_td,
              'rz_20_rush_yards': rz_20_rush_yards, 'rz_20_rush_percentage': rz_20_rush_percentage, 'rz_10_rush_att': rz_10_rush_att,
              'rz_10_rush_td': rz_10_rush_td, 'rz_10_rush_yards': rz_10_rush_yards, 'rz_10_rush_percentage': rz_10_rush_percentage,
              'rz_5_rush_att': rz_5_rush_att, 'rz_5_rush_td': rz_5_rush_att, 'rz_5_rush_yards': rz_5_rush_yards, 'rz_5_rush_percentage': rz_5_rush_percentage}

    return result
@nfl.route('/nfl/rz_stat', methods=['PUT'])
def nfl_update_rz_stat(json_dict):
    player_id = json_dict['player_id']
    year = json_dict['year']
    rz_20_pass_att = json_dict['rz_20_pass_att']
    rz_20_pass_comp = json_dict['rz_20_pass_comp']
    rz_20_comp_percentage = json_dict['rz_20_comp_percentage']
    rz_20_pass_yards = json_dict['rz_20_pass_yards']
    rz_20_pass_td = json_dict['rz_20_pass_td']
    rz_20_pass_int = json_dict['rz_20_pass_int']
    rz_10_pass_att = json_dict['rz_10_pass_att']
    rz_10_pass_comp = json_dict['rz_10_pass_comp']
    rz_10_comp_percentage = json_dict['rz_10_comp_percentage']
    rz_10_pass_yards = json_dict['rz_10_pass_yards']
    rz_10_pass_td = json_dict['rz_10_pass_td']
    rz_10_pass_int = json_dict['rz_10_pass_int']
    rz_20_targets = json_dict['rz_20_targets']
    rz_20_receptions = json_dict['rz_20_receptions']
    rz_20_rec_yards = json_dict['rz_20_rec_yards']
    rz_20_catch_percentage = json_dict['rz_20_catch_percentage']
    rz_20_rec_td = json_dict['rz_20_rec_td']
    rz_20_target_percentage = json_dict['rz_20_target_percentage']
    rz_10_targets = json_dict['rz_10_targets']
    rz_10_receptions = json_dict['rz_10_receptions']
    rz_10_rec_yards = json_dict['rz_10_rec_yards']
    rz_10_catch_percentage = json_dict['rz_10_catch_percentage']
    rz_10_rec_td = json_dict['rz_10_rec_td']
    rz_10_target_percentage = json_dict['rz_10_target_percentage']
    rz_20_rush_att = json_dict['rz_20_rush_att']
    rz_20_rush_yards = json_dict['rz_20_rush_yards']
    rz_20_rush_td = json_dict['rz_20_rush_td']
    rz_20_rush_percentage = json_dict['rz_20_rush_percentage']
    rz_10_rush_att = json_dict['rz_10_rush_att']
    rz_10_rush_yards = json_dict['rz_10_rush_yards']
    rz_10_rush_td = json_dict['rz_10_rush_td']
    rz_10_rush_percentage = json_dict['rz_10_rush_percentage']
    rz_5_rush_att = json_dict['rz_5_rush_att']
    rz_5_rush_yards = json_dict['rz_5_rush_yards']
    rz_5_rush_td = json_dict['rz_5_rush_td']
    rz_5_rush_percentage = json_dict['rz_5_rush_percentage']

    values = (rz_20_pass_att, rz_20_pass_comp, rz_20_comp_percentage, rz_20_pass_yards, rz_20_pass_td, rz_20_pass_int,
              rz_10_pass_att, rz_10_pass_comp, rz_10_comp_percentage, rz_10_pass_yards, rz_10_pass_td, rz_10_pass_int, rz_20_targets, rz_20_receptions,
              rz_20_rec_yards, rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions,
              rz_10_rec_yards, rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_yards,
              rz_20_rush_td, rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_yards, rz_10_rush_td, rz_10_rush_percentage,
              rz_5_rush_att, rz_5_rush_yards, rz_5_rush_td, rz_5_rush_percentage, player_id, year)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""UPDATE nfl_redzone_stats 
            SET rz_20_pass_att = %s, rz_20_pass_comp = %s, rz_20_comp_percentage = %s, rz_20_pass_yards = %s, rz_20_pass_td = %s, rz_20_pass_int = %s,
                rz_10_pass_att = %s, rz_10_pass_comp = %s, rz_10_comp_percentage = %s, rz_10_pass_yards = %s, rz_10_pass_td = %s, 
                rz_10_pass_int = %s, rz_20_targets = %s, rz_20_receptions = %s, rz_20_rec_yards = %s, rz_20_catch_percentage = %s, 
                rz_20_rec_td = %s, rz_20_target_percentage = %s, rz_10_targets = %s, rz_10_receptions = %s, rz_10_rec_yards = %s, 
                rz_10_catch_percentage = %s, rz_10_rec_td = %s, rz_10_target_percentage = %s, rz_20_rush_att = %s, rz_20_rush_td = %s,
                rz_20_rush_yards = %s, rz_20_rush_percentage = %s, rz_10_rush_att = %s, rz_10_rush_td = %s, rz_10_rush_yards = %s, 
                rz_10_rush_percentage = %s, rz_5_rush_att = %s, rz_5_rush_td = %s, rz_5_rush_yards = %s, rz_5_rush_percentage = %s 
            WHERE nfl_redzone_stats.player_id = %s AND nfl_redzone_stats.year = %s""",
                   (values))
    connection.commit()
    print(f"Game has been added to games table.")


    result = {'player_id':player_id, 'year': year, 'rz_20_pass_att': rz_20_pass_att, 'rz_20_pass_comp': rz_20_pass_comp,  'rz_20_pass_comp_percentage': rz_20_comp_percentage,
              'rz_20_pass_yard': rz_20_pass_yards, 'rz_20_pass_td': rz_20_pass_td, 'rz_20_pass_int': rz_20_pass_int,
              'rz_10_pass_att': rz_10_pass_att, 'rz_10_pass_comp': rz_10_pass_comp, 'rz_10_pass_yard': rz_10_pass_yards, 'rz_10_pass_td': rz_10_pass_td, 'rz_10_pass_int': rz_10_pass_int,
              'rz_10_comp_percentage': rz_10_comp_percentage, 'rz_20_targets': rz_20_targets, 'rz_20_receptions': rz_20_receptions,
              'rz_20_rec_yards': rz_20_rec_yards, 'rz_20_catch_percentage': rz_20_catch_percentage, 'rz_20_rec_td': rz_20_rec_td, 'rz_20_target_percentage': rz_20_target_percentage,
              'rz_10_targets': rz_10_targets, 'rz_10_receptions': rz_10_targets, 'rz_10_rec_yards': rz_10_rec_yards, 'rz_10_catch_percentage': rz_10_catch_percentage,
              'rz_10_rec_td': rz_10_rec_td, 'rz_10_target_percentage': rz_10_target_percentage, 'rz_20_rush_att': rz_10_target_percentage, 'rz_20_rush_td': rz_20_rush_td,
              'rz_20_rush_yards': rz_20_rush_yards, 'rz_20_rush_percentage': rz_20_rush_percentage, 'rz_10_rush_att': rz_10_rush_att,
              'rz_10_rush_td': rz_10_rush_td, 'rz_10_rush_yards': rz_10_rush_yards, 'rz_10_rush_percentage': rz_10_rush_percentage,
              'rz_5_rush_att': rz_5_rush_att, 'rz_5_rush_td': rz_5_rush_att, 'rz_5_rush_yards': rz_5_rush_yards, 'rz_5_rush_percentage': rz_5_rush_percentage}

    return result
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
    return output



@nfl.route('/nfl/team_stats', methods=['GET'])
def nfl_get_team_stats():
    team_id = request.args.get('id', None)
    year = request.args.get('year', None)
    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name,  fb_off_stats.*, fb_def_stats.*
                FROM fb_off_stats
                JOIN team ON team.id = fb_off_stats.team_id
                JOIN fb_def_stats ON (fb_def_stats.team_id =  fb_off_stats.team_id) AND (fb_def_stats.year =  fb_off_stats.year)
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

    return output



# NFL TEAM OFFENSE ROUTES
@nfl.route('/nfl/team_offense', methods=['POST'])
def nfl_add_team_off_stats(json_dict):
    team_id = json_dict['team_id']
    year = json_dict['year']
    games = json_dict['games']
    dvoa = json_dict['dvoa']
    epa_per_play = json_dict['epa_per_play']
    success_rate = json_dict['success_rate']
    dropback_epa = json_dict['dropback_epa']
    dropback_sr = json_dict['dropback_sr']
    rush_epa = json_dict['rush_epa']
    rush_sr = json_dict['rush_sr']
    pass_comp = json_dict['pass_comp']
    pass_att = json_dict['pass_att']
    pass_comp_percentage = json_dict['pass_comp_percentage']
    pass_yards = json_dict['pass_yards']
    pass_td = json_dict['pass_td']
    pass_td_percentage = json_dict['pass_td_percentage']
    yards_per_att = json_dict['yards_per_att']
    pass_yards_per_comp = json_dict['pass_yards_per_comp']
    pass_yards_per_game = json_dict['pass_yards_per_game']
    passer_rating = json_dict['passer_rating']
    sacks = json_dict['sacks']
    ints = json_dict['ints']
    int_percentage = json_dict['int_percentage']
    rush_att = json_dict['rush_att']
    rush_yards = json_dict['rush_yards']
    rush_td = json_dict['rush_td']
    rush_yards_per_att = json_dict['rush_yards_per_att']
    rush_yards_per_game = json_dict['rush_yards_per_game']
    fumbles = json_dict['fumbles']
    total_points = json_dict['total_points']
    points_per_game = json_dict['points_per_game']
    drives = json_dict['drives']
    plays = json_dict['plays']
    scoring_percentage = json_dict['scoring_percentage']
    to_percentage = json_dict['to_percentage']
    plays_per_drive = json_dict['plays_per_drive']
    yards_per_drive = json_dict['yards_per_drive']
    points_per_drive = json_dict['points_per_drive']
    third_down_att = json_dict['third_down_att']
    third_down_conv = json_dict['third_down_conv']
    third_down_conv_rate = json_dict['third_down_conv_rate']
    fourth_down_att = json_dict['fourth_down_att']
    fourth_down_conv = json_dict['fourth_down_conv']
    fourth_down_conv_rate = json_dict['fourth_down_conv_rate']
    rz_att = json_dict['rz_att']
    rz_td = json_dict['rz_td']
    rz_percentage = json_dict['rz_percentage']

    values = (team_id, year, games, dvoa, epa_per_play, success_rate, dropback_epa, dropback_sr, rush_epa, rush_sr,
    pass_comp, pass_att, pass_comp_percentage, pass_yards, pass_td, pass_td_percentage, yards_per_att, pass_yards_per_comp,
    pass_yards_per_game, passer_rating, sacks, ints, int_percentage, rush_att, rush_yards, rush_td, rush_yards_per_att,
    rush_yards_per_game, fumbles, total_points, points_per_game, drives, plays, scoring_percentage, to_percentage,
    plays_per_drive, yards_per_drive, points_per_drive, third_down_att, third_down_conv, third_down_conv_rate, fourth_down_att,
    fourth_down_conv, fourth_down_conv_rate, rz_att, rz_td, rz_percentage)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO nfl_team_offense (team_id, year, games, dvoa, epa_per_play, success_rate, dropback_epa, dropback_sr, rush_epa, rush_sr, 
    pass_comp, pass_att, pass_comp_percentage, pass_yards, pass_td, pass_td_percentage, yards_per_att, pass_yards_per_comp, 
    pass_yards_per_game, passer_rating, sacks, ints, int_percentage, rush_att, rush_yards, rush_td, rush_yards_per_att, 
    rush_yards_per_game, fumbles, total_points, points_per_game, drives, plays, scoring_percentage, to_percentage, 
    plays_per_drive, yards_per_drive, points_per_drive, third_down_att, third_down_conv, third_down_conv_rate, fourth_down_att, 
    fourth_down_conv, fourth_down_conv_rate, rz_att, rz_td, rz_percentage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))
    connection.commit()
    print(f"Team {year}  offensive stats has been added to nfl_team_offense table.")


    result = {'team_id': team_id, 'year': year, 'games': games, 'dvoa': dvoa, 'epa_per_play': epa_per_play, 'success_rate': success_rate,
    'dropback_epa': dropback_epa, 'dropback_sr': dropback_sr, 'rush_epa': rush_epa, 'rush_sr': rush_sr, 'pass_comp': pass_comp,
    'pass_att': pass_att, 'pass_comp_percentage': pass_comp_percentage, 'pass_yards': pass_yards, 'pass_td': pass_td, 'pass_td_percentage': pass_td_percentage,
    'yards_per_att': yards_per_att, 'pass_yards_per_comp': pass_yards_per_comp, 'pass_yards_per_game': pass_yards_per_game, 'passer_rating': passer_rating,
    'sacks': sacks, 'ints': ints, 'int_percentage': int_percentage, 'rush_att': rush_att, 'rush_yards': rush_yards, 'rush_td': rush_td,
    'rush_yards_per_att': rush_yards_per_att, 'rush_yards_per_game': rush_yards_per_game, 'fumbles': fumbles, 'total_points': total_points,
    'points_per_game': points_per_game, 'drives': drives, 'plays': plays, 'scoring_percentage': scoring_percentage, 'to_percentage': to_percentage,
    'plays_per_drive': plays_per_drive, 'yards_per_drive': yards_per_drive, 'points_per_drive': points_per_drive, 'third_down_att': third_down_att,
    'third_down_conv': third_down_conv, 'third_down_conv_rate': third_down_conv_rate, 'fourth_down_att': fourth_down_att, 'fourth_down_conv': fourth_down_conv,
    'fourth_down_conv_rate': fourth_down_conv_rate, 'rz_att': rz_att, 'rz_td':rz_td, 'rz_percentage': rz_percentage}
    return result
@nfl.route('/nfl/team_offense', methods=['PUT'])
def nfl_update_team_off_stats(json_dict):
    team_id = json_dict['team_id']
    year = json_dict['year']
    games = json_dict['games']
    dvoa = json_dict['dvoa']
    epa_per_play = json_dict['epa_per_play']
    success_rate = json_dict['success_rate']
    dropback_epa = json_dict['dropback_epa']
    dropback_sr = json_dict['dropback_sr']
    rush_epa = json_dict['rush_epa']
    rush_sr = json_dict['rush_sr']
    pass_comp = json_dict['pass_comp']
    pass_att = json_dict['pass_att']
    pass_comp_percentage = json_dict['pass_comp_percentage']
    pass_yards = json_dict['pass_yards']
    pass_td = json_dict['pass_td']
    pass_td_percentage = json_dict['pass_td_percentage']
    yards_per_att = json_dict['yards_per_att']
    pass_yards_per_comp = json_dict['pass_yards_per_comp']
    pass_yards_per_game = json_dict['pass_yards_per_game']
    passer_rating = json_dict['passer_rating']
    sacks = json_dict['sacks']
    ints = json_dict['ints']
    int_percentage = json_dict['int_percentage']
    rush_att = json_dict['rush_att']
    rush_yards = json_dict['rush_yards']
    rush_td = json_dict['rush_td']
    rush_yards_per_att = json_dict['rush_yards_per_att']
    rush_yards_per_game = json_dict['rush_yards_per_game']
    fumbles = json_dict['fumbles']
    total_points = json_dict['total_points']
    points_per_game = json_dict['points_per_game']
    drives = json_dict['drives']
    plays = json_dict['plays']
    scoring_percentage = json_dict['scoring_percentage']
    to_percentage = json_dict['to_percentage']
    plays_per_drive = json_dict['plays_per_drive']
    yards_per_drive = json_dict['yards_per_drive']
    points_per_drive = json_dict['points_per_drive']
    third_down_att = json_dict['third_down_att']
    third_down_conv = json_dict['third_down_conv']
    third_down_conv_rate = json_dict['third_down_conv_rate']
    fourth_down_att = json_dict['fourth_down_att']
    fourth_down_conv = json_dict['fourth_down_conv']
    fourth_down_conv_rate = json_dict['fourth_down_conv_rate']
    rz_att = json_dict['rz_att']
    rz_td = json_dict['rz_td']
    rz_percentage = json_dict['rz_percentage']


    values = (games, dvoa, epa_per_play, success_rate, dropback_epa, dropback_sr, rush_epa, rush_sr,
    pass_comp, pass_att, pass_comp_percentage, pass_yards, pass_td, pass_td_percentage, yards_per_att, pass_yards_per_comp,
    pass_yards_per_game, passer_rating, sacks, ints, int_percentage, rush_att, rush_yards, rush_td, rush_yards_per_att,
    rush_yards_per_game, fumbles, total_points, points_per_game, drives, plays, scoring_percentage, to_percentage,
    plays_per_drive, yards_per_drive, points_per_drive, third_down_att, third_down_conv, third_down_conv_rate, fourth_down_att,
    fourth_down_conv, fourth_down_conv_rate, rz_att, rz_td, rz_percentage, team_id, year)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""UPDATE nfl_redzone_stats
                    SET games = %s, dvoa = %s, epa_per_play = %s, success_rate = %s, dropback_epa = %s, dropback_sr = %s, 
    rush_epa = %s, rush_sr = %s, pass_comp = %s, pass_att = %s, pass_comp_percentage = %s, pass_yards = %s, pass_td = %s, 
    pass_td_percentage = %s, yards_per_att = %s, pass_yards_per_comp = %s, pass_yards_per_game = %s, passer_rating = %s, sacks = %s, 
    ints = %s, int_percentage = %s, rush_att = %s, rush_yards = %s, rush_td = %s, rush_yards_per_att = %s, rush_yards_per_game = %s, 
    fumbles = %s, total_points = %s, points_per_game = %s, drives = %s, plays = %s, scoring_percentage = %s, to_percentage = %s,
    plays_per_drive = %s, yards_per_drive = %s, points_per_drive = %s, third_down_att = %s, third_down_conv = %s, third_down_conv_rate = %s, 
    fourth_down_att = %s, fourth_down_conv = %s, fourth_down_conv_rate = %s, rz_att = %s, rz_td = %s, rz_percentage = %s
                     WHERE nfl_team_offense.team_id = %s AND nfl_team_offense.year = %s""",
                   (values))
    connection.commit()
    print(f"Team {year}  offensive stats has been added to fb_team_off table.")

    result = {'team_id': team_id, 'year': year, 'games': games, 'dvoa': dvoa, 'epa_per_play': epa_per_play, 'success_rate': success_rate,
    'dropback_epa': dropback_epa, 'dropback_sr': dropback_sr, 'rush_epa': rush_epa, 'rush_sr': rush_sr, 'pass_comp': pass_comp,
    'pass_att': pass_att, 'pass_comp_percentage': pass_comp_percentage, 'pass_yards': pass_yards, 'pass_td': pass_td, 'pass_td_percentage': pass_td_percentage,
    'yards_per_att': yards_per_att, 'pass_yards_per_comp': pass_yards_per_comp, 'pass_yards_per_game': pass_yards_per_game, 'passer_rating': passer_rating,
    'sacks': sacks, 'ints': ints, 'int_percentage': int_percentage, 'rush_att': rush_att, 'rush_yards': rush_yards, 'rush_td': rush_td,
    'rush_yards_per_att': rush_yards_per_att, 'rush_yards_per_game': rush_yards_per_game, 'fumbles': fumbles, 'total_points': total_points,
    'points_per_game': points_per_game, 'drives': drives, 'plays': plays, 'scoring_percentage': scoring_percentage, 'to_percentage': to_percentage,
    'plays_per_drive': plays_per_drive, 'yards_per_drive': yards_per_drive, 'points_per_drive': points_per_drive, 'third_down_att': third_down_att,
    'third_down_conv': third_down_conv, 'third_down_conv_rate': third_down_conv_rate, 'fourth_down_att': fourth_down_att, 'fourth_down_conv': fourth_down_conv,
    'fourth_down_conv_rate': fourth_down_conv_rate, 'rz_att': rz_att, 'rz_td': rz_td, 'rz_percentage': rz_percentage}
    return result
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

    return output


# TEAM DEFENSE STATS
@nfl.route('/nfl/team_defense', methods=['POST'])
def nfl_add_team_def_stats(json_dict):
    team_id = json_dict['team_id']
    year = json_dict['year']
    games = json_dict['games']
    dvoa = json_dict['dvoa']
    epa_per_play = json_dict['epa_per_play']
    success_rate = json_dict['success_rate']
    dropback_epa = json_dict['dropback_epa']
    dropback_sr = json_dict['dropback_sr']
    rush_epa = json_dict['rush_epa']
    rush_sr = json_dict['rush_sr']
    pass_comp = json_dict['pass_comp']
    pass_att = json_dict['pass_att']
    pass_comp_percentage = json_dict['pass_comp_percentage']
    pass_yards = json_dict['pass_yards']
    pass_td = json_dict['pass_td']
    pass_td_percentage = json_dict['pass_td_percentage']
    yards_per_att = json_dict['yards_per_att']
    pass_yards_per_comp = json_dict['pass_yards_per_comp']
    pass_yards_per_game = json_dict['pass_yards_per_game']
    passer_rating = json_dict['passer_rating']
    qb_hits = json_dict['qb_hits']
    sacks = json_dict['sacks']
    ints = json_dict['ints']
    int_percentage = json_dict['int_percentage']
    pass_deflections = json_dict['pass_deflections']
    rush_att = json_dict['rush_att']
    rush_yards = json_dict['rush_yards']
    rush_td = json_dict['rush_td']
    rush_yards_per_att = json_dict['rush_yards_per_att']
    rush_yards_per_game = json_dict['rush_yards_per_game']
    total_points = json_dict['total_points']
    points_per_game = json_dict['points_per_game']
    rz_att = json_dict['rz_att']
    rz_td = json_dict['rz_td']
    rz_percentage = json_dict['rz_percentage']
    drives = json_dict['drives']
    plays = json_dict['plays']
    scoring_percentage = json_dict['scoring_percentage']
    to_percentage = json_dict['to_percentage']
    plays_per_drive = json_dict['plays_per_drive']
    yards_per_drive = json_dict['yards_per_drive']
    points_per_drive = json_dict['points_per_drive']
    third_down_att = json_dict['third_down_att']
    third_down_conv = json_dict['third_down_conv']
    third_down_conv_rate = json_dict['third_down_conv_rate']
    fourth_down_att = json_dict['fourth_down_att']
    fourth_down_conv = json_dict['fourth_down_conv']
    fourth_down_conv_rate = json_dict['fourth_down_conv_rate']
    qb_rush_att = json_dict['qb_rush_att']
    qb_rush_yards = json_dict['qb_rush_yards']
    qb_rush_td = json_dict['qb_rush_td']
    rb_att = json_dict['rb_att']
    rb_yards = json_dict['rb_yards']
    rb_td = json_dict['rb_td']
    rb_targets = json_dict['rb_targets']
    rb_rec = json_dict['rb_rec']
    rb_rec_yards = json_dict['rb_rec_yards']
    rb_rec_td = json_dict['rb_rec_td']
    wr_targets = json_dict['wr_targets']
    wr_rec = json_dict['wr_rec']
    wr_yards = json_dict['wr_yards']
    wr_td = json_dict['wr_td']
    te_targets = json_dict['te_targets']
    te_rec = json_dict['te_rec']
    te_yards = json_dict['te_yards']
    te_td = json_dict['te_td']


    values = (team_id, year, games, dvoa, epa_per_play, success_rate, dropback_epa, dropback_sr, rush_epa, rush_sr, pass_comp,
    pass_att, pass_comp_percentage, pass_yards, pass_td, pass_td_percentage, yards_per_att, pass_yards_per_comp, pass_yards_per_game,
    passer_rating, qb_hits, sacks, ints, int_percentage, pass_deflections, rush_att, rush_yards, rush_td, rush_yards_per_att,
    rush_yards_per_game, points_per_game, total_points, drives, plays, scoring_percentage, to_percentage, plays_per_drive,
    yards_per_drive, points_per_drive, third_down_att, third_down_conv, third_down_conv_rate, fourth_down_att, fourth_down_conv,
    fourth_down_conv_rate, rz_att, rz_td, rz_percentage, qb_rush_att, qb_rush_yards, qb_rush_td, rb_att, rb_yards, rb_td,
    rb_targets, rb_rec, rb_rec_yards, rb_rec_td, wr_targets, wr_rec, wr_yards, wr_td, te_targets, te_rec, te_yards, te_td)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO nfl_team_defense (team_id, year, games, dvoa, epa_per_play, success_rate, dropback_epa, dropback_sr, rush_epa, rush_sr, pass_comp,
    pass_att, pass_comp_percentage, pass_yards, pass_td, pass_td_percentage, yards_per_att, pass_yards_per_comp, pass_yards_per_game,
    passer_rating, qb_hits, sacks, ints, int_percentage, pass_deflections, rush_att, rush_yards, rush_td, rush_yards_per_att,
    rush_yards_per_game, points_per_game, total_points, drives, plays, scoring_percentage, to_percentage, plays_per_drive,
    yards_per_drive, points_per_drive, third_down_att, third_down_conv, third_down_conv_rate, fourth_down_att, fourth_down_conv,
    fourth_down_conv_rate, rz_att, rz_td, rz_percentage, qb_rush_att, qb_rush_yards, qb_rush_td, rb_att, rb_yards, rb_td,
    rb_targets, rb_rec, rb_rec_yards, rb_rec_td, wr_targets, wr_rec, wr_yards, wr_td, te_targets, te_rec, te_yards, te_td) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))
    connection.commit()
    print(f"Team {year}  offensive stats has been added to nfl_team_defense table.")


    result = {'team_id': team_id, 'year': year, 'games': games, 'dvoa': dvoa, 'epa_per_play': epa_per_play,
              'success_rate': success_rate, 'dropback_epa': dropback_epa, 'dropback_sr': dropback_sr, 'rush_epa': rush_epa,
              'rush_sr': rush_sr, 'pass_comp': pass_comp, 'pass_att': pass_att, 'pass_comp_percentage': pass_comp_percentage,
              'pass_yards': pass_yards, 'pass_td': pass_td, 'pass_td_percentage': pass_td_percentage, 'pass_yards_per_comp': pass_yards_per_comp,
              'pass_yards_per_game': pass_yards_per_game, 'yards_per_att': yards_per_att, 'passer_rating': passer_rating, 'qb_hits': qb_hits, 'sacks': sacks,
              'ints': ints, 'int_percentage': int_percentage, 'pass_deflections': pass_deflections, 'rush_att': rush_att, 'rush_yards': rush_yards, 'rush_td': rush_td,
              'rush_yards_per_att': rush_yards_per_att, 'rush_yards_per_game': rush_yards_per_game, 'total_points': total_points,
              'points_per_game': points_per_game, 'rz_att_faced': rz_att, 'rz_td_allowed': rz_td,
              'rz_td_allowed_percentage': rz_percentage, 'drives': drives, 'plays': plays, 'scoring_percentage': scoring_percentage,
              'to_percentage': to_percentage, 'plays_per_drive': plays_per_drive, 'yards_per_drive': yards_per_drive, 'points_per_drive': points_per_drive,
              'third_down_att': third_down_att, 'third_down_conv': third_down_conv, 'third_down_conv_rate': third_down_conv_rate,
              'fourth_down_att': fourth_down_att, 'fourth_down_conv': fourth_down_conv, 'fourth_down_conv_rate': fourth_down_conv_rate,
              'qb_rush_yards': qb_rush_yards, 'qb_rush_td': qb_rush_td, 'rb_att': rb_att, 'rb_yards': rb_yards, 'rb_td': rb_td,
              'rb_targets': rb_targets, 'rb_rec': rb_rec, 'rb_rec_yards': rb_rec_yards, 'rb_rec_td': rb_rec_td, 'wr_targets': wr_targets,
              'wr_rec': wr_rec, 'wr_yards': wr_yards, 'wr_td': wr_td, 'te_targets': te_targets, 'te_rec': te_rec, 'te_yards': te_yards, 'te_td': te_td}
    return result
@nfl.route('/nfl/team_defense', methods=['PUT'])
def nfl_update_team_def_stats(json_dict):
    team_id = json_dict['team_id']
    year = json_dict['year']
    games = json_dict['games']
    dvoa = json_dict['dvoa']
    epa_per_play = json_dict['epa_per_play']
    success_rate = json_dict['success_rate']
    dropback_epa = json_dict['dropback_epa']
    dropback_sr = json_dict['dropback_sr']
    rush_epa = json_dict['rush_epa']
    rush_sr = json_dict['rush_sr']
    pass_comp = json_dict['pass_comp']
    pass_att = json_dict['pass_att']
    pass_comp_percentage = json_dict['pass_comp_percentage']
    pass_yards = json_dict['pass_yards']
    pass_td = json_dict['pass_td']
    pass_td_percentage = json_dict['pass_td_percentage']
    yards_per_att = json_dict['yards_per_att']
    pass_yards_per_comp = json_dict['pass_yards_per_comp']
    pass_yards_per_game = json_dict['pass_yards_per_game']
    passer_rating = json_dict['passer_rating']
    qb_hits = json_dict['qb_hits']
    sacks = json_dict['sacks']
    ints = json_dict['ints']
    int_percentage = json_dict['int_percentage']
    pass_deflections = json_dict['pass_deflections']
    rush_att = json_dict['rush_att']
    rush_yards = json_dict['rush_yards']
    rush_td = json_dict['rush_td']
    rush_yards_per_att = json_dict['rush_yards_per_att']
    rush_yards_per_game = json_dict['rush_yards_per_game']
    total_points = json_dict['total_points']
    points_per_game = json_dict['points_per_game']
    rz_att = json_dict['rz_att']
    rz_td = json_dict['rz_td']
    rz_percentage = json_dict['rz_percentage']
    drives = json_dict['drives']
    plays = json_dict['plays']
    scoring_percentage = json_dict['scoring_percentage']
    to_percentage = json_dict['to_percentage']
    plays_per_drive = json_dict['plays_per_drive']
    yards_per_drive = json_dict['yards_per_drive']
    points_per_drive = json_dict['points_per_drive']
    third_down_att = json_dict['third_down_att']
    third_down_conv = json_dict['third_down_conv']
    third_down_conv_rate = json_dict['third_down_conv_rate']
    fourth_down_att = json_dict['fourth_down_att']
    fourth_down_conv = json_dict['fourth_down_conv']
    fourth_down_conv_rate = json_dict['fourth_down_conv_rate']
    qb_rush_att = json_dict['qb_rush_att']
    qb_rush_yards = json_dict['qb_rush_yards']
    qb_rush_td = json_dict['qb_rush_td']
    rb_att = json_dict['rb_att']
    rb_yards = json_dict['rb_yards']
    rb_td = json_dict['rb_td']
    rb_targets = json_dict['rb_targets']
    rb_rec = json_dict['rb_rec']
    rb_rec_yards = json_dict['rb_rec_yards']
    rb_rec_td = json_dict['rb_rec_td']
    wr_targets = json_dict['wr_targets']
    wr_rec = json_dict['wr_rec']
    wr_yards = json_dict['wr_yards']
    wr_td = json_dict['wr_td']
    te_targets = json_dict['te_targets']
    te_rec = json_dict['te_rec']
    te_yards = json_dict['te_yards']
    te_td = json_dict['te_td']

    values = (games, dvoa, epa_per_play, success_rate, dropback_epa, dropback_sr, rush_epa, rush_sr, pass_comp,
    pass_att, pass_comp_percentage, pass_yards, pass_td, pass_td_percentage, yards_per_att, pass_yards_per_comp, pass_yards_per_game,
    passer_rating, qb_hits, sacks, ints, int_percentage, pass_deflections, rush_att, rush_yards, rush_td, rush_yards_per_att,
    rush_yards_per_game, points_per_game, total_points, drives, plays, scoring_percentage, to_percentage, plays_per_drive,
    yards_per_drive, points_per_drive, third_down_att, third_down_conv, third_down_conv_rate, fourth_down_att, fourth_down_conv,
    fourth_down_conv_rate, rz_att, rz_td, rz_percentage, qb_rush_att, qb_rush_yards, qb_rush_td, rb_att, rb_yards, rb_td,
    rb_targets, rb_rec, rb_rec_yards, rb_rec_td, wr_targets, wr_rec, wr_yards, wr_td, te_targets, te_rec, te_yards, te_td,team_id, year)

    connection = create_connection()
    cursor = connection.cursor()

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
                    WHERE nfl_team_defense.team_id = %s AND nfl_team_defense.year = %s""",
                (values))

    connection.commit()
    print(f"Team {year}  offensive stats has been added to fb_team_off table.")

    result = {'team_id': team_id, 'year': year, 'games': games,'def_dvoa': dvoa, 'def_epa': epa_per_play, 'def_dropback_epa': dropback_epa,
    'def_dropback_sr': dropback_sr, 'def_rush_epa': rush_epa, 'def_rush_sr': rush_sr, 'pass_att_faced': pass_att, 'pass_comp_allowed': pass_comp,
    'pass_yards_allowed': pass_yards, 'pass_td_allowed': pass_td, 'yards_per_att': yards_per_att, 'pass_yards_per_comp': pass_yards_per_comp,
    'pass_yards_per_game': pass_yards_per_game, 'passer_rating': passer_rating, 'qb_hits': qb_hits, 'sacks': sacks, 'ints': ints,
    'int_percentage': int_percentage, 'pass_deflections': pass_deflections, 'rush_att': rush_att, 'rush_yards': rush_yards, 'rush_td': rush_td,
    'rush_yards_per_att': rush_yards_per_att, 'rush_yards_per_game': rush_yards_per_game, 'total_points': total_points, 'points_per_game': points_per_game,
    'rz_att': rz_att, 'rz_td': rz_td, 'rz_percentage': rz_percentage, 'drives': drives, 'plays': plays, 'scoring_percentage': scoring_percentage,
    'to_percentage': to_percentage, 'plays_per_drive': plays_per_drive, 'yards_per_drive': yards_per_drive, 'points_per_drive': points_per_drive,
    'third_down_att': third_down_att, 'third_down_conv': third_down_conv, 'third_down_conv_rate': third_down_conv_rate, 'fourth_down_att': fourth_down_att,
    'fourth_down_conv': fourth_down_conv, 'fourth_down_conv_rate': fourth_down_conv_rate, 'qb_rush_att': qb_rush_att, 'qb_rush_yards': qb_rush_yards,
    'qb_rush_td': qb_rush_td, 'rb_att': rb_att, 'rb_yards': rb_yards, 'rb_td': rb_td, 'rb_targets': rb_targets, 'rb_rec': rb_rec, 'rb_rec_yards': rb_rec_yards,
    'rb_rec_td': rb_rec_td, 'wr_targets': wr_targets, 'wr_rec': wr_rec, 'wr_yards': wr_yards, 'wr_td': wr_td,'te_targets': te_targets, 'te_rec': te_rec,
    'te_yards': te_yards, 'te_td': te_td}

    # print(len(result))
    return result
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


# # GET NFL TEAM DEFENSE STAT RANK
# nfl.route('nfl/stat_rank', method=['GET'])
# def nfl_stat_rank():
#     team_id = request.args.get('id', None)
#     connection = create_connection()
#     cursor = connection.cursor()
#     print(f"player_id = {team_id}")
