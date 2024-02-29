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
                    WHERE home_team_id = %id OR away_team_id = %s ''',
                   [id])
    results = list(cursor.fetchall())
    result_list = []
    for result in results:
        player_dict = {'id': result[0], 'home_team_id': result[1], 'away_team_id': result[2],
                       'home_score': result[3], 'away_score': result[4], 'week': result[5], 'year': result[6], 'weather': result[7],
                       'vegas_line': result[8], 'weather_id': result[9], 'margin_of_victory': result[10], 'over_under': result[11],
                       'over_under_result': result[12]}
        result_list.append(player_dict)
    return result_list

@nfl.route('/nfl/rz_stat', methods=['POST'])
def nfl_add_rz_stat(json_dict):
    player_id = json_dict['player_id']
    team_id = json_dict['team_id']
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

    values = (player_id, team_id, year, rz_20_pass_att, rz_20_pass_yard, rz_20_pass_td, rz_20_pass_int, rz_20_pass_comp_percentage,
              rz_10_pass_att, rz_10_pass_yard, rz_10_pass_td, rz_10_pass_int, rz_10_comp_percentage, rz_20_targets, rz_20_receptions,
              rz_20_rec_yards, rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions,
              rz_10_rec_yards, rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_td,
              rz_20_rush_yards, rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_td, rz_10_rush_yards, rz_10_rush_percentage,
              rz_5_rush_att, rz_5_rush_td, rz_5_rush_yards, rz_5_rush_percentage)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO fb_red_zone (player_id, team_id, year, rz_20_pass_att, rz_20_pass_yards, rz_20_pass_td, rz_20_pass_int, rz_20_comp_percentage,
              rz_10_pass_att, rz_10_pass_yards, rz_10_pass_td, rz_10_pass_int, rz_10_comp_percentage, rz_20_targets, rz_20_receptions,
              rz_20_rec_yards, rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions,
              rz_10_rec_yards, rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_td,
              rz_20_rush_yards, rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_td, rz_10_rush_yards, rz_10_rush_percentage,
              rz_5_rush_att, rz_5_rush_td, rz_5_rush_yards, rz_5_rush_percentage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))
    connection.commit()
    print(f"Game has been added to games tabel.")


    result = {'player_id':player_id, 'team_id': team_id, 'year': year, 'rz_20_pass_att': rz_20_pass_att, 'rz_20_pass_yard': rz_20_pass_yard,
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

@nfl.route('/nfl/team', methods=['POST'])
def nfl_add_team_stats(json_dict):
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
