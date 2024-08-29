from .db import create_connection
from flask import Blueprint, request, jsonify

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

@player.route('/player', methods=['PUT'])
def update_player(json_dict):
    connection = create_connection()
    cursor=connection.cursor()
    last_name = json_dict['last_name']
    first_name = json_dict['first_name']
    position = json_dict['position']
    id = json_dict['id']

    player_name = first_name + ' ' + last_name
    values = (last_name, first_name, position, id)

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

    # Enable Access-Control-Allow-Origin
    results = jsonify(results)
    results.headers.add("Access-Control-Allow-Origin", "*")
    return results



@player.route('/players', methods=['GET'])
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

    # Enable Access-Control-Allow-Origin
    results = jsonify(results)
    results.headers.add("Access-Control-Allow-Origin", "*")
    return results
