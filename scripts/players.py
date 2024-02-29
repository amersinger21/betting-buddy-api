from .db import create_connection
from flask import Blueprint, request

players = Blueprint("players", __name__)

@players.route('/player', methods=['POST'])
def add_player(json_dict):
    connection = create_connection()
    cursor=connection.cursor()
    last_name = json_dict['last_name']
    first_name = json_dict['first_name']
    position = json_dict['position']
    player_name = first_name + ' ' + last_name
    # CHECK IF THE PLAYER DATA FOR THAT YEAR IS ALREADY IN THE TABLE
    cursor.execute("SELECT id, last_name, first_name, position FROM player WHERE last_name = %s and first_name = %s and position = %s;",
        [last_name, first_name, position])

    result = cursor.fetchone()

    if result:
        print(f"{player_name}'s is already in player table.")

    else:
        cursor.execute("INSERT INTO player (last_name, first_name, position) VALUES (%s, %s, %s)", (last_name, first_name, position))
        connection.commit()
        print(f"{player_name} has been added to player tabel.")

    result = {'last_name': last_name, 'first_name': first_name, 'position': position}
    return result


@players.route('/players', methods=['GET'])
def get_players():
    sport_id = request.args.get('sport_id', None)
    connection = create_connection()
    cursor = connection.cursor()
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
    return result_list
