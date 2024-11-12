from .db import create_connection
from flask import Blueprint, request

nba = Blueprint("nba", __name__)

# ADD GAMES
@nba.route('/nba/games', methods=['POST'])
def nba_add_game(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['year'], json_dict['date'], json_dict['day_of_the_week'], json_dict['start_time'], json_dict['away_team_id'],
              json_dict['away_score'], json_dict['home_team_id'], json_dict['home_score'], json_dict['margin_of_victory'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("INSERT INTO nba_games (year, date, day_of_the_week, start_time, away_team_id, away_score, home_team_id, home_score, margin_of_victory)"
                   " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    print(f"Game has been added to games tabel.")

@nba.route('/nba/games', methods=['GET'])
def nba_get_games():
    # GET JSON DATA AND PUT INTO VARIABLES
    team_id = request.args.get('id', None)
    number = request.args.get('number', None)
    # CHECK IF NUMBER OF ROWS IS ENTERED OR ALL
    if number != 'all':
        number = int(number)
    else:
        number = 10000

    # CONNECT TO DB
    connection = create_connection()
    cursor = connection.cursor()

    # EXECUTE SQL QUERY AND GET RESULTS AS A LIST OF DATA
    cursor.execute('''SELECT team_h.name AS home_name, team_a.name AS away_name, nba_g.*
                      FROM nba_games AS nba_g
                      LEFT JOIN team AS team_h ON team_h.id = nba_g.home_team_id
                      LEFT JOIN team AS team_a ON team_a.id = nba_g.away_team_id
                      WHERE home_team_id = %s OR away_team_id = %s
                      LIMIT 0, %s''',
                   [team_id, team_id, number])
    results = list(cursor.fetchall())

    # LOOP THROUGH RESULTS TO CREATE JSON DOCUMENT
    result_list = []
    for result in results:
        player_dict = {'id': result[2], 'year': result[3], 'date': result[4], 'day_of_the_week': result[5], 'start_time': result[6],
                       'away_team': result[1], 'away_score': result[8], 'home_team': result[0], 'home_score': result[10],
                       'margin_of_victory': result[11]}
        result_list.append(player_dict)
    return result_list
@nba.route('/nba/games_vs_opponent', methods=['GET'])
def nba_get_games_vs_opp():
    # GET JSON DATA AND PUT INTO VARIABLES
    team_id = request.args.get('id', None)
    opp_id = request.args.get('opp_id', None)
    number = request.args.get('number', None)
    # CHECK IF NUMBER OF ROWS IS ENTERED OR ALL
    if number != 'all':
        number = int(number)
    else:
        number = 10000

    # CONNECT TO DB
    connection = create_connection()
    cursor = connection.cursor()

    # EXECUTE SQL QUERY AND GET RESULTS AS A LIST OF DATA
    cursor.execute('''SELECT team_h.name AS home_name, team_a.name AS away_name, nba_g.*
                      FROM nba_games AS nba_g
                      LEFT JOIN team AS team_h ON team_h.id = nba_g.home_team_id
                      LEFT JOIN team AS team_a ON team_a.id = nba_g.away_team_id
                      WHERE (home_team_id = %s OR away_team_id = %s) AND (home_team_id = %s OR away_team_id = %s)
                      LIMIT 0, %s''',
                   [team_id, team_id, opp_id, opp_id, number])
    results = list(cursor.fetchall())

    # LOOP THROUGH RESULTS TO CREATE JSON DOCUMENT
    result_list = []
    for result in results:
        player_dict = {'id': result[2], 'year': result[3], 'date': result[4], 'day_of_the_week': result[5], 'start_time': result[6],
                       'away_team': result[1], 'away_score': result[8], 'home_team': result[0], 'home_score': result[10],
                       'margin_of_victory': result[11]}
        result_list.append(player_dict)
    return result_list


# TEAM STATS
@nba.route('/nba/team_stats', methods=['GET'])
def nba_get_team_stats():
    team_id = request.args.get('id', None)
    year = request.args.get('year', None)

    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name, nba_team_stats.*
                FROM nba_team_stats
                JOIN team ON team.id = nba_team_stats.team_id
                WHERE team.id = %s AND nba_team_stats.year = %s'''
    vals = [team_id, year]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())
    output = []
    for result in results:
        item = {'name': result[0], 'id': result[1], 'team_id': result[2], 'year': result[3], 'fg_made': result[4], 'fg_att': result[5],
                'fg_percentage': result[6], 'three_pointers_made': result[7], 'three_pointers_att': result[8], 'three_pointers_percentage': result[9], 'two_pointers_made': result[10],
                'two_pointers_att': result[11], 'two_pointers_percentage': result[12], 'ft_made': result[13], 'ft_att': result[14], 'ft_percentage': result[15],
                'off_reb': result[16], 'def_reb': result[17], 'total_reb': result[18], 'turn_overs': result[19],
                'personal_fouls': result[20], 'points': result[21], 'fg_made_pg': result[22], 'fg_att_pg': result[23],
                'fg_percentage_pg': result[25], 'three_pointers_made_pg': result[26], 'three_pointers_att_pg': result[27], 'three_pointers_percentage_pg': result[28], 'two_pointers_made_pg': result[29],
                'two_pointers_att_pg': result[30], 'two_pointers_percentage_pg': result[31], 'ft_made_pg': result[32], 'ft_att_pg': result[33], 'ft_percentage_pg': result[34],
                'off_reb_pg': result[35], 'def_reb_pg': result[36], 'total_reb_pg': result[37], 'turn_overs_pg': result[38],
                'personal_fouls_pg': result[39], 'points_pg': result[40], 'fg_made_p100': result[41], 'fg_att_p100': result[42],
                'fg_percentage_p100': result[43], 'three_pointers_made_p100': result[44], 'three_pointers_att_p100': result[45],
                'three_pointers_percentage_p100': result[46], 'two_pointers_madep100': result[47],
                'two_pointers_attv': result[48], 'two_pointers_percentage_p100': result[49], 'ft_made_p100': result[50],
                'ft_att_p100': result[51], 'ft_percentage_p100': result[52], 'off_reb_p100': result[53], 'def_reb_p100': result[54],
                'total_reb_p100': result[55], 'turn_overs_p100': result[56], 'personal_fouls_p100': result[57], 'points_p100': result[58]}

        if item not in output:
            output.append(item)

    return output


# TEAM STATS AGAINST
@nba.route('/nba/team_stats_against', methods=['GET'])
def nba_get_team_stats_against():
    team_id = request.args.get('id', None)
    year = request.args.get('year', None)

    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name, nba_team_stats_against.*
                FROM nba_team_stats_against
                JOIN team ON team.id = nba_team_stats_against.team_id
                WHERE team.id = %s AND nba_team_stats_against.year = %s'''
    vals = [team_id, year]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())
    output = []
    for result in results:
        item = {'name': result[0], 'id': result[1], 'team_id': result[2], 'year': result[3], 'fg_made': result[4], 'fg_att': result[5],
                'fg_percentage': result[6], 'three_pointers_made': result[7], 'three_pointers_att': result[8], 'three_pointers_percentage': result[9], 'two_pointers_made': result[10],
                'two_pointers_att': result[11], 'two_pointers_percentage': result[12], 'ft_made': result[13], 'ft_att': result[14], 'ft_percentage': result[15],
                'off_reb': result[16], 'def_reb': result[17], 'total_reb': result[18], 'turn_overs': result[19],
                'personal_fouls': result[20], 'points': result[21], 'fg_made_pg': result[22], 'fg_att_pg': result[23],
                'fg_percentage_pg': result[25], 'three_pointers_made_pg': result[26], 'three_pointers_att_pg': result[27], 'three_pointers_percentage_pg': result[28], 'two_pointers_made_pg': result[29],
                'two_pointers_att_pg': result[30], 'two_pointers_percentage_pg': result[31], 'ft_made_pg': result[32], 'ft_att_pg': result[33], 'ft_percentage_pg': result[34],
                'off_reb_pg': result[35], 'def_reb_pg': result[36], 'total_reb_pg': result[37], 'turn_overs_pg': result[38],
                'personal_fouls_pg': result[39], 'points_pg': result[40], 'fg_made_p100': result[41], 'fg_att_p100': result[42],
                'fg_percentage_p100': result[43], 'three_pointers_made_p100': result[44], 'three_pointers_att_p100': result[45],
                'three_pointers_percentage_p100': result[46], 'two_pointers_madep100': result[47],
                'two_pointers_attv': result[48], 'two_pointers_percentage_p100': result[49], 'ft_made_p100': result[50],
                'ft_att_p100': result[51], 'ft_percentage_p100': result[52], 'off_reb_p100': result[53], 'def_reb_p100': result[54],
                'total_reb_p100': result[55], 'turn_overs_p100': result[56], 'personal_fouls_p100': result[57], 'points_p100': result[58]}

        if item not in output:
            output.append(item)

    return output


@nba.route('/nba/team_standings', methods=['GET'])
def nba_get_team_standings():
    team_id = request.args.get('id', None)
    year = request.args.get('year', None)

    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name, nba_standings.*
                FROM nba_standings
                JOIN team ON team.id = nba_standings.team_id
                WHERE team.id = %s AND nba_standings.year = %s;'''
    vals = [team_id, year]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())
    output = []
    for result in results:
        item = {'name': result[0], 'id': result[1], 'team_id': result[2], 'year': result[3], 'conf_rank': result[4], 'record': result[5],
                'win_percentage': result[6], 'home_record': result[7], 'away_record': result[8], 'east_conf_record': result[9], 'west_conf_record': result[10],
                'pre_allstar_record': result[11], 'post_allstar_record': result[12], 'one_score_game_record': result[13], 'ten_point_game_record': result[14], 'oct_record': result[15],
                'nov_record': result[16], 'dec_record': result[17], 'jan_record': result[18], 'feb_record': result[19],
                'mar_record': result[20], 'apr_record': result[21]}

        if item not in output:
            output.append(item)

    return output



@nba.route('/nba/player_stats', methods=['GET'])
def nba_get_player_data():
    player_id = request.args.get('id', None)
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = float(request.args.get('value', None))
    connection = create_connection()
    cursor = connection.cursor()
    print(f"player_id = {player_id}")
    print(f"value = {value}")
    print(f"operator = {operator}")

    column = 'nba_player_stats.' + column_name
    print(f"column = {column}")

    if operator == 'over':
        op_val = '>'
    else:
        op_val = '<'

    query = f'''SELECT CONCAT(player.first_name, ' ', player.last_name) AS player_name, player.position, nba_player_stats.*
                FROM nba_player_stats
                JOIN player ON player.id = nba_player_stats.player_id
                WHERE player.id = %s AND {column} {op_val} %s'''
    vals = [player_id, value]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())

    output = []
    for result in results:
        item = {'name': result[0],'pos': result[1], 'id': result[2], 'player_id': result[3], 'game_id': result[4], 'team_id': result[5],
        'opp_id': result[6], 'pass_att': result[7], 'pass_comp': result[8], 'pass_yards': result[9], 'pass_td': result[10], 'pass_longest': result[11],
        'ints': result[12], 'sacks': result[13], 'rush_att': result[14], 'rush_yards': result[15], 'rush_td': result[16], 'rush_longest': result[17],
        'targets': result[18], 'rec': result[19], 'rec_yards': result[20], 'rec_td': result[21], 'rec_longest': result[22], 'fumbles': result[23]}
        output.append(item)

    return output

