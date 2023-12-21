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


@team_offense.route('/team_offense', methods=['GET'])
def get_games():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM fb_off_stats")
    results = cursor.fetchall()
    result_list = []
    for result in results:
        print(result)
        print('---------------')
        team_id = result[1]
        year = result[2]
        games = result[3]
        off_dvoa = result[4]
        off_epa = result[5]
        dropback_epa = result[6]
        dropback_sr = result[7]
        rush_epa = result[8]
        rush_sr = result[9]
        pass_att = result[10]
        pass_comp = result[11]
        pass_yards = result[12]
        pass_td = result[13]
        int_thrown = result[14]
        pass_yards_att = result[15]
        pass_yards_per_game = result[16]
        sacks_taken = result[17]
        rush_att = result[18]
        rush_yards = result[19]
        rush_td = result[20]
        rush_yards_per_att = result[21]
        rush_yards_per_game = result[22]
        fumbles_lost = result[23]
        points_scored = result[24]
        points_scored_per_game = result[25]
        off_rz_plays = result[26]
        off_rz_td = result[27]
        total_drives = result[28]
        total_plays = result[29]
        scoring_percentage = result[30]
        to_percentage = result[31]
        avg_drive_play = result[32]
        avg_drive_points = result[33]
        avg_drive_yards = result[34]

        off_dict = {'team_id': team_id, 'year': year, 'games': games, 'off_dvoa': off_dvoa, 'off_epa': off_epa,
                  'dropback_epa': dropback_epa,
                  'dropback_sr': dropback_sr, 'rush_epa': rush_epa, 'rush_sr': rush_sr, 'pass_att': pass_att,
                  'pass_comp': pass_comp,
                  'pass_yards': pass_yards, 'pass_td': pass_td, 'int_thrown': int_thrown,
                  'pass_yards_att': pass_yards_att, 'pass_yards_per_game': pass_yards_per_game,
                  'sacks_taken': sacks_taken, 'rush_att': rush_att, 'rush_yards': rush_yards, 'rush_td': rush_td,
                  'rush_yards_per_att': rush_yards_per_att,
                  'rush_yards_per_game': rush_yards_per_game, 'fumbles_lost': fumbles_lost,
                  'points_scored': points_scored, 'points_scored_per_game': points_scored_per_game,
                  'off_rz_plays': off_rz_plays, 'off_rz_td': off_rz_td, 'total_drives': total_drives,
                  'total_plays': total_plays,
                  'scoring_percentage': scoring_percentage, 'to_percentage': to_percentage,
                  'avg_drive_play': avg_drive_play,
                  'avg_drive_points': avg_drive_points, 'avg_drive_yards': avg_drive_yards}
        result_list.append(off_dict)
    return result_list

# print(get_games())