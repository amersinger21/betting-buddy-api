from scripts.db import create_connection
from flask import Blueprint

nba = Blueprint("nba", __name__)

# NBA standings routes
@nba.route('/nba/team_standings', methods=['POST'])
def nba_add_team_standings(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['record'], json_dict['win_percentage'],
    json_dict['home_record'], json_dict['away_record'] , json_dict['east_conf_record'], json_dict['west_conf_record'],
    json_dict['pre_allstar_record'], json_dict['post_allstar_record'], json_dict['one_score_game_record'], json_dict['ten_point_game_record'],
    json_dict['oct_record'], json_dict['nov_record'], json_dict['dec_record'], json_dict['jan_record'], json_dict['feb_record'],
    json_dict['mar_record'], json_dict['apr_record'])

    # CONNECT TO THE DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""INSERT INTO nba_standings (team_id, year, record, win_percentage, home_record, away_record , east_conf_record, west_conf_record,
    pre_allstar_record, post_allstar_record, one_score_game_record, ten_point_game_record, oct_record, nov_record, dec_record, jan_record,
    feb_record, mar_record, apr_record) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()

    return f"{json_dict['year']} NBA standings have been added to nba_standings table."
@nba.route('/nba/team_standings', methods=['GET'])
def nba_update_team_standings(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['record'], json_dict['win_percentage'], json_dict['home_record'], json_dict['away_record'],
              json_dict['east_conf_record'], json_dict['west_conf_record'], json_dict['pre_allstar_record'],
              json_dict['post_allstar_record'], json_dict['one_score_game_record'], json_dict['ten_point_game_record'],
              json_dict['oct_record'], json_dict['nov_record'], json_dict['dec_record'], json_dict['jan_record'],
              json_dict['feb_record'], json_dict['mar_record'], json_dict['apr_record'], json_dict['team_id'], json_dict['year'])

    # CONNECT TO THE DB
    connection = create_connection()
    cursor = connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""UPDATE nba_standings 
                    SET record = %s, win_percentage = %s, home_record = %s, away_record = %s, 
                    east_conf_record = %s, west_conf_record = %s, pre_allstar_record = %s, post_allstar_record = %s, 
                    one_score_game_record = %s, ten_point_game_record = %s, oct_record = %s, nov_record = %s, dec_record = %s, 
                    jan_record = %s, feb_record = %s, mar_record = %s, apr_record = %s
                    WHERE nba_standings.team_id = %s AND nba_standings.year = %s""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()

    return f"nba_standings table has been updated with the most recent {json_dict['year']} data."


# NBA game routes
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
def nba_update_game(json_dict):
    values = (json_dict['year'], json_dict['date'], json_dict['day_of_the_week'], json_dict['start_time'], json_dict['away_team_id'],
              json_dict['away_score'], json_dict['home_team_id'], json_dict['home_score'], json_dict['margin_of_victory'])

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute('''UPDATE nfl_games 
             SET year = %s, date = %s, day_of_the_week = %s, start_time = %s, away_team_id = %s, away_score = %s, home_team_id = %s, 
             home_score = %s, margin_of_victory = %s''', (values))
    connection.commit()

    return "nba_games table has been updated."


# NBA team stats
@nba.route('/nba/team_stats', methods=['PUT'])
def nba_update_team_stats(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['games'], json_dict['fg_made'], json_dict['fg_att'], json_dict['fg_percentage'],
    json_dict['three_point_made'] , json_dict['three_point_att'], json_dict['three_point_percentage'], json_dict['two_point_made'],
    json_dict['two_point_att'], json_dict['two_point_percentage'], json_dict['ft_made'], json_dict['ft_att'], json_dict['ft_percentage'],
    json_dict['off_reb'], json_dict['def_reb'], json_dict['total_reb'], json_dict['assists'], json_dict['steals'],
    json_dict['blocks'], json_dict['turn_overs'], json_dict['personal_fouls'], json_dict['points'], json_dict['fg_made_pg'], json_dict['fg_att_pg'],
    json_dict['fg_percentage_pg'], json_dict['three_point_made_pg'], json_dict['three_point_att_pg'], json_dict['three_point_percentage_pg'],
    json_dict['two_point_made_pg'], json_dict['two_point_att_pg'], json_dict['two_point_percentage_pg'], json_dict['ft_made_pg'],
    json_dict['ft_att_pg'], json_dict['ft_percentage_pg'], json_dict['off_reb_pg'], json_dict['def_reb_pg'], json_dict['total_reb_pg'],
    json_dict['assists_pg'], json_dict['steals_pg'], json_dict['blocks_pg'], json_dict['turn_overs_pg'], json_dict['personal_fouls_pg'],
    json_dict['points_pg'], json_dict['fg_made_p100'], json_dict['fg_att_p100'], json_dict['fg_percentage_p100'], json_dict['three_point_made_p100'],
    json_dict['three_point_att_p100'], json_dict['three_point_percentage_p100'], json_dict['two_point_made_p100'],
    json_dict['two_point_att_p100'], json_dict['two_point_percentage_p100'], json_dict['ft_made_p100'], json_dict['ft_att_p100'],
    json_dict['ft_percentage_p100'], json_dict['off_reb_p100'], json_dict['def_reb_p100'], json_dict['total_reb_p100'], json_dict['assists_p100'],
    json_dict['steals_p100'], json_dict['blocks_p100'], json_dict['turn_overs_p100'], json_dict['personal_fouls_p100'], json_dict['points_p100'],
    json_dict['team_id'], json_dict['year'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""UPDATE nba_team_offense
                    SET games = %s, fg_made = %s, fg_att = %s, fg_percentage = %s, three_point_made = %s, 
                    three_point_att = %s, three_point_percentage = %s, two_point_made = %s, two_point_att = %s, two_point_percentage = %s, 
                    ft_made = %s, ft_att = %s, ft_percentage = %s, off_reb = %s, def_reb = %s, total_reb = %s, assists = %s, steals = %s,
                    blocks = %s, turn_overs = %s, personal_fouls = %s, points = %s, fg_made_pg = %s, fg_att_pg = %s, fg_percentage_pg = %s, 
                    three_point_made_pg = %s, three_point_att_pg = %s, three_point_percentage_pg = %s, two_point_made_pg = %s, 
                    two_point_att_pg = %s, two_point_percentage_pg = %s, ft_made_pg = %s, ft_att_pg = %s, ft_percentage_pg = %s, off_reb_pg = %s, 
                    def_reb_pg = %s, total_reb_pg = %s, assists_pg = %s, steals_pg = %s, blocks_pg = %s, turn_overs_pg = %s, personal_fouls_pg = %s, 
                    points_pg = %s, fg_made_p100 = %s, fg_att_p100 = %s, fg_percentage_p100 = %s, three_point_made_p100 = %s, three_point_att_p100 = %s,
                    three_point_percentage_p100 = %s, two_point_made_p100 = %s, two_point_att_p100 = %s, two_point_percentage_p100 = %s, ft_made_p100 = %s, 
                    ft_att_p100 = %s, ft_percentage_p100 = %s, off_reb_p100 = %s, def_reb_p100 = %s, total_reb_p100 = %s, assists_p100 = %s, 
                    steals_p100 = %s, blocks_p100 = %s, turn_overs_p100 = %s, personal_fouls_p100 = %s, points_p100 = %s
                    WHERE team_id = %s AND year = %s""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    return f"nba_team_stats table has been updated with the most recent {json_dict['year']}."
@nba.route('/nba/team_stats', methods=['POST'])
def nba_add_team_stats(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['games'], json_dict['fg_made'], json_dict['fg_att'], json_dict['fg_percentage'],
              json_dict['three_point_made'], json_dict['three_point_att'], json_dict['three_point_percentage'], json_dict['two_point_made'],
              json_dict['two_point_att'], json_dict['two_point_percentage'], json_dict['ft_made'], json_dict['ft_att'], json_dict['ft_percentage'],
              json_dict['off_reb'], json_dict['def_reb'], json_dict['total_reb'], json_dict['assists'], json_dict['steals'], json_dict['blocks'],
              json_dict['turn_overs'], json_dict['personal_fouls'], json_dict['points'], json_dict['fg_made_pg'],  json_dict['fg_att_pg'],
              json_dict['fg_percentage_pg'], json_dict['three_point_made_pg'], json_dict['three_point_att_pg'], json_dict['three_point_percentage_pg'],
              json_dict['two_point_made_pg'], json_dict['two_point_att_pg'], json_dict['two_point_percentage_pg'], json_dict['ft_made_pg'],
              json_dict['ft_att_pg'], json_dict['ft_percentage_pg'], json_dict['off_reb_pg'], json_dict['def_reb_pg'],  json_dict['total_reb_pg'],
              json_dict['assists_pg'], json_dict['steals_pg'], json_dict['blocks_pg'], json_dict['turn_overs_pg'], json_dict['personal_fouls_pg'],
              json_dict['points_pg'], json_dict['fg_made_p100'], json_dict['fg_att_p100'], json_dict['fg_percentage_p100'],
              json_dict['three_point_made_p100'], json_dict['three_point_att_p100'], json_dict['three_point_percentage_p100'],
              json_dict['two_point_made_p100'], json_dict['two_point_att_p100'], json_dict['two_point_percentage_p100'], json_dict['ft_made_p100'],
              json_dict['ft_att_p100'], json_dict['ft_percentage_p100'], json_dict['off_reb_p100'], json_dict['def_reb_p100'],
              json_dict['total_reb_p100'], json_dict['assists_p100'], json_dict['steals_p100'], json_dict['blocks_p100'],
              json_dict['turn_overs_p100'], json_dict['personal_fouls_p100'], json_dict['points_p100'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""INSERT INTO nba_team_offense (team_id, year, games, fg_made, fg_att, fg_percentage, three_point_made, three_point_att, three_point_percentage, two_point_made, two_point_att, two_point_percentage, ft_made, ft_att, ft_percentage, off_reb, def_reb, total_reb, assists, steals, blocks, turn_overs, personal_fouls, points, fg_made_pg, fg_att_pg, fg_percentage_pg, three_point_made_pg, three_point_att_pg, three_point_percentage_pg, two_point_made_pg, two_point_att_pg, two_point_percentage_pg, ft_made_pg, ft_att_pg, ft_percentage_pg, off_reb_pg, def_reb_pg, total_reb_pg, assists_pg, steals_pg, blocks_pg, turn_overs_pg, personal_fouls_pg, points_pg, fg_made_p100, fg_att_p100, fg_percentage_p100, three_point_made_p100, three_point_att_p100, three_point_percentage_p100, two_point_made_p100, two_point_att_p100, two_point_percentage_p100, ft_made_p100, ft_att_p100, ft_percentage_p100, off_reb_p100, def_reb_p100, total_reb_p100, assists_p100, steals_p100, blocks_p100, turn_overs_p100, personal_fouls_p100, points_p100) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
      %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    return f"{json_dict['team_id']}'s {json_dict['year']} data has been added to nba_team_stats table."



# NBA team stats against
@nba.route('/nba/team_stats_against', methods=['POST'])
def nba_add_team_stats_against(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['games'], json_dict['fg_made'], json_dict['fg_att'], json_dict['fg_percentage'],
    json_dict['three_point_made'] , json_dict['three_point_att'], json_dict['three_point_percentage'], json_dict['two_point_made'],
    json_dict['two_point_att'], json_dict['two_point_percentage'], json_dict['ft_made'], json_dict['ft_att'], json_dict['ft_percentage'],
    json_dict['off_reb'], json_dict['def_reb'], json_dict['total_reb'], json_dict['assists'], json_dict['steals'],
    json_dict['blocks'], json_dict['turn_overs'], json_dict['personal_fouls'], json_dict['points'], json_dict['fg_made_pg'], json_dict['fg_att_pg'],
    json_dict['fg_percentage_pg'], json_dict['three_point_made_pg'], json_dict['three_point_att_pg'], json_dict['three_point_percentage_pg'],
    json_dict['two_point_made_pg'], json_dict['two_point_att_pg'], json_dict['two_point_percentage_pg'], json_dict['ft_made_pg'],
    json_dict['ft_att_pg'], json_dict['ft_percentage_pg'], json_dict['off_reb_pg'], json_dict['def_reb_pg'], json_dict['total_reb_pg'],
    json_dict['assists_pg'], json_dict['steals_pg'], json_dict['blocks_pg'], json_dict['turn_overs_pg'], json_dict['personal_fouls_pg'],
    json_dict['points_pg'], json_dict['fg_made_p100'], json_dict['fg_att_p100'], json_dict['fg_percentage_p100'], json_dict['three_point_made_p100'],
    json_dict['three_point_att_p100'], json_dict['three_point_percentage_p100'], json_dict['two_point_made_p100'],
    json_dict['two_point_att_p100'], json_dict['two_point_percentage_p100'], json_dict['ft_made_p100'], json_dict['ft_att_p100'],
    json_dict['ft_percentage_p100'], json_dict['off_reb_p100'], json_dict['def_reb_p100'], json_dict['total_reb_p100'], json_dict['assists_p100'],
    json_dict['steals_p100'], json_dict['blocks_p100'], json_dict['turn_overs_p100'], json_dict['personal_fouls_p100'], json_dict['points_p100'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""INSERT INTO nba_team_defense (team_id, year, games, fg_made, fg_att, fg_percentage, three_point_made, three_point_att, three_point_percentage, two_point_made, two_point_att, two_point_percentage, ft_made, ft_att, ft_percentage, off_reb, def_reb, total_reb, assists, steals, blocks, turn_overs, personal_fouls, points, fg_made_pg, fg_att_pg, fg_percentage_pg, three_point_made_pg, three_point_att_pg, three_point_percentage_pg, two_point_made_pg, two_point_att_pg, two_point_percentage_pg, ft_made_pg, ft_att_pg, ft_percentage_pg, off_reb_pg, def_reb_pg, total_reb_pg, assists_pg, steals_pg, blocks_pg, turn_overs_pg, personal_fouls_pg, points_pg, fg_made_p100, fg_att_p100, fg_percentage_p100, three_point_made_p100, three_point_att_p100, three_point_percentage_p100, two_point_made_p100, two_point_att_p100, two_point_percentage_p100, ft_made_p100, ft_att_p100, ft_percentage_p100, off_reb_p100, def_reb_p100, total_reb_p100, assists_p100, steals_p100, blocks_p100, turn_overs_p100, personal_fouls_p100, points_p100) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
      %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    return f"{json_dict['team_id']}'s {json_dict['year']} data has been added to nba_team_stats table."
@nba.route('/nba/team_stats_against', methods=['PUT'])
def nba_update_team_stats_against(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['games'], json_dict['fg_made'], json_dict['fg_att'], json_dict['fg_percentage'],
    json_dict['three_point_made'] , json_dict['three_point_att'], json_dict['three_point_percentage'], json_dict['two_point_made'],
    json_dict['two_point_att'], json_dict['two_point_percentage'], json_dict['ft_made'], json_dict['ft_att'], json_dict['ft_percentage'],
    json_dict['off_reb'], json_dict['def_reb'], json_dict['total_reb'], json_dict['assists'], json_dict['steals'],
    json_dict['blocks'], json_dict['turn_overs'], json_dict['personal_fouls'], json_dict['points'], json_dict['fg_made_pg'], json_dict['fg_att_pg'],
    json_dict['fg_percentage_pg'], json_dict['three_point_made_pg'], json_dict['three_point_att_pg'], json_dict['three_point_percentage_pg'],
    json_dict['two_point_made_pg'], json_dict['two_point_att_pg'], json_dict['two_point_percentage_pg'], json_dict['ft_made_pg'],
    json_dict['ft_att_pg'], json_dict['ft_percentage_pg'], json_dict['off_reb_pg'], json_dict['def_reb_pg'], json_dict['total_reb_pg'],
    json_dict['assists_pg'], json_dict['steals_pg'], json_dict['blocks_pg'], json_dict['turn_overs_pg'], json_dict['personal_fouls_pg'],
    json_dict['points_pg'], json_dict['fg_made_p100'], json_dict['fg_att_p100'], json_dict['fg_percentage_p100'], json_dict['three_point_made_p100'],
    json_dict['three_point_att_p100'], json_dict['three_point_percentage_p100'], json_dict['two_point_made_p100'],
    json_dict['two_point_att_p100'], json_dict['two_point_percentage_p100'], json_dict['ft_made_p100'], json_dict['ft_att_p100'],
    json_dict['ft_percentage_p100'], json_dict['off_reb_p100'], json_dict['def_reb_p100'], json_dict['total_reb_p100'], json_dict['assists_p100'],
    json_dict['steals_p100'], json_dict['blocks_p100'], json_dict['turn_overs_p100'], json_dict['personal_fouls_p100'], json_dict['points_p100'],
    json_dict['team_id'], json_dict['year'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""UPDATE nba_team_defense
                    SET games = %s, fg_made = %s, fg_att = %s, fg_percentage = %s, three_point_made = %s, 
                    three_point_att = %s, three_point_percentage = %s, two_point_made = %s, two_point_att = %s, two_point_percentage = %s, 
                    ft_made = %s, ft_att = %s, ft_percentage = %s, off_reb = %s, def_reb = %s, total_reb = %s, assists = %s, steals = %s,
                    blocks = %s, turn_overs = %s, personal_fouls = %s, points = %s, fg_made_pg = %s, fg_att_pg = %s, fg_percentage_pg = %s, 
                    three_point_made_pg = %s, three_point_att_pg = %s, three_point_percentage_pg = %s, two_point_made_pg = %s, 
                    two_point_att_pg = %s, two_point_percentage_pg = %s, ft_made_pg = %s, ft_att_pg = %s, ft_percentage_pg = %s, off_reb_pg = %s, 
                    def_reb_pg = %s, total_reb_pg = %s, assists_pg = %s, steals_pg = %s, blocks_pg = %s, turn_overs_pg = %s, personal_fouls_pg = %s, 
                    points_pg = %s, fg_made_p100 = %s, fg_att_p100 = %s, fg_percentage_p100 = %s, three_point_made_p100 = %s, three_point_att_p100 = %s,
                    three_point_percentage_p100 = %s, two_point_made_p100 = %s, two_point_att_p100 = %s, two_point_percentage_p100 = %s, ft_made_p100 = %s, 
                    ft_att_p100 = %s, ft_percentage_p100 = %s, off_reb_p100 = %s, def_reb_p100 = %s, total_reb_p100 = %s, assists_p100 = %s, 
                    steals_p100 = %s, blocks_p100 = %s, turn_overs_p100 = %s, personal_fouls_p100 = %s, points_p100 = %s
                    WHERE team_id = %s AND year = %s""", (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    return f"nba_team_defense table has been updated with the most recent {json_dict['year']}."


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