from .db import create_connection
from flask import Blueprint, request, jsonify
import pandas as pd

player = Blueprint("player", __name__)

nfl_team_dict = {'ARI': 1, 'ATL': 2, 'BAL': 3, 'BUF': 4, 'CAR': 5, 'CHI': 6, 'CIN': 7, 'CLE': 8, 'DAL': 9, 'DEN': 10,
                 'DET': 11, 'GB': 12, 'HOU': 13, 'IND': 14, 'JAX': 15, 'KC': 16, 'LAC': 17, 'LAR': 18, 'LV': 19,
                 'MIA': 20, 'MIN': 21, 'NE': 22, 'NO': 23, 'NYG': 24, 'NYJ': 25, 'PHI': 26, 'PIT': 27, 'SEA': 28,
                 'SF': 29, 'TB': 30, 'TEN': 31, 'WAS': 32}

@player.route('/player', methods=['POST'])
def add_player():
    file = request.files['player_template']

    # Read CSV data
    df = pd.read_csv(file)
    print(df)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        values = [row['last_name'], row['first_name'], row['sport_id'], row['position'], row['image'], row['current_team'],
                  row['currently_playing']]

        # execute sql query inserting into table
        cursor.execute(
            "INSERT INTO player (last_name, first_name, sport_id, position, image, current_team, currently_playing) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (values))

        connection.commit()
        print(f"{row['first_name']} {row['last_name']} has been added to player tabel.")

    return f"Player table has been updated"


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

    # execute the query getting the nfl players
    cursor.execute(f'''SELECT player.id, player.first_name, player.last_name, player.position, player.current_team, team.id
                    FROM player
                    JOIN
                    team ON team.name = player.current_team
                    WHERE player.sport_id = {sport_id} and team.sport_id = {sport_id} and player.currently_playing = 'Y'
                    ''')
    results = list(cursor.fetchall())

    result_list = []
    for result in results:
        print(result)
        player_dict = {'id': result[0], 'last_name': result[2], 'first_name': result[1], 'position': result[3], 'team': result[4],
                       'full_name': f"{result[1]} {result[2]}", 'team_id': result[5]}
        result_list.append(player_dict)

    # Enable Access-Control-Allow-Origin
    result_list = jsonify(result_list)
    result_list.headers.add("Access-Control-Allow-Origin", "*")
    return result_list


@player.route('/players', methods=['PUT'])
def update_player_status(json_dict):
    file = request.files['player_template']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        values = [row['current_team'], row['currently_playing'], row['id'], row['last_name'], row['first_name']]


        cursor.execute('''UPDATE player
                SET current_team = %s, currently_playing = %s
                WHERE player.id = %s AND player.last_name = %s AND player.first_name = %s''', (values))
        connection.commit()
        print(f"{row['first_name']} {row['last_name']} has been added to player tabel.")




