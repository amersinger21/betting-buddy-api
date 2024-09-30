import pandas as pd

from .db import create_connection
from flask import Blueprint, request, jsonify

player = Blueprint("player", __name__)

@player.route('/player', methods=['POST'])
def add_player(json_dict):
    # initialize variables
    connection = create_connection()
    cursor=connection.cursor()
    last_name = json_dict['last_name']
    first_name = json_dict['first_name']
    position = json_dict['position']
    current_team = json_dict['current_team']
    currently_playing =json_dict['currently_playing']


    # execute sql query inserting into table
    cursor.execute("INSERT INTO player (last_name, first_name, position, current_team, currently_playing) VALUES (%s, %s, %s, %s, %s)", (last_name, first_name, position, current_team, currently_playing))
    connection.commit()
    print(f"{first_name} {last_name} has been added to player tabel.")

    result = {'last_name': last_name, 'first_name': first_name, 'position': position, 'current_team': current_team, 'current_playing': currently_playing}
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
                    FROM nfl_player_teams
                        JOIN
                    player ON player.id = nfl_player_teams.player_id
                        JOIN
                    team ON team.id = nfl_player_teams.team_id
                        WHERE team.sport_id = %s and player.currently_playing = %s
                        GROUP BY nfl_player_teams.player_id''',
                   [sport_id,'Y'])
    results = list(cursor.fetchall())

    result_list = []
    for result in results:
        player_dict = {'id': result[0], 'last_name': result[2], 'first_name': result[1]}
        result_list.append(player_dict)

    # Enable Access-Control-Allow-Origin
    result_list = jsonify(result_list)
    result_list.headers.add("Access-Control-Allow-Origin", "*")
    return result_list


