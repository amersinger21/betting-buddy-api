from .db import create_connection
from flask import Blueprint, request


games = Blueprint("game", __name__)

@games.route('/game', methods=['POST'])
def add_game(json_dict):
    home_team = json_dict['home_team_id']
    away_team = json_dict['away_team_id']
    home_score = json_dict['home_score']
    away_score = json_dict['away_score']
    week = json_dict['week']
    year = json_dict['year']
    weather_id = json_dict['weather_id']
    vegas_line = json_dict['vegas_line']
    vegas_line_results = json_dict['vegas_line_result']
    margin_of_victory = json_dict['margin_of_victory']
    over_under = json_dict['over_under']
    over_under_results = json_dict['over_under_result']

    values = (home_team, away_team, home_score, away_score, week, year, weather_id, vegas_line, vegas_line_results, margin_of_victory, over_under,
              over_under_results)


    connection = create_connection()
    cursor=connection.cursor()

    cursor.execute("INSERT INTO games (home_team_id, away_team_id, home_score, away_score, week, year, weather_id, vegas_line, vegas_line_result, margin_of_victory, over_under, over_under_result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (values))
    connection.commit()
    print(f"Game has been added to games tabel.")


    result = {'home_team': home_team, 'away_team': away_team, 'home_score': home_score, 'away_score': away_score, 'week': week,
              'year': year, 'weather_id': weather_id, 'vegas_line': vegas_line, 'vegas_line_result': vegas_line_results, 'margin_of_victory': margin_of_victory,
              'over_under': over_under, 'over_under_result': over_under_results}

    return result

@games.route('/game', methods=['GET'])
def get_games():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM games")
    results = cursor.fetchall()
    result_list = []
    for result in results:
        id = result[0]
        home_team_id = result[1]
        away_team_id = result[2]
        home_score = result[3]
        away_score = result[4]
        week = result[5]
        year = result[6]
        weather_id = result[7]
        vegas_line = result[8]
        vegas_line_result = result[9]
        margin_of_victory = result[10]
        over_under = result[11]
        over_under_result = result[12]

        game_dict = {'id': id, 'home_team': home_team_id, 'away_team': away_team_id, 'home_score': home_score, 'away_score': away_score,
                  'week': week, 'year': year, 'weather_id': weather_id, 'vegas_line': vegas_line, 'vegas_line_result': vegas_line_result,
                  'margin_of_victory': margin_of_victory, 'over_under': over_under, 'over_under_results': over_under_result}
        result_list.append(game_dict)
    return result_list

# @games.route('/game/<player_id>', methods=['GET'])
# def get_games():
#     connection = create_connection()
#     cursor = connection.cursor()
#     cursor.execute("SELECT * FROM games")
#     results = cursor.fetchall()
#     result_list = []
#     for result in results:
#         id = result[0]
#         home_team_id = result[1]
#         away_team_id = result[2]
#         home_score = result[3]
#         away_score = result[4]
#         week = result[5]
#         year = result[6]
#         weather_id = result[7]
#         vegas_line = result[8]
#         vegas_line_result = result[9]
#         margin_of_victory = result[10]
#         over_under = result[11]
#         over_under_result = result[12]
#
#         game_dict = {'id': id, 'home_team': home_team_id, 'away_team': away_team_id, 'home_score': home_score, 'away_score': away_score,
#                   'week': week, 'year': year, 'weather_id': weather_id, 'vegas_line': vegas_line, 'vegas_line_result': vegas_line_result,
#                   'margin_of_victory': margin_of_victory, 'over_under': over_under, 'over_under_results': over_under_result}
#         result_list.append(game_dict)
#     return result_list