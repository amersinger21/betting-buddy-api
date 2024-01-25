from .db import create_connection
from flask import jsonify, request, Blueprint

sport = Blueprint("sport", __name__)

@sport.route('/sport', methods=['POST'])
def add_sport(json_dict):
    connection = create_connection()
    cursor=connection.cursor()
    sport_name = json_dict['name']
    # CHECK IF THE PLAYER DATA FOR THAT YEAR IS ALREADY IN THE TABLE
    cursor.execute("SELECT id, name FROM type_sports WHERE name = %s;",
        [sport_name])

    result = cursor.fetchone()

    if result:
        print(f"{sport_name}'s is already in type_sports table.")

    else:
        cursor.execute("INSERT INTO type_sports (name) VALUES (%s)", (sport_name))
        connection.commit()
        print(f"{sport_name} has been added to type_sports tabel.")

    result = {'name': sport_name}
    return result


@sport.route('/sport/<sport_name>')
def get_sport(sport_name):
    connection = create_connection()
    cursor=connection.cursor()

    cursor.execute("SELECT id, name FROM type_sports WHERE name = %s;",
        [sport_name])

    result = cursor.fetchone()
    result_list = []
    sport_dict = {'id': result[0], 'name': result[1]}
    result_list.append(sport_dict)
    return result_list

@sport.route('/sport', methods=['GET'])
def get_sports():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name FROM type_sports")
    results = cursor.fetchall()
    result_list = []
    for result in results:
        id = result[0]
        name = result[1]
        team_dict = {'id': id, 'name': name}
        result_list.append(team_dict)
    return result_list