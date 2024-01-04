from .db import create_connection
from flask import jsonify, request, Blueprint

team_offense = Blueprint("team_offense", __name__)

@team_offense.route('/team_offense', methods=['POST'])
def add_team_offense(json_dict):
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


@team_offense.route('/team_stat', methods=['GET'])
def get_games():
    team_id = request.args.get('team_id', None)
    # column_name = request.args.get('column_name', None)
    # operator = request.args.get('operator', None)
    # value = float(request.args.get('value', None))
    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    # query = f'''SELECT team.name, fb_off_stats.*, fb_def_stats.*
    #             FROM fb_off_stats
    #             JOIN team ON team.id = fb_off_stats.team_id
    #             JOIN fb_def_stats ON fb_def_stats.team_id = fb_off_stats.team_id
    #             WHERE team.id = %s'''

    query = f'''SELECT team.name,  fb_off_stats.*, fb_def_stats.*
                FROM fb_off_stats
                JOIN team ON team.id = fb_off_stats.team_id 
                JOIN fb_def_stats ON (fb_def_stats.team_id =  fb_off_stats.team_id) AND (fb_def_stats.year =  fb_off_stats.year)
                WHERE team.id = %s'''
    vals = [team_id]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())
    print(results)
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

    # print(output)
    return output
