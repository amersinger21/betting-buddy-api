from .db import create_connection
from flask import Blueprint, request

player = Blueprint("player", __name__)

@player.route('/player', methods=['POST'])
def add_player(json_dict):
    connection = create_connection()
    cursor=connection.cursor()
    last_name = json_dict['last_name']
    first_name = json_dict['first_name']
    position = json_dict['position']
    player_name = first_name + ' ' + last_name

    cursor.execute("INSERT INTO player (last_name, first_name, position) VALUES (%s, %s, %s)", (last_name, first_name, position))
    connection.commit()
    print(f"{player_name} has been added to player tabel.")

    result = {'last_name': last_name, 'first_name': first_name, 'position': position}
    return result

def update_player(json_dict):
    connection = create_connection()
    cursor=connection.cursor()
    last_name = json_dict['last_name']
    first_name = json_dict['first_name']
    position = json_dict['position']
    id = json_dict['id']

    player_name = first_name + ' ' + last_name
    values = (last_name, first_name, position, id)
    # cursor.execute("""UPDATE fb_off_stats
    #                 SET games = %s, off_dvoa = %s, off_epa = %s, dropback_epa = %s, dropback_sr = %s, rush_epa = %s, rush_sr = %s,
    #                  pass_att = %s, pass_comp = %s, pass_yards = %s, pass_td = %s, int_thrown = %s, pass_yards_att = %s,
    #                  pass_yards_per_game = %s, sacks_taken = %s, rush_att = %s, rush_yards = %s, rush_td = %s, rush_yards_per_att = %s,
    #                  rush_yards_per_game = %s, fumbles_lost = %s, points_scored = %s, points_scored_per_game = %s,
    #                  off_rz_plays = %s, off_rz_td = %s, total_drives = %s, total_plays = %s, scoring_percentage = %s, to_percentage = %s,
    #                  avg_drive_play = %s, avg_drive_points = %s, avg_drive_yards = %s
    #                  WHERE fb_off_stats.team_id = %s AND fb_off_stats.year = %s""",
    #                (values))
    cursor.execute("""UPDATE player 
                   SET last_name = %s, first_name = %s, position = %s
                   WHERE player.id = %s""", (values))
    connection.commit()
    print(f"{player_name} has been added to player tabel.")

    result = {'last_name': last_name, 'first_name': first_name, 'position': position}
    return result

@player.route('/player', methods=['GET'])
def get_player():
    first_name = request.args.get('first_name', None)
    last_name = request.args.get('last_name', None)
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute('''
                SELECT *
                FROM player
                WHERE player.first_name = %s AND player.last_name = %s''',
                [first_name, last_name])
    results = list(cursor.fetchall())
    return results
    # for result in results:
    #     player_dict = {'id': result[0], 'last_name': result[2], 'first_name': result[1]}


@player.route('/player', methods=['GET'])
def get_player_dropdown():
    sport_id = request.args.get('sport_id', None)
    connection = create_connection()
    cursor = connection.cursor()
    # return sport_id
    cursor.execute('''
                SELECT player.id, player.first_name, player.last_name
                    FROM player_teams
                        JOIN
                    player ON player.id = player_teams.player_id
                        JOIN
                    team ON team.id = player_teams.team_id
                        WHERE team.sport_id = %s
                        GROUP BY player_teams.player_id''',
                   [sport_id])
    results = list(cursor.fetchall())

    result_list = []
    for result in results:
        player_dict = {'id': result[0], 'last_name': result[2], 'first_name': result[1]}
        result_list.append(player_dict)
    return results
