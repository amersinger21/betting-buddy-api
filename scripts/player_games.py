from .db import create_connection
from flask import Blueprint


player_stats = Blueprint("player_stats", __name__)

@player_stats.route('/game', methods=['POST'])
def add_player_games(json_dict):
    player_id = json_dict['player_id']
    game_id = json_dict['game_id']
    team_id = json_dict['team_id']
    opp_id = json_dict['opp_id']
    pass_att = json_dict['pass_att']
    pass_comp = json_dict['pass_comp']
    pass_yards = json_dict['pass_yards']
    pass_td = json_dict['pass_td']
    pass_longest = json_dict['pass_longest']
    ints = json_dict['ints']
    sacks = json_dict['sacks']
    rush_att = json_dict['rush_att']
    rush_yards = json_dict['rush_yards']
    rush_td = json_dict['rush_td']
    rush_longest = json_dict['rush_longest']
    targets = json_dict['targets']
    rec = json_dict['rec']
    rec_yards = json_dict['rec_yards']
    rec_td = json_dict['rec_td']
    rec_longest = json_dict['rec_longest']
    fumbles = json_dict['fumbles']


    values = (player_id, game_id, team_id, opp_id, pass_att, pass_comp, pass_yards, pass_td, pass_longest, ints,
              sacks, rush_att, rush_yards, rush_td, rush_longest, targets, rec, rec_yards, rec_td, rec_longest, fumbles)

    connection = create_connection()
    cursor=connection.cursor()

    cursor.execute("""INSERT INTO fb_player_stats (player_id, game_id, team_id, opp_id, pass_att, pass_comp, pass_yards, pass_td, pass_longest, 
                    ints, sacks, rush_att, rush_yards, rush_td, rush_longest, targets, rec, rec_yards, rec_td, rec_longest, fumbles) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))

    connection.commit()
    print(f"Game has been added to games tabel.")


    result = {'player_id': player_id, 'game_id': game_id, 'team_id': team_id, 'opp_id': opp_id, 'pass_att': pass_att,
              'pass_comp': pass_comp, 'pass_yards': pass_yards, 'pass_td': pass_td, 'pass_longest':pass_longest, 'ints': ints,
              'sacks': sacks, 'rush_att': rush_att, 'rush_yards': rush_yards, 'rush_td': rush_td, 'rush_longest': rush_longest,
              'targets': targets, 'rec': rec, 'rec_yards': rec_yards, 'rec_td': rec_td, 'rec_longest': rec_longest, 'fumbles':fumbles}

    return result

@player_stats.route('/game', methods=['GET'])
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