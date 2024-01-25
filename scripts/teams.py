from .db import create_connection
from flask import Blueprint, request

teams = Blueprint("teams", __name__)

# @team.route('/team', methods=['POST'])
# def add_team(json_dict):
#     connection = create_connection()
#     cursor=connection.cursor()
#     team_name = json_dict['name']
#     sport_id = json_dict['sport_id']
#
#     # CHECK IF THE PLAYER DATA FOR THAT YEAR IS ALREADY IN THE TABLE
#     cursor.execute("SELECT name, sport_id FROM team WHERE name = %s AND sport_id = %s;",
#         [team_name, sport_id])
#
#     result = cursor.fetchone()
#
#     if result:
#         print(f"{team_name}'s is already in type_sports table.")
#
#     else:
#         cursor.execute("INSERT INTO team (name, sport_id) VALUES (%s, %s)", (team_name, sport_id))
#         connection.commit()
#         print(f"{team_name} has been added to type_sports tabel.")
#
#     result = {'name': team_name, 'sport_id': sport_id}
#     return result
#
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

@teams.route('/teams', methods=['GET'])
def get_teams():
    sport_id = request.args.get('sport_id', None)
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''SELECT team.id, team.name FROM player_teams
                    JOIN    
                team ON team.id = player_teams.team_id
                    WHERE team.sport_id = %s
                    GROUP BY player_teams.team_id''',
        [sport_id])
    results = cursor.fetchall()
    result_list = []
    for result in results:
        team_dict = {'id': result[0], 'name': result[1]}
        result_list.append(team_dict)
    return result_list