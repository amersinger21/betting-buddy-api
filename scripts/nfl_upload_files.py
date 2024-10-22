import pandas as pd

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

    cursor.execute("""UPDATE nfl_team_offense
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


# NFL TEAM STANDINGS
@nfl.route('/nfl/standings', methods=['POST'])
def nfl_add_standings(json_dict):
    year = json_dict['year']
    team_id = json_dict['team_id']
    wins = json_dict['wins']
    losses = json_dict['losses']
    ties = json_dict['ties']
    win_loss_percentage = json_dict['win_loss_percentage']
    points_for = json_dict['points_for']
    points_against = json_dict['points_against']
    point_diff = json_dict['point_diff']
    avg_margin_of_victory = json_dict['avg_margin_of_victory']
    strength_of_schedule = json_dict['strength_of_schedule']

    values = (year, team_id, wins, losses, ties, win_loss_percentage, points_for, points_against, point_diff,
              avg_margin_of_victory, strength_of_schedule)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO nfl_standings (year, team_id, wins, losses, ties, win_loss_percentage, points_for, points_against, point_diff,
              avg_margin_of_victory, strength_of_schedule) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))
    connection.commit()
    print(f"Game has been added to nfl_standings table.")

    result = {'year':year, 'team_id': team_id, 'wins': wins, 'losses': losses, 'ties': ties,'win_loss_percentage': win_loss_percentage,
              'points_for': points_for, 'points_against': points_against, 'point_diff': point_diff, 'avg_margin_of_victory': avg_margin_of_victory,
              'strength_of_schedule': strength_of_schedule}

    return result
@nfl.route('/nfl/standings', methods=['PUT'])
def nfl_update_standings(json_dict):
    year = json_dict['year']
    team_id = json_dict['team_id']
    wins = json_dict['wins']
    losses = json_dict['losses']
    ties = json_dict['ties']
    win_loss_percentage = json_dict['win_loss_percentage']
    points_for = json_dict['points_for']
    points_against = json_dict['points_against']
    point_diff = json_dict['point_diff']
    avg_margin_of_victory = json_dict['avg_margin_of_victory']
    strength_of_schedule = json_dict['strength_of_schedule']

    values = (wins, losses, ties, win_loss_percentage, points_for, points_against, point_diff, avg_margin_of_victory,
              strength_of_schedule, team_id, year)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""UPDATE  nfl_standings 
                SET wins = %s, losses = %s, ties = %s, win_loss_percentage = %s, points_for = %s,
                 points_against = %s, point_diff = %s, avg_margin_of_victory = %s, strength_of_schedule = %s
                WHERE nfl_standings.team_id = %s and nfl_standings.year = %s""",
                   (values))

    connection.commit()
    print(f"Game has been added to nfl_standings table.")

    result = {'year':year, 'team_id': team_id, 'wins': wins, 'losses': losses, 'ties': ties,'win_loss_percentage': win_loss_percentage,
              'points_for': points_for, 'points_against': points_against, 'point_diff': point_diff, 'avg_margin_of_victory': avg_margin_of_victory,
              'strength_of_schedule': strength_of_schedule}

    return result


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
    total_points = json_dict['total_points']
    over_under_result = json_dict['over_under_result']

    values = (week, year, home_id, home_score, away_id, away_score, winner, margin_of_victory, weather_id, vegas_line,
              vegas_line_result, over_under, total_points, over_under_result)

    connection = create_connection()
    cursor=connection.cursor()

    cursor.execute('''INSERT INTO nfl_games (week, year, home_id, home_score, away_id, away_score, winner, margin_of_victory, weather_id, vegas_line,
              vegas_line_result, over_under, total_points, over_under_result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                   (values))
    connection.commit()

    result = { 'week': week, 'year': year, 'home_team': home_id, 'home_score': home_score, 'away_team': away_id, 'away_score': away_score,
               'winner': winner, 'margin_of_victory': margin_of_victory, 'weather_id': weather_id, 'vegas_line': vegas_line,
               'vegas_line_result': vegas_line_result,'over_under': over_under, 'total_points': total_points, 'over_under_result': over_under_result}

    return result

@nfl.route('/nfl/games', methods=['PUT'])
def nfl_update_game_info(json_dict):
    id = json_dict['id']
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
    total_points = json_dict['total_points']
    over_under_result = json_dict['over_under_result']

    values = (week, year, home_score, away_score, winner, margin_of_victory, weather_id, vegas_line,
              vegas_line_result, over_under, total_points, over_under_result, id, home_id, away_id)

    connection = create_connection()
    cursor=connection.cursor()

    cursor.execute('''UPDATE nfl_games 
            SET week = %s, year = %s, home_score = %s, away_score = %s, winner = %s, margin_of_victory = %s, weather_id = %s, vegas_line = %s,
            vegas_line_result = %s, over_under = %s, total_points = %s, over_under_result = %s
            WHERE nfl_games.id = %s AND nfl_games.home_id = %s AND nfl_games.away_id = %s''', (values))
    connection.commit()

    print(f"Game info table has been updated..")

    result = {'week': week, 'year': year, 'home_team': home_id, 'home_score': home_score, 'away_team': away_id, 'away_score': away_score,
               'winner': winner, 'margin_of_victory': margin_of_victory, 'weather_id': weather_id, 'vegas_line': vegas_line,
               'vegas_line_result': vegas_line_result,'over_under': over_under, 'total_points': total_points, 'over_under_result': over_under_result}

    return result