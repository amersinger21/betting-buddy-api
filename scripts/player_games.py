from .db import create_connection
from flask import Blueprint, request


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

@player_stats.route('/player_stats', methods=['GET'])
def get_games():
    player_id = request.args.get('player_id', None)
    column_name = request.args.get('column_name', None)
    operator = request.args.get('operator', None)
    value = float(request.args.get('value', None))
    connection = create_connection()
    cursor = connection.cursor()
    print(f"player_id = {player_id}")
    print(f"value = {value}")
    print(f"operator = {operator}")

    column = 'fb_player_stats.' + column_name
    print(f"column = {column}")

    if operator == 'over':
        op_val = '>'
    else:
        op_val = '<'

    query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name,
                    player.position, fb_player_stats.*
                    FROM
                    fb_player_stats
                    JOIN
                    player ON player.id = fb_player_stats.player_id
                    WHERE player.id = %s AND {column} {op_val} %s'''
    vals = [player_id, value]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())

    output = []
    for result in results:
        item = {'name': '', 'pos': '', 'id': 0, 'player_id': 0, 'game_id': 0, 'team_id': 0, 'opp_id': 0, 'pass_att': 0, 'pass_comp': 0, 'pass_yards': 0,
                'pass_td': 0, 'pass_longest': 0, 'ints': 0, 'sacks': 0, 'rush_att': 0, 'rush_yards': 0, 'rush_td': 0,
                'rush_longest': 0, 'targets': 0, 'rec': 0, 'rec_yards': 0, 'rec_td': 0, 'rec_longest': 0, 'fumbles': 0}
        item['name'] = result[0]
        item['pos'] = result[1]
        item['id'] = result[2]
        item['player_id'] = result[3]
        item['game_id'] = result[4]
        item['team_id'] = result[5]
        item['opp_id'] = result[6]
        item['pass_att'] = result[7]
        item['pass_comp'] = result[8]
        item['pass_yards'] = result[9]
        item['pass_td'] = result[10]
        item['pass_longest'] = result[11]
        item['ints'] = result[12]
        item['sacks'] = result[13]
        item['rush_att'] = result[14]
        item['rush_yards'] = result[15]
        item['rush_td'] = result[16]
        item['rush_longest'] = result[17]
        item['targets'] = result[18]
        item['rec'] = result[19]
        item['rec_yards'] = result[20]
        item['rec_td'] = result[21]
        item['rec_longest'] = result[22]
        item['fumbles'] = result[23]
        output.append(item)

    return output

