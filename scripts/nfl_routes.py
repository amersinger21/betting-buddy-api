from .db import create_connection
from flask import Blueprint, request

nfl = Blueprint("nfl", __name__)

@nfl.route('/nfl/player_stats', methods=['POST'])
def nfl_add_player_stats(json_dict):
    player_id = json_dict['player_id']
    game_id = json_dict['game_id']
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


    values = (player_id, game_id, team_id, opp_id, pass_att, pass_comp, pass_yards, pass_td, pass_longest, ints,
              sacks, rush_att, rush_yards, rush_td, rush_longest, targets, rec, rec_yards, rec_td, rec_longest, fumbles)

    connection = create_connection()
    cursor=connection.cursor()

    cursor.execute("""INSERT INTO fb_player_stats (player_id, game_id, team_id, opp_id, pass_att, pass_comp, pass_yards, pass_td, pass_longest, 
                    ints, sacks, rush_att, rush_yards, rush_td, rush_longest, targets, rec, rec_yards, rec_td, rec_longest, fumbles) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))

    connection.commit()
    print(f"Game has been added to games tabel.")


    result = {'player_id': player_id, 'game_id': game_id, 'team_id': team_id, 'opp_id': opp_id, 'pass_att': pass_att,
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

    column = 'fb_player_stats.' + column_name
    print(f"column = {column}")

    if operator == 'over':
        op_val = '>'
    else:
        op_val = '<'

    query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name,
                    player.position, fb_player_stats.*
                    FROM
                    fb_player_stats
                    JOIN
                    player ON player.id = fb_player_stats.player_id
                    WHERE player.id = %s AND {column} {op_val} %s'''
    vals = [player_id, value]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())

    output = []
    for result in results:
        item = {'name': '', 'pos': '', 'id': 0, 'player_id': 0, 'game_id': 0, 'team_id': 0, 'opp_id': 0, 'pass_att': 0, 'pass_comp': 0, 'pass_yards': 0,
                'pass_td': 0, 'pass_longest': 0, 'ints': 0, 'sacks': 0, 'rush_att': 0, 'rush_yards': 0, 'rush_td': 0,
                'rush_longest': 0, 'targets': 0, 'rec': 0, 'rec_yards': 0, 'rec_td': 0, 'rec_longest': 0, 'fumbles': 0}
        item['name'] = result[0]
        item['pos'] = result[1]
        item['id'] = result[2]
        item['player_id'] = result[3]
        item['game_id'] = result[4]
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


# GAME INFO ROUTES
@nfl.route('/nfl/games', methods=['POST'])
def nfl_add_game(json_dict):
    home_team = json_dict['home_team_id']
    away_team = json_dict['away_team_id']
    home_score = json_dict['home_score']
    away_score = json_dict['away_score']
    week = json_dict['week']
    year = json_dict['year']
    weather_id = json_dict['weather_id']
    vegas_line = json_dict['vegas_line']
    vegas_line_results = json_dict['vegas_line_result']
    margin_of_victory = json_dict['margin_of_victory']
    over_under = json_dict['over_under']
    over_under_results = json_dict['over_under_result']

    values = (home_team, away_team, home_score, away_score, week, year, weather_id, vegas_line, vegas_line_results, margin_of_victory, over_under,
              over_under_results)


    connection = create_connection()
    cursor=connection.cursor()

    cursor.execute("INSERT INTO games (home_team_id, away_team_id, home_score, away_score, week, year, weather_id, vegas_line, vegas_line_result, margin_of_victory, over_under, over_under_result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (values))
    connection.commit()
    print(f"Game has been added to games tabel.")


    result = {'home_team': home_team, 'away_team': away_team, 'home_score': home_score, 'away_score': away_score, 'week': week,
              'year': year, 'weather_id': weather_id, 'vegas_line': vegas_line, 'vegas_line_result': vegas_line_results, 'margin_of_victory': margin_of_victory,
              'over_under': over_under, 'over_under_result': over_under_results}

    return result
@nfl.route('/nfl/games', methods=['GET'])
def nfl_get_games():
    id = request.args.get('id', None)
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM games
                    WHERE home_team_id = %s OR away_team_id = %s ''',
                   [id, id])
    results = list(cursor.fetchall())
    result_list = []
    for result in results:
        player_dict = {'id': result[0], 'home_team_id': result[1], 'away_team_id': result[2],
                       'home_score': result[3], 'away_score': result[4], 'week': result[5], 'year': result[6], 'weather': result[7],
                       'vegas_line': result[8], 'vegas_line_result': result[9], 'margin_of_victory': result[10], 'over_under': result[11],
                       'over_under_result': result[12]}
        result_list.append(player_dict)
    return result_list




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


# RED ZONE STATS:
@nfl.route('/nfl/rz_stat', methods=['POST'])
def nfl_add_rz_stat(json_dict):
    player_id = json_dict['player_id']
    year = json_dict['year']
    rz_20_pass_att = json_dict['rz_20_pass_att']
    rz_20_pass_yard = json_dict['rz_20_pass_yards']
    rz_20_pass_td = json_dict['rz_20_pass_td']
    rz_20_pass_int = json_dict['rz_20_pass_int']
    rz_20_pass_comp_percentage = json_dict['rz_20_comp_percentage']
    rz_10_pass_att = json_dict['rz_10_pass_att']
    rz_10_pass_yard = json_dict['rz_10_pass_yards']
    rz_10_pass_td = json_dict['rz_10_pass_td']
    rz_10_pass_int = json_dict['rz_10_pass_int']
    rz_10_comp_percentage = json_dict['rz_10_comp_percentage']
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

    values = (player_id, year, rz_20_pass_att, rz_20_pass_yard, rz_20_pass_td, rz_20_pass_int, rz_20_pass_comp_percentage,
              rz_10_pass_att, rz_10_pass_yard, rz_10_pass_td, rz_10_pass_int, rz_10_comp_percentage, rz_20_targets, rz_20_receptions,
              rz_20_rec_yards, rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions,
              rz_10_rec_yards, rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_td,
              rz_20_rush_yards, rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_td, rz_10_rush_yards, rz_10_rush_percentage,
              rz_5_rush_att, rz_5_rush_td, rz_5_rush_yards, rz_5_rush_percentage)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO fb_red_zone (player_id, year, rz_20_pass_att, rz_20_pass_yards, rz_20_pass_td, rz_20_pass_int, rz_20_comp_percentage,
              rz_10_pass_att, rz_10_pass_yards, rz_10_pass_td, rz_10_pass_int, rz_10_comp_percentage, rz_20_targets, rz_20_receptions,
              rz_20_rec_yards, rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions,
              rz_10_rec_yards, rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_td,
              rz_20_rush_yards, rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_td, rz_10_rush_yards, rz_10_rush_percentage,
              rz_5_rush_att, rz_5_rush_td, rz_5_rush_yards, rz_5_rush_percentage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))
    connection.commit()
    print(f"Game has been added to games table.")


    result = {'player_id':player_id, 'year': year, 'rz_20_pass_att': rz_20_pass_att, 'rz_20_pass_yard': rz_20_pass_yard,
              'rz_20_pass_td': rz_20_pass_td, 'rz_20_pass_int': rz_20_pass_int, 'rz_20_pass_comp_percentage': rz_20_pass_comp_percentage,
              'rz_10_pass_att': rz_10_pass_att, 'rz_10_pass_yard': rz_10_pass_yard, 'rz_10_pass_td': rz_10_pass_td, 'rz_10_pass_int': rz_10_pass_int,
              'rz_10_comp_percentage': rz_10_comp_percentage, 'rz_20_targets': rz_10_comp_percentage, 'rz_20_receptions': rz_20_receptions,
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
    prior_yr = int(year) - 2
    connection = create_connection()
    cursor = connection.cursor()

    query = f'''SELECT player.first_name, player.last_name, fb_red_zone.*
                FROM fb_red_zone
                JOIN player ON player.id = fb_red_zone.player_id
                WHERE fb_red_zone.player_id = %s AND fb_red_zone.year > %s'''

    vals = [player_id, prior_yr]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())

    output = []
    # return results
    for result in results:
        item = {'name': result[0] + ' ' + result[1], 'player_id': result[3], 'year': result[4], 'rz_20_pass_att': result[5], 'rz_20_pass_yards': result[6],
                'rz_20_pass_td': result[7], 'rz_20_pass_int': result[8], 'rz_20_comp_percentage': result[9], 'rz_10_pass_att': result[10],
                'rz_10_pass_yards': result[11],  'rz_10_pass_td': result[12], 'rz_10_pass_int': result[13], 'rz_10_comp_percentage': result[14],
                'rz_20_targets': result[15], 'rz_20_receptions': result[16], 'rz_20_rec_yards': result[17], 'rz_20_catch_percentage': result[18],
                'rz_20_rec_td': result[19], 'rz_20_target_percentage': result[20], 'rz_10_targets': result[21], 'rz_10_receptions': result[22],
                'rz_10_rec_yards': result[23], 'rz_10_catch_percentage': result[24], 'rz_10_rec_td': result[25], 'rz_10_target_percentage': result[26],
                'rz_20_rush_att': result[27], 'rz_20_rush_yards': result[28], 'rz_20_rush_td': result[29], 'rz_20_rush_percentage': result[30],
                'rz_10_rush_att': result[31], 'rz_10_rush_yards': result[32], 'rz_10_rush_td': result[33], 'rz_10_rush_percentage': result[34],
                'rz_5_rush_att': result[35], 'rz_5_rush_yards': result[36], 'rz_5_rush_td': result[37], 'rz_5_rush_percentage': result[38]}
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
    off_dvoa = json_dict['off_dvoa']
    off_epa = json_dict['off_epa']
    dropback_epa = json_dict['dropback_epa']
    dropback_sr = json_dict['dropback_sr']
    rush_epa = json_dict['rush_epa']
    rush_sr = json_dict['rush_sr']
    pass_att = json_dict['pass_att']
    pass_comp = json_dict['pass_comp']
    pass_yards = json_dict['pass_yards']
    pass_td = json_dict['pass_td']
    int_thrown = json_dict['int_thrown']
    pass_yards_att = json_dict['pass_yards_att']
    pass_yards_per_game = json_dict['pass_yards_per_game']
    sacks_taken = json_dict['sacks_taken']
    rush_att = json_dict['rush_att']
    rush_yards = json_dict['rush_yards']
    rush_td = json_dict['rush_td']
    rush_yards_per_att = json_dict['rush_yards_per_att']
    rush_yards_per_game = json_dict['rush_yards_per_game']
    fumbles_lost = json_dict['fumbles_lost']
    points_scored = json_dict['points_scored']
    points_scored_per_game = json_dict['points_scored_per_game']
    off_rz_plays = json_dict['off_rz_plays']
    off_rz_td = json_dict['off_rz_td']
    total_drives = json_dict['total_drives']
    total_plays = json_dict['total_plays']
    scoring_percentage = json_dict['scoring_percentage']
    to_percentage = json_dict['to_percentage']
    avg_drive_play = json_dict['avg_drive_play']
    avg_drive_points = json_dict['avg_drive_points']
    avg_drive_yards = json_dict['avg_drive_yards']


    values = (team_id, year, games, off_dvoa, off_epa, dropback_epa, dropback_sr, rush_epa, rush_sr, pass_att, pass_comp, pass_yards,
              pass_td, int_thrown, pass_yards_att, pass_yards_per_game, sacks_taken, rush_att, rush_yards, rush_td, rush_yards_per_att,
              rush_yards_per_game, fumbles_lost, points_scored, points_scored_per_game, off_rz_plays, off_rz_td, total_drives, total_plays,
              scoring_percentage, to_percentage, avg_drive_play, avg_drive_points, avg_drive_yards)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO fb_off_stats (team_id, year, games, off_dvoa, off_epa, dropback_epa, dropback_sr, rush_epa, rush_sr, pass_att, pass_comp, pass_yards,
              pass_td, int_thrown, pass_yards_att, pass_yards_per_game, sacks_taken, rush_att, rush_yards, rush_td, rush_yards_per_att,
              rush_yards_per_game, fumbles_lost, points_scored, points_scored_per_game, off_rz_plays, off_rz_td, total_drives, total_plays,
              scoring_percentage, to_percentage, avg_drive_play, avg_drive_points, avg_drive_yards) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))
    connection.commit()
    print(f"Team {year}  offensive stats has been added to fb_team_off table.")


    result = {'team_id': team_id, 'year': year, 'games': games, 'off_dvoa': off_dvoa, 'off_epa': off_epa, 'dropback_epa': dropback_epa,
              'dropback_sr': dropback_sr, 'rush_epa': rush_epa, 'rush_sr': rush_sr, 'pass_att': pass_att, 'pass_comp': pass_comp,
              'pass_yards': pass_yards, 'pass_td': pass_td, 'int_thrown': int_thrown, 'pass_yards_att': pass_yards_att, 'pass_yards_per_game': pass_yards_per_game,
              'sacks_taken': sacks_taken, 'rush_att': rush_att, 'rush_yards': rush_yards, 'rush_td': rush_td, 'rush_yards_per_att': rush_yards_per_att,
              'rush_yards_per_game': rush_yards_per_game, 'fumbles_lost': fumbles_lost, 'points_scored': points_scored, 'points_scored_per_game': points_scored_per_game,
              'off_rz_plays': off_rz_plays, 'off_rz_td': off_rz_td, 'total_drives': total_drives, 'total_plays': total_plays,
              'scoring_percentage': scoring_percentage, 'to_percentage': to_percentage, 'avg_drive_play':avg_drive_play,
              'avg_drive_points': avg_drive_points, 'avg_drive_yards': avg_drive_yards}
    return result
@nfl.route('/nfl/team_offense', methods=['PUT'])
def nfl_update_team_off_stats(json_dict):
    team_id = json_dict['team_id']
    year = json_dict['year']
    games = json_dict['games']
    off_dvoa = json_dict['off_dvoa']
    off_epa = json_dict['off_epa']
    dropback_epa = json_dict['dropback_epa']
    dropback_sr = json_dict['dropback_sr']
    rush_epa = json_dict['rush_epa']
    rush_sr = json_dict['rush_sr']
    pass_att = json_dict['pass_att']
    pass_comp = json_dict['pass_comp']
    pass_yards = json_dict['pass_yards']
    pass_td = json_dict['pass_td']
    int_thrown = json_dict['int_thrown']
    pass_yards_att = json_dict['pass_yards_att']
    pass_yards_per_game = json_dict['pass_yards_per_game']
    sacks_taken = json_dict['sacks_taken']
    rush_att = json_dict['rush_att']
    rush_yards = json_dict['rush_yards']
    rush_td = json_dict['rush_td']
    rush_yards_per_att = json_dict['rush_yards_per_att']
    rush_yards_per_game = json_dict['rush_yards_per_game']
    fumbles_lost = json_dict['fumbles_lost']
    points_scored = json_dict['points_scored']
    points_scored_per_game = json_dict['points_scored_per_game']
    off_rz_plays = json_dict['off_rz_plays']
    off_rz_td = json_dict['off_rz_td']
    total_drives = json_dict['total_drives']
    total_plays = json_dict['total_plays']
    scoring_percentage = json_dict['scoring_percentage']
    to_percentage = json_dict['to_percentage']
    avg_drive_play = json_dict['avg_drive_play']
    avg_drive_points = json_dict['avg_drive_points']
    avg_drive_yards = json_dict['avg_drive_yards']


    values = (games, off_dvoa, off_epa, dropback_epa, dropback_sr, rush_epa, rush_sr, pass_att, pass_comp, pass_yards,
              pass_td, int_thrown, pass_yards_att, pass_yards_per_game, sacks_taken, rush_att, rush_yards, rush_td, rush_yards_per_att,
              rush_yards_per_game, fumbles_lost, points_scored, points_scored_per_game, off_rz_plays, off_rz_td, total_drives, total_plays,
              scoring_percentage, to_percentage, avg_drive_play, avg_drive_points, avg_drive_yards, team_id, year)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""UPDATE fb_off_stats
                    SET games = %s, off_dvoa = %s, off_epa = %s, dropback_epa = %s, dropback_sr = %s, rush_epa = %s, rush_sr = %s,
                     pass_att = %s, pass_comp = %s, pass_yards = %s, pass_td = %s, int_thrown = %s, pass_yards_att = %s, 
                     pass_yards_per_game = %s, sacks_taken = %s, rush_att = %s, rush_yards = %s, rush_td = %s, rush_yards_per_att = %s, 
                     rush_yards_per_game = %s, fumbles_lost = %s, points_scored = %s, points_scored_per_game = %s,
                     off_rz_plays = %s, off_rz_td = %s, total_drives = %s, total_plays = %s, scoring_percentage = %s, to_percentage = %s, 
                     avg_drive_play = %s, avg_drive_points = %s, avg_drive_yards = %s
                     WHERE fb_off_stats.team_id = %s AND fb_off_stats.year = %s""",
                   (values))
    connection.commit()
    print(f"Team {year}  offensive stats has been added to fb_team_off table.")


    result = {'team_id': team_id, 'year': year, 'games': games, 'off_dvoa': off_dvoa, 'off_epa': off_epa, 'dropback_epa': dropback_epa,
              'dropback_sr': dropback_sr, 'rush_epa': rush_epa, 'rush_sr': rush_sr, 'pass_att': pass_att, 'pass_comp': pass_comp,
              'pass_yards': pass_yards, 'pass_td': pass_td, 'int_thrown': int_thrown, 'pass_yards_att': pass_yards_att, 'pass_yards_per_game': pass_yards_per_game,
              'sacks_taken': sacks_taken, 'rush_att': rush_att, 'rush_yards': rush_yards, 'rush_td': rush_td, 'rush_yards_per_att': rush_yards_per_att,
              'rush_yards_per_game': rush_yards_per_game, 'fumbles_lost': fumbles_lost, 'points_scored': points_scored, 'points_scored_per_game': points_scored_per_game,
              'off_rz_plays': off_rz_plays, 'off_rz_td': off_rz_td, 'total_drives': total_drives, 'total_plays': total_plays,
              'scoring_percentage': scoring_percentage, 'to_percentage': to_percentage, 'avg_drive_play':avg_drive_play,
              'avg_drive_points': avg_drive_points, 'avg_drive_yards': avg_drive_yards}
    return result
@nfl.route('/nfl/team_offense', methods=['GET'])
def nfl_get_off_stats():
    team_id = request.args.get('id', None)
    year = request.args.get('year', None)
    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name,  fb_off_stats.*
                FROM fb_off_stats
                JOIN team ON team.id = fb_off_stats.team_id 
                WHERE team.id = %s AND fb_off_stats.year = %s'''
    vals = [team_id, year]
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
                'to_percentage': result[32], 'avg_drive_play': result[33], 'avg_drive_points': result[34], 'avg_drive_yards': result[35]}
        if item not in output:
            output.append(item)

    return output


# TEAM DEFENSE STATS
@nfl.route('/nfl/team_defense', methods=['POST'])
def nfl_add_team_def_stats(json_dict):
    team_id = json_dict['team_id']
    year = json_dict['year']
    games = json_dict['games']
    def_dvoa = json_dict['def_dvoa']
    def_epa = json_dict['def_epa']
    def_dropback_epa = json_dict['def_dropback_epa']
    def_dropback_sr = json_dict['def_dropback_sr']
    def_rush_epa = json_dict['def_rush_epa']
    def_rush_sr = json_dict['def_rush_sr']
    pass_att_faced = json_dict['pass_att_faced']
    pass_comp_allowed = json_dict['pass_comp_allowed']
    pass_yards_allowed = json_dict['pass_yards_allowed']
    pass_td_allowed = json_dict['pass_td_allowed']
    allowed_pyards_per_att = json_dict['allowed_pyards_per_att']
    allowed_pyards_per_game = json_dict['allowed_pyards_per_game']
    qb_hits = json_dict['qb_hits']
    qb_sacks = json_dict['qb_sacks']
    ints = json_dict['ints']
    rush_att_faced = json_dict['rush_att_faced']
    rush_yards_allowed = json_dict['rush_yards_allowed']
    rush_td_allowed = json_dict['rush_td_allowed']
    allowed_ryards_per_att = json_dict['allowed_ryards_per_att']
    allowed_ryards_per_game = json_dict['allowed_ryards_per_game']
    rec_allowed = json_dict['rec_allowed']
    rec_td_allowed = json_dict['rec_td_allowed']
    points_allowed = json_dict['points_allowed']
    points_per_game_allowed = json_dict['points_per_game_allowed']
    rz_att_faced = json_dict['rz_att_faced']
    rz_td_allowed = json_dict['rz_td_allowed']
    rz_td_allowed_percentage = json_dict['rz_td_allowed_percentage']
    drives_faced = json_dict['drives_faced']
    plays_faced = json_dict['plays_faced']
    score_against_percentage = json_dict['score_against_percentage']
    def_to_percentage = json_dict['def_to_percentage']
    plays_faced_per_drive = json_dict['plays_faced_per_drive']
    yards_allowed_per_drive = json_dict['yards_allowed_per_drive']
    points_allowed_per_drive = json_dict['points_allowed_per_drive']
    TE_targets = json_dict['TE_targets']
    TE_rec = json_dict['TE_rec']
    TE_yards = json_dict['TE_yards']
    TE_td = json_dict['TE_td']
    WR_targets = json_dict['WR_targets']
    WR_rec = json_dict['WR_rec']
    WR_yards = json_dict['WR_yards']
    WR_td = json_dict['WR_td']
    RB_targets = json_dict['RB_targets']
    RB_rec = json_dict['RB_rec']
    RB_rec_yards = json_dict['RB_rec_yards']
    RB_rec_td = json_dict['RB_rec_td']
    RB_att = json_dict['RB_att']
    RB_rush_yards = json_dict['RB_rush_yards']
    RB_rush_td = json_dict['RB_rush_td']
    QB_completions = json_dict['QB_completions']
    QB_att = json_dict['QB_att']
    QB_yards = json_dict['QB_yards']
    QB_rush_att = json_dict['QB_rush_att']
    QB_rush_yards = json_dict['QB_rush_yards']
    QB_rush_td = json_dict['QB_rush_td']

    values = (team_id, year, games, def_dvoa, def_epa, def_dropback_epa, def_dropback_sr, def_rush_epa, def_rush_sr, pass_att_faced,
              pass_comp_allowed, pass_yards_allowed, pass_td_allowed, allowed_pyards_per_att, allowed_pyards_per_game, qb_hits,
              qb_sacks, ints, rush_att_faced, rush_yards_allowed, rush_td_allowed, allowed_ryards_per_att, allowed_ryards_per_game,
              rec_allowed, rec_td_allowed, points_allowed, points_per_game_allowed, rz_att_faced, rz_td_allowed, rz_td_allowed_percentage,
              drives_faced, plays_faced, score_against_percentage, def_to_percentage, plays_faced_per_drive, yards_allowed_per_drive,
              points_allowed_per_drive, TE_targets, TE_rec, TE_yards, TE_td, WR_targets, WR_rec, WR_yards, WR_td, RB_targets,
              RB_rec, RB_rec_yards, RB_rec_td, RB_att, RB_rush_yards, RB_rush_td, QB_completions, QB_att, QB_yards, QB_rush_att, QB_rush_yards, QB_rush_td)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO fb_off_stats (team_id, year, games, def_dvoa, def_epa, def_dropback_epa, def_dropback_sr, def_rush_epa, 
    def_rush_sr, pass_att_faced, pass_comp_allowed, pass_yards_allowed, pass_td_allowed, allowed_pyards_per_att, allowed_pyards_per_game, qb_hits, 
    qb_sacks, ints, rush_att_faced, rush_yards_allowed, rush_td_allowed, allowed_ryards_per_att, allowed_ryards_per_game, rec_allowed, rec_td_allowed, 
    points_allowed, points_per_game_allowed, rz_att_faced, rz_td_allowed, rz_td_allowed_percentage, drives_faced, plays_faced, score_against_percentage,
    def_to_percentage, plays_faced_per_drive, yards_allowed_per_drive, points_allowed_per_drive, TE_targets, TE_rec, TE_yards, TE_td,
    WR_targets, WR_rec, WR_yards, WR_td, RB_targets, RB_rec, RB_rec_yards, RB_rec_td, RB_att, RB_rush_yards, RB_rush_td, QB_completions, 
    QB_att, QB_yards, QB_rush_att, QB_rush_yards, QB_rush_td) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""",
                   (values))
    connection.commit()
    print(f"Team {year}  offensive stats has been added to fb_team_off table.")


    result = {'team_id': team_id, 'year': year, 'games': games, 'def_dvoa': def_dvoa, 'def_epa': def_epa, 'def_dropback_epa': def_dropback_epa,
        'def_dropback_sr': def_dropback_sr, 'def_rush_epa': def_rush_epa, 'def_rush_sr': def_rush_sr, 'pass_att_faced': pass_att_faced,
        'pass_comp_allowed': pass_comp_allowed, 'pass_yards_allowed': pass_yards_allowed, 'pass_td_allowed': pass_td_allowed,
        'allowed_pyards_per_att': allowed_pyards_per_att, 'allowed_pyards_per_game': allowed_pyards_per_game, 'qb_hits': qb_hits,
        'qb_sacks': qb_sacks, 'ints': ints, 'rush_att_faced': rush_att_faced, 'rush_yards_allowed': rush_yards_allowed,
        'rush_td_allowed': rush_td_allowed, 'allowed_ryards_per_att': allowed_ryards_per_att, 'allowed_ryards_per_game': allowed_ryards_per_game,
        'rec_allowed': rec_allowed, 'rec_td_allowed': rec_td_allowed, 'def_to_percentage': def_to_percentage, 'plays_faced_per_drive': plays_faced_per_drive,
        'yards_allowed_per_drive': yards_allowed_per_drive, 'points_allowed_per_drive': plays_faced_per_drive, 'TE_targets': TE_targets,
        'TE_rec': TE_rec, 'TE_yards': TE_yards, 'TE_td': TE_td, 'WR_targets': WR_targets, 'WR_rec': WR_rec, 'WR_yards': WR_yards,
        'WR_td': WR_td, 'RB_targets': RB_targets, 'RB_rec': RB_rec, 'RB_rec_yards': RB_rec_yards, 'RB_rec_td': RB_rec_yards,
        'RB_att': RB_att, 'RB_rush_yards': RB_rush_yards, 'RB_rush_td': RB_rush_td, 'QB_completions': QB_completions,
        'QB_att': QB_att, 'QB_yards': QB_yards, 'QB_rush_att': QB_rush_att, 'QB_rush_yards': QB_rush_yards, 'QB_rush_td': QB_rush_td}
    return result
@nfl.route('/nfl/team_defense', methods=['PUT'])
def nfl_update_team_def_stats(json_dict):
    team_id = json_dict['team_id']
    year = json_dict['year']
    games = json_dict['games']
    def_dvoa = json_dict['def_dvoa']
    def_epa = json_dict['def_epa']
    def_dropback_epa = json_dict['def_dropback_epa']
    def_dropback_sr = json_dict['def_dropback_sr']
    def_rush_epa = json_dict['def_rush_epa']
    def_rush_sr = json_dict['def_rush_sr']
    pass_att_faced = json_dict['pass_att_faced']
    pass_comp_allowed = json_dict['pass_comp_allowed']
    pass_yards_allowed = json_dict['pass_yards_allowed']
    pass_td_allowed = json_dict['pass_td_allowed']
    allowed_pyards_per_att = json_dict['allowed_pyards_per_att']
    allowed_pyards_per_game = json_dict['allowed_pyards_per_game']
    qb_hits = json_dict['qb_hits']
    qb_sacks = json_dict['qb_sacks']
    ints = json_dict['ints']
    rush_att_faced = json_dict['rush_att_faced']
    rush_yards_allowed = json_dict['rush_yards_allowed']
    rush_td_allowed = json_dict['rush_td_allowed']
    allowed_ryards_per_att = json_dict['allowed_ryards_per_att']
    allowed_ryards_per_game = json_dict['allowed_ryards_per_game']
    rec_allowed = json_dict['rec_allowed']
    rec_td_allowed = json_dict['rec_td_allowed']
    points_allowed = json_dict['points_allowed']
    points_per_game_allowed = json_dict['points_per_game_allowed']
    rz_att_faced = json_dict['rz_att_faced']
    rz_td_allowed = json_dict['rz_td_allowed']
    rz_td_allowed_percentage = json_dict['rz_td_allowed_percentage']
    drives_faced = json_dict['drives_faced']
    plays_faced = json_dict['plays_faced']
    score_against_percentage = json_dict['score_against_percentage']
    def_to_percentage = json_dict['def_to_percentage']
    plays_faced_per_drive = json_dict['plays_faced_per_drive']
    yards_allowed_per_drive = json_dict['yards_allowed_per_drive']
    points_allowed_per_drive = json_dict['points_allowed_per_drive']
    TE_targets = json_dict['TE_targets']
    TE_rec = json_dict['TE_rec']
    TE_yards = json_dict['TE_yards']
    TE_td = json_dict['TE_td']
    WR_targets = json_dict['WR_targets']
    WR_rec = json_dict['WR_rec']
    WR_yards = json_dict['WR_yards']
    WR_td = json_dict['WR_td']
    RB_targets = json_dict['RB_targets']
    RB_rec = json_dict['RB_rec']
    RB_rec_yards = json_dict['RB_rec_yards']
    RB_rec_td = json_dict['RB_rec_td']
    RB_att = json_dict['RB_att']
    RB_rush_yards = json_dict['RB_rush_yards']
    RB_rush_td = json_dict['RB_rush_td']
    QB_completions = json_dict['QB_completions']
    QB_att = json_dict['QB_att']
    QB_yards = json_dict['QB_yards']
    QB_rush_att = json_dict['QB_rush_att']
    QB_rush_yards = json_dict['QB_rush_yards']
    QB_rush_td = json_dict['QB_rush_td']

    values = (games, def_dvoa, def_epa, def_dropback_epa, def_dropback_sr, def_rush_epa, def_rush_sr,
              pass_att_faced, pass_comp_allowed, pass_yards_allowed, pass_td_allowed, allowed_pyards_per_att, allowed_pyards_per_game,
              qb_hits, qb_sacks, ints, rush_att_faced, rush_yards_allowed, rush_td_allowed, allowed_ryards_per_att,
              allowed_ryards_per_game, rec_allowed, rec_td_allowed, points_allowed, points_per_game_allowed, rz_att_faced, rz_td_allowed,
              rz_td_allowed_percentage, drives_faced, plays_faced, score_against_percentage, def_to_percentage, plays_faced_per_drive,
              yards_allowed_per_drive, points_allowed_per_drive, TE_targets, TE_rec, TE_yards, TE_td, WR_targets, WR_rec, WR_yards, WR_td,
              RB_targets,  RB_rec, RB_rec_yards, RB_rec_td, RB_att, RB_rush_yards, RB_rush_td, QB_completions, QB_att, QB_yards,
              QB_rush_att, QB_rush_yards, QB_rush_td, team_id, year, )
    # print(len(values)) # count == 58

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""UPDATE fb_def_stats
                SET games = %s, def_dvoa = %s, def_epa = %s, def_dropback_epa = %s, def_dropback_sr = %s, def_rush_epa = %s,
    def_rush_sr = %s, pass_att_faced = %s, pass_comp_allowed = %s, pass_yards_allowed = %s, pass_td_allowed = %s, allowed_pyards_per_att = %s,
    allowed_pyards_per_game = %s, qb_hits = %s, qb_sacks = %s, ints = %s, rush_att_faced = %s, rush_yards_allowed = %s,
    rush_td_allowed = %s, allowed_ryards_per_att = %s, allowed_ryards_per_game = %s, rec_allowed = %s, rec_td_allowed = %s,
    points_allowed = %s, points_per_game_allowed = %s, rz_att_faced = %s, rz_td_allowed = %s, rz_td_allowed_percentage = %s,
    drives_faced = %s, plays_faced = %s, score_against_percentage = %s, def_to_percentage = %s, plays_faced_per_drive = %s,
    yards_allowed_per_drive = %s, points_allowed_per_drive = %s, TE_targets = %s, TE_rec = %s, TE_yards = %s, TE_td = %s,
    WR_targets = %s, WR_rec = %s, WR_yards = %s, WR_td = %s, RB_targets = %s, RB_rec = %s, RB_rec_yards = %s, RB_rec_td = %s,
    RB_att = %s, RB_rush_yards = %s, RB_rush_td = %s, QB_completions = %s, QB_att = %s, QB_yards = %s, QB_rush_att = %s,
    QB_rush_yards = %s, QB_rush_td = %s
                WHERE fb_def_stats.team_id = %s AND fb_def_stats.year = %s""",
                (values))
    connection.commit()
    print(f"Team {year}  offensive stats has been added to fb_team_off table.")

    result = {'team_id': team_id, 'year': year,
    'games': games,'def_dvoa': def_dvoa, 'def_epa': def_epa,
    'def_dropback_epa': def_dropback_epa,
    'def_dropback_sr': def_dropback_sr,
    'def_rush_epa': def_rush_epa,
    'def_rush_sr': def_rush_sr,
    'pass_att_faced': pass_att_faced,
    'pass_comp_allowed': pass_comp_allowed,
    'pass_yards_allowed': pass_yards_allowed,
    'pass_td_allowed': pass_td_allowed,
    'allowed_pyards_per_att': allowed_pyards_per_att,
    'allowed_pyards_per_game': allowed_pyards_per_game,
    'qb_hits': qb_hits,
    'qb_sacks': qb_sacks,
    'ints': ints,
    'rush_att_faced': rush_att_faced,
    'rush_yards_allowed': rush_yards_allowed,
    'rush_td_allowed': rush_td_allowed,
    'allowed_ryards_per_att': allowed_ryards_per_att,
    'allowed_ryards_per_game': allowed_ryards_per_game,
    'rec_allowed': rec_allowed,
    'rec_td_allowed': rec_td_allowed,
    'points_allowed': points_allowed,
    'points_per_game_allowed': points_per_game_allowed,
    'rz_att_faced': rz_att_faced,
    'rz_td_allowed': rz_td_allowed,
    'rz_td_allowed_percentage': rz_td_allowed_percentage,
    'drives_faced': drives_faced,
    'plays_faced': plays_faced,
    'score_against_percentage': score_against_percentage,
    'def_to_percentage': def_to_percentage,
    'plays_faced_per_drive': plays_faced_per_drive,
    'yards_allowed_per_drive': yards_allowed_per_drive,
    'points_allowed_per_drive': points_allowed_per_drive,
    'TE_targets': TE_targets,
    'TE_rec': TE_rec,
    'TE_yards': TE_yards,
    'TE_td': TE_td,
    'WR_targets': WR_targets,
    'WR_rec': WR_rec,
    'WR_yards': WR_yards,
    'WR_td': WR_td,
    'RB_targets': RB_targets,
    'RB_rec': RB_rec,
    'RB_rec_yards': RB_rec_yards,
    'RB_rec_td': RB_rec_td,
    'RB_att': RB_att,
    'RB_rush_yards': RB_rush_yards,
    'RB_rush_td': RB_rush_td,
    'QB_completions': QB_completions,
    'QB_att': QB_att,
    'QB_yards': QB_yards,
    'QB_rush_att': QB_rush_att,
    'QB_rush_yards': QB_rush_yards,
    'QB_rush_td': QB_rush_td}

    # print(len(result))
    return result
@nfl.route('/nfl/team_defense', methods=['GET'])
def nfl_get_def_stats():
    team_id = request.args.get('id', None)
    year = request.args.get('year', None)
    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name,  fb_def_stats.*
                FROM fb_def_stats
                JOIN team ON team.id = fb_def_stats.team_id
                WHERE team.id = %s AND fb_def_stats.year = %s'''
    vals = [team_id, year]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())

    output = []
    for result in results:
        item = {'name': result[0], 'id': result[1], 'team_id': result[2], 'year': result[3], 'games': result[4], 'def_dvoa': result[5],
                'def_epa': result[6], 'def_dropback_epa': result[7], 'def_dropback_sr': result[8], 'def_rush_epa': result[9],
                'def_rush_sr': result[10], 'pass_comp_allowed': result[11], 'pass_att_faced': result[12], 'pass_yards_allowed': result[13],
                'pass_td_allowed': result[14], 'allowed_pyards_per_att': result[15], 'allowed_pyards_per_game': result[16], 'qb_hit':result[17],
                'qb_sacks': result[18], 'ints': result[19], 'rush_att_faced': result[20], 'rush_yards_allowed': result[21],
                'rush_td_allowed': result[22], 'allowed_ryards_per_att': result[23], 'allowed_ryards_per_game': result[24],
                'rec_allowed': result[25], 'rec_td_allowed': result[26], 'points_allowed': result[27], 'points_per_game_allowed': result[28],
                'rz_att_faced': result[29], 'rz_td_allowed': result[30], 'rz_td_allowed_percentage': result[31], 'drives_faced': result[32],
                'plays_faced': result[33], 'score_against_percentage': result[34], 'def_to_percentage': result[35], 'plays_faced_per_drive': result[36],
                'yards_allowed_per_drive': result[37], 'points_allowed_per_drive': result[38], 'TE_targets': result[39],
                'TE_rec': result[40], 'TE_yards': result[41], 'TE_td': result[42], 'WR_targets': result[43], 'WR_rec': result[44],
                'WR_yards': result[45], 'WR_td': result[46], 'RB_targets': result[47], 'RB_rec': result[48], 'RB_rec_yards': result[49],
                'RB_rec_td': result[50], 'RB_att': result[51], 'RB_rush_yards': result[52], 'RB_rush_td': result[53], 'QB_completions': result[54],
                'QB_att': result[55], 'QB_yards': result[56], 'QB_rush_att': result[57], 'QB_rush_yards': result[58], 'QB_rush_td': result[59]}

        if item not in output:
            output.append(item)

    return output