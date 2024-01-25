from .db import create_connection
from flask import Blueprint



weather = Blueprint("weather", __name__)

@weather.route('/weather', methods=['POST'])
def add_weather(json_dict):
    connection = create_connection()
    cursor=connection.cursor()
    weather_type = json_dict['name']
    # CHECK IF THE PLAYER DATA FOR THAT YEAR IS ALREADY IN THE TABLE
    cursor.execute("SELECT id, name FROM type_weather WHERE name = %s;",
        [weather_type])

    result = cursor.fetchone()

    if result:
        print(f"{weather_type}'s is already in type_weather table.")

    else:
        cursor.execute("INSERT INTO type_weather (name) VALUES (%s)", (weather_type))
        connection.commit()
        print(f"{weather_type} has been added to type_weather tabel.")

    result = {'name': weather_type}
    return result


@weather.route('/weather/<weather_name>')
def get_weather(weather_name):
    connection = create_connection()
    cursor=connection.cursor()

    cursor.execute("SELECT id, name FROM type_weather WHERE name = %s;",
        [weather_name])

    result = cursor.fetchone()
    result_list = []
    sport_dict = {'id': result[0], 'name': result[1]}
    result_list.append(sport_dict)
    return result_list

@weather.route('/weather', methods=['GET'])
def get_weathers():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name FROM type_weather")
    results = cursor.fetchall()
    result_list = []
    for result in results:
        id = result[0]
        name = result[1]
        weather_dict = {'id': id, 'name': name}
        result_list.append(weather_dict)
    return result_list




