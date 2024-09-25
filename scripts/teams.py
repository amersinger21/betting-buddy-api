from .db import create_connection
from flask import Blueprint, request

teams = Blueprint("teams", __name__)

@teams.route('/teams', methods=['POST'])
def add_team(json_dict):
    connection = create_connection()
    cursor=connection.cursor()
    name = json_dict['name']
    full_name = json_dict['full_name']
    sport_id = json_dict['sport_id']

    cursor.execute("INSERT INTO team (name, sport_id, full_name) VALUES (%s, %s, %s)", (name, sport_id, full_name))

    connection.commit()
    print(f"{full_name} has been added to player tabel.")

    result = {'sport_id': sport_id, 'name': name, 'full_name': full_name}
    
    return result

@teams.route('/teams', methods=['GET'])
def get_teams():
    sport_id = request.args.get('sport_id', None)
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''select * from team
                        WHERE sport_id = %s''',
        [sport_id])
    results = cursor.fetchall()
    result_list = []
    for result in results:
        team_dict = {'id': result[0], 'name': result[1]}
        result_list.append(team_dict)
    
    results_list = jsonify(results_list)
    results_list.headers.add("Access-Control-Allow-Origin", "*")
    return result_list


#
# @team.route('/team/<team_name_sportid>')
# def get_team(team_name):
#     connection = create_connection()
#     cursor=connection.cursor()
#     team_split = team_name.split('_')
#     team_name = team_split[0]
#     sport_id = int(team_split[1])
#
#     cursor.execute("SELECT id, name, sport_id FROM team WHERE name = %s and sport_id = %s;",
#         [team_name, sport_id])
#
#     result = cursor.fetchone()
#     result_list = []
#     player_dict = {'id': result[0], 'team_name': result[1], 'sport_id': result[2]}
#     result_list.append(player_dict)
#     return result_list