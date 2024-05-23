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
@nba.route('/nba/team_stats', methods=['POST'])
def nba_add_team_stats(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['games'], json_dict['fg_made'], json_dict['fg_att'], json_dict['fg_percentage'],
              json_dict['three_pointers_made'], json_dict['three_pointers_att'], json_dict['three_point_percentage'], json_dict['two_pointers_made'],
              json_dict['two_point_att'], json_dict['two_point_percentage'], json_dict['ft_made'], json_dict['ft_att'], json_dict['ft_percentage'],
              json_dict['off_reb'], json_dict['def_reb'], json_dict['total_reb'], json_dict['assists'], json_dict['steals'], json_dict['blocks'],
              json_dict['turn_overs'], json_dict['personal_fouls'], json_dict['points'], json_dict['fg_made_pg'],  json_dict['fg_att_pg'],
              json_dict['fg_percentage_pg'], json_dict['three_pointers_made_pg'], json_dict['three_pointers_att_pg'], json_dict['three_point_percentage_pg'],
              json_dict['two_pointers_made_pg'], json_dict['two_point_att_pg'], json_dict['two_point_percentage_pg'], json_dict['ft_made_pg'],
              json_dict['ft_att_pg'], json_dict['ft_percentage_pg'], json_dict['off_reb_pg'], json_dict['def_reb_pg'],  json_dict['total_reb_pg'],
              json_dict['assists_pg'], json_dict['steals_pg'], json_dict['blocks_pg'], json_dict['turn_overs_pg'], json_dict['personal_fouls_pg'],
              json_dict['points_pg'], json_dict['fg_made_p100'], json_dict['fg_att_p100'], json_dict['fg_percentage_p100'],
              json_dict['three_pointers_made_p100'], json_dict['three_pointers_att_p100'], json_dict['three_point_percentage_p100'],
              json_dict['two_pointers_made_p100'], json_dict['two_point_att_p100'], json_dict['two_point_percentage_p100'], json_dict['ft_made_p100'],
              json_dict['ft_att_p100'], json_dict['ft_percentage_p100'], json_dict['off_reb_p100'], json_dict['def_reb_p100'],
              json_dict['total_reb_p100'], json_dict['assists_p100'], json_dict['steals_p100'], json_dict['blocks_p100'],
              json_dict['turn_overs_p100'], json_dict['personal_fouls_p100'], json_dict['points_p100'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""INSERT INTO nba_team_stats (team_id, year, games, fg_made, fg_att, fg_percentage, three_pointers_made, three_pointers_att, three_point_percentage, two_pointers_made, two_point_att, two_point_percentage, ft_made, ft_att, ft_percentage, off_reb, def_reb, total_reb, assists, steals, blocks, turn_overs, personal_fouls, points, fg_made_pg, fg_att_pg, fg_percentage_pg, three_pointers_made_pg, three_pointers_att_pg, three_point_percentage_pg, two_pointers_made_pg, two_point_att_pg, two_point_percentage_pg, ft_made_pg, ft_att_pg, ft_percentage_pg, off_reb_pg, def_reb_pg, total_reb_pg, assists_pg, steals_pg, blocks_pg, turn_overs_pg, personal_fouls_pg, points_pg, fg_made_p100, fg_att_p100, fg_percentage_p100, three_pointers_made_p100, three_pointers_att_p100, three_point_percentage_p100, two_pointers_made_p100, two_point_att_p100, two_point_percentage_p100, ft_made_p100, ft_att_p100, ft_percentage_p100, off_reb_p100, def_reb_p100, total_reb_p100, assists_p100, steals_p100, blocks_p100, turn_overs_p100, personal_fouls_p100, points_p100) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
      %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    return f"{json_dict['team_id']}'s {json_dict['year']} data has been added to nba_team_stats table."
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
@nba.route('/nba/team_stats', methods=['PUT'])
def nba_update_team_stats(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['games'], json_dict['fg_made'], json_dict['fg_att'], json_dict['fg_percentage'],
    json_dict['three_pointers_made'] , json_dict['three_pointers_att'], json_dict['three_pointers_percentage'], json_dict['two_pointers_made'],
    json_dict['two_pointers_att'], json_dict['two_pointers_percentage'], json_dict['ft_made'], json_dict['ft_att'], json_dict['ft_percentage'],
    json_dict['off_reb'], json_dict['def_reb'], json_dict['total_reb'], json_dict['assists'], json_dict['steals'],
    json_dict['blocks'], json_dict['turn_overs'], json_dict['personal_fouls'], json_dict['points'], json_dict['fg_made_pg'], json_dict['fg_att_pg'],
    json_dict['fg_made_percentage'], json_dict['three_pointers_made_pg'], json_dict['three_pointers_att_pg'], json_dict['three_pointers_percentage_pg'],
    json_dict['two_pointers_made_pg'], json_dict['two_pointers_att_pg'], json_dict['two_pointers_percentage_pg'], json_dict['ft_made_pg'],
    json_dict['ft_att_pg'], json_dict['ft_percentage_pg'], json_dict['off_reb_pg'], json_dict['def_reb_pg'], json_dict['total_reb_pg'],
    json_dict['assists_pg'], json_dict['steals_pg'], json_dict['blocks_pg'], json_dict['turn_overs_pg'], json_dict['personal_fouls_pg'],
    json_dict['points_pg'], json_dict['fg_made_p100'], json_dict['fg_att_p100'], json_dict['fg_percentage_p100'], json_dict['three_pointers_made_p100'],
    json_dict['three_pointers_att_p100'], json_dict['three_pointers_percentage_p100'], json_dict['two_pointers_made_p100'],
    json_dict['two_point_att_p100'], json_dict['two_point_percentage_p100'], json_dict['ft_made_p100'], json_dict['ft_att_p100'],
    json_dict['ft_percentage_p100'], json_dict['off_reb_p100'], json_dict['def_reb_p100'], json_dict['total_reb_p100'], json_dict['assists_p100'],
    json_dict['steals_p100'], json_dict['blocks_p100'], json_dict['turn_overs_p100'], json_dict['personal_fouls_p100'], json_dict['points_p100'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""UPDATE nba_team_stats
                    SET team_id = %s, year = %s, games = %s, fg_made = %s, fg_att = %s, fg_percentage = %s, three_pointers_made = %s, 
                    three_pointers_att = %s, three_point_percentage = %s, two_pointers_made = %s, two_point_att = %s, two_point_percentage = %s, 
                    ft_made = %s, ft_att = %s, ft_percentage = %s, off_reb = %s, def_reb = %s, total_reb = %s, assists = %s, steals = %s,
                    blocks = %s, turn_overs = %s, personal_fouls = %s, points = %s, fg_made_pg = %s, fg_att_pg = %s, fg_percentage_pg = %s, 
                    three_pointers_made_pg = %s, three_pointers_att_pg = %s, three_point_percentage_pg = %s, two_pointers_made_pg = %s, 
                    two_point_att_pg = %s, two_point_percentage_pg = %s, ft_made_pg = %s, ft_att_pg = %s, ft_percentage_pg = %s, off_reb_pg = %s, 
                    def_reb_pg = %s, total_reb_pg = %s, assists_pg = %s, steals_pg = %s, blocks_pg = %s, turn_overs_pg = %s, personal_fouls_pg = %s, 
                    points_pg = %s, fg_made_p100 = %s, fg_att_p100 = %s, fg_percentage_p100 = %s, three_pointers_made_p100 = %s, three_pointers_att_p100 = %s,
                    three_point_percentage_p100 = %s, two_pointers_made_p100 = %s, two_point_att_p100 = %s, two_point_percentage_p100 = %s, ft_made_p100 = %s, 
                    ft_att_p100 = %s, ft_percentage_p100 = %s, off_reb_p100 = %s, def_reb_p100 = %s, total_reb_p100 = %s, assists_p100 = %s, 
                    steals_p100 = %s, blocks_p100 = %s, turn_overs_p100 = %s, personal_fouls_p100 = %s, points_p100 = %s""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    return f"nba_team_stats table has been updated with the most recent {json_dict['year']}."


# TEAM STATS AGAINST
@nba.route('/nba/team_stats_against', methods=['POST'])
def nba_add_team_stats_against(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['games'], json_dict['fg_made'], json_dict['fg_att'], json_dict['fg_percentage'],
    json_dict['three_pointers_made'] , json_dict['three_pointers_att'], json_dict['three_pointers_percentage'], json_dict['two_pointers_made'],
    json_dict['two_pointers_att'], json_dict['two_pointers_percentage'], json_dict['ft_made'], json_dict['ft_att'], json_dict['ft_percentage'],
    json_dict['off_reb'], json_dict['def_reb'], json_dict['total_reb'], json_dict['assists'], json_dict['steals'],
    json_dict['blocks'], json_dict['turn_overs'], json_dict['personal_fouls'], json_dict['points'], json_dict['fg_made_pg'], json_dict['fg_att_pg'],
    json_dict['fg_made_percentage'], json_dict['three_pointers_made_pg'], json_dict['three_pointers_att_pg'], json_dict['three_pointers_percentage_pg'],
    json_dict['two_pointers_made_pg'], json_dict['two_pointers_att_pg'], json_dict['two_pointers_percentage_pg'], json_dict['ft_made_pg'],
    json_dict['ft_att_pg'], json_dict['ft_percentage_pg'], json_dict['off_reb_pg'], json_dict['def_reb_pg'], json_dict['total_reb_pg'],
    json_dict['assists_pg'], json_dict['steals_pg'], json_dict['blocks_pg'], json_dict['turn_overs_pg'], json_dict['personal_fouls_pg'],
    json_dict['points_pg'], json_dict['fg_made_p100'], json_dict['fg_att_p100'], json_dict['fg_percentage_p100'], json_dict['three_pointers_made_p100'],
    json_dict['three_pointers_att_p100'], json_dict['three_pointers_percentage_p100'], json_dict['two_pointers_made_p100'],
    json_dict['two_point_att_p100'], json_dict['two_point_percentage_p100'], json_dict['ft_made_p100'], json_dict['ft_att_p100'],
    json_dict['ft_percentage_p100'], json_dict['off_reb_p100'], json_dict['def_reb_p100'], json_dict['total_reb_p100'], json_dict['assists_p100'],
    json_dict['steals_p100'], json_dict['blocks_p100'], json_dict['turn_overs_p100'], json_dict['personal_fouls_p100'], json_dict['points_p100'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""INSERT INTO nba_team_stats_against (team_id, year, games, fg_made, fg_att, fg_percentage, three_pointers_made, three_pointers_att, three_point_percentage, two_pointers_made, two_point_att, two_point_percentage, ft_made, ft_att, ft_percentage, off_reb, def_reb, total_reb, assists, steals, blocks, turn_overs, personal_fouls, points, fg_made_pg, fg_att_pg, fg_percentage_pg, three_pointers_made_pg, three_pointers_att_pg, three_point_percentage_pg, two_pointers_made_pg, two_point_att_pg, two_point_percentage_pg, ft_made_pg, ft_att_pg, ft_percentage_pg, off_reb_pg, def_reb_pg, total_reb_pg, assists_pg, steals_pg, blocks_pg, turn_overs_pg, personal_fouls_pg, points_pg, fg_made_p100, fg_att_p100, fg_percentage_p100, three_pointers_made_p100, three_pointers_att_p100, three_point_percentage_p100, two_pointers_made_p100, two_point_att_p100, two_point_percentage_p100, ft_made_p100, ft_att_p100, ft_percentage_p100, off_reb_p100, def_reb_p100, total_reb_p100, assists_p100, steals_p100, blocks_p100, turn_overs_p100, personal_fouls_p100, points_p100) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
      %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    return f"{json_dict['team_id']}'s {json_dict['year']} data has been added to nba_team_stats table."
@nba.route('/nba/team_stats_against', methods=['PUT'])
def nba_update_team_stats_against(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['games'], json_dict['fg_made'], json_dict['fg_att'], json_dict['fg_percentage'],
    json_dict['three_pointers_made'] , json_dict['three_pointers_att'], json_dict['three_pointers_percentage'], json_dict['two_pointers_made'],
    json_dict['two_pointers_att'], json_dict['two_pointers_percentage'], json_dict['ft_made'], json_dict['ft_att'], json_dict['ft_percentage'],
    json_dict['off_reb'], json_dict['def_reb'], json_dict['total_reb'], json_dict['assists'], json_dict['steals'],
    json_dict['blocks'], json_dict['turn_overs'], json_dict['personal_fouls'], json_dict['points'], json_dict['fg_made_pg'], json_dict['fg_att_pg'],
    json_dict['fg_made_percentage'], json_dict['three_pointers_made_pg'], json_dict['three_pointers_att_pg'], json_dict['three_pointers_percentage_pg'],
    json_dict['two_pointers_made_pg'], json_dict['two_pointers_att_pg'], json_dict['two_pointers_percentage_pg'], json_dict['ft_made_pg'],
    json_dict['ft_att_pg'], json_dict['ft_percentage_pg'], json_dict['off_reb_pg'], json_dict['def_reb_pg'], json_dict['total_reb_pg'],
    json_dict['assists_pg'], json_dict['steals_pg'], json_dict['blocks_pg'], json_dict['turn_overs_pg'], json_dict['personal_fouls_pg'],
    json_dict['points_pg'], json_dict['fg_made_p100'], json_dict['fg_att_p100'], json_dict['fg_percentage_p100'], json_dict['three_pointers_made_p100'],
    json_dict['three_pointers_att_p100'], json_dict['three_pointers_percentage_p100'], json_dict['two_pointers_made_p100'],
    json_dict['two_point_att_p100'], json_dict['two_point_percentage_p100'], json_dict['ft_made_p100'], json_dict['ft_att_p100'],
    json_dict['ft_percentage_p100'], json_dict['off_reb_p100'], json_dict['def_reb_p100'], json_dict['total_reb_p100'], json_dict['assists_p100'],
    json_dict['steals_p100'], json_dict['blocks_p100'], json_dict['turn_overs_p100'], json_dict['personal_fouls_p100'], json_dict['points_p100'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""UPDATE nba_team_stats_against
                    SET team_id = %s, year = %s, games = %s, fg_made = %s, fg_att = %s, fg_percentage = %s, three_pointers_made = %s, 
                    three_pointers_att = %s, three_point_percentage = %s, two_pointers_made = %s, two_point_att = %s, two_point_percentage = %s, 
                    ft_made = %s, ft_att = %s, ft_percentage = %s, off_reb = %s, def_reb = %s, total_reb = %s, assists = %s, steals = %s,
                    blocks = %s, turn_overs = %s, personal_fouls = %s, points = %s, fg_made_pg = %s, fg_att_pg = %s, fg_percentage_pg = %s, 
                    three_pointers_made_pg = %s, three_pointers_att_pg = %s, three_point_percentage_pg = %s, two_pointers_made_pg = %s, 
                    two_point_att_pg = %s, two_point_percentage_pg = %s, ft_made_pg = %s, ft_att_pg = %s, ft_percentage_pg = %s, off_reb_pg = %s, 
                    def_reb_pg = %s, total_reb_pg = %s, assists_pg = %s, steals_pg = %s, blocks_pg = %s, turn_overs_pg = %s, personal_fouls_pg = %s, 
                    points_pg = %s, fg_made_p100 = %s, fg_att_p100 = %s, fg_percentage_p100 = %s, three_pointers_made_p100 = %s, three_pointers_att_p100 = %s,
                    three_point_percentage_p100 = %s, two_pointers_made_p100 = %s, two_point_att_p100 = %s, two_point_percentage_p100 = %s, ft_made_p100 = %s, 
                    ft_att_p100 = %s, ft_percentage_p100 = %s, off_reb_p100 = %s, def_reb_p100 = %s, total_reb_p100 = %s, assists_p100 = %s, 
                    steals_p100 = %s, blocks_p100 = %s, turn_overs_p100 = %s, personal_fouls_p100 = %s, points_p100 = %s""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    return f"nba_team_stats_against table has been updated with the most recent {json_dict['year']}."
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



# NBA STANDINGS ROUTES
@nba.route('/nba/team_standings', methods=['POST'])
def nba_add_team_standings(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['conf_rank'], json_dict['record'], json_dict['win_percentage'],
    json_dict['home_record'], json_dict['away_record'] , json_dict['east_conf_record'], json_dict['west_conf_record'],
    json_dict['pre_allstar_record'], json_dict['post_allstar_record'], json_dict['one_score_game_record'], json_dict['ten_point_game_record'],
    json_dict['oct_record'], json_dict['nov_record'], json_dict['dec_record'], json_dict['jan_record'], json_dict['feb_record'],
    json_dict['mar_record'], json_dict['apr_record'])

    # CONNECT TO THE DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""INSERT INTO nba_standings (team_id, year, conf_rank, record, win_percentage, home_record, away_record , east_conf_record, west_conf_record,
    pre_allstar_record, post_allstar_record, one_score_game_record, ten_point_game_record, oct_record, nov_record, dec_record, jan_record,
    feb_record, mar_record, apr_record) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()

    return f"{json_dict['year']} NBA standings have been added to nba_standings table."
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
@nba.route('/nba/team_standings', methods=['GET'])
def nba_update_team_standings(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['conf_rank'], json_dict['record'], json_dict['win_percentage'],
    json_dict['home_record'], json_dict['away_record'], json_dict['east_conf_record'], json_dict['west_conf_record'],
    json_dict['pre_allstar_record'], json_dict['post_allstar_record'], json_dict['one_score_game_record'], json_dict['ten_point_game_record'],
    json_dict['oct_record'], json_dict['nov_record'], json_dict['dec_record'], json_dict['jan_record'], json_dict['feb_record'],
    json_dict['mar_record'], json_dict['apr_record'])

    # CONNECT TO THE DB
    connection = create_connection()
    cursor = connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""UPDATE nba_standings 
                    SET team_id = %s, year = %s, conf_rank = %s, record = %s, win_percentage = %s, home_record = %s, away_record = %s, 
                    east_conf_record = %s, west_conf_record = %s, pre_allstar_record = %s, post_allstar_record = %s, 
                    one_score_game_record = %s, ten_point_game_record = %s, oct_record = %s, nov_record = %s, dec_record = %s, 
                    jan_record = %s, feb_record = %s, mar_record = %s, apr_record = %s""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()

    return f"nba_standings table has been updated with the most recent {json_dict['year']} data."


# PLAYER_DATA
@nba.route('/nba/player_stats', methods=['POST'])
def nba_add_player_data(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['game_id'], json_dict['year'], json_dict['date'], json_dict['team_id'], json_dict['opponent'], json_dict['player_id'],
    json_dict['mp'], json_dict['fg_made'], json_dict['fg_att'], json_dict['fg_percentage'], json_dict['threes_made'], json_dict['threes_att'],
    json_dict['threes_percentage'], json_dict['ft_made'], json_dict['ft_att'], json_dict['ft_percentage'], json_dict['off_reb'],
    json_dict['def_reb'], json_dict['total_reb'], json_dict['assists'], json_dict['steals'], json_dict['blocks'], json_dict['turnover'],
    json_dict['personal_fouls'], json_dict['points'],  json_dict['plus_minus'], json_dict['off_reb_percent'], json_dict['def_reb_percent'],
    json_dict['total_reb_percent'], json_dict['assists_percent'], json_dict['steals_percent'], json_dict['blocks_percent'],
    json_dict['turnover_percent'], json_dict['off_rating'], json_dict['def_rating'], json_dict['usage_rate'])

    # CONNECT TO THE DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""INSERT INTO nba_player_stats (game_id, year, date, team_id, opponent, player_id, mp, fg_made, fg_att, fg_percentage, threes_made, threes_att, threes_percentage, ft_made, ft_att, ft_percentage, off_reb, def_reb, total_reb, assists, steals, blocks, turnover, personal_fouls, points, plus_minus, off_reb_percent, def_reb_percent, total_reb_percent, assists_percent, steals_percent, blocks_percent, turnover_percent, off_rating, def_rating, usage_rate)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()

    return f"{json_dict['player_id']} on {json_dict['date']} has been added to nba_player_stats table."
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

