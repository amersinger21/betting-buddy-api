from .db import create_connection
from flask import Blueprint, request

import json

mlb = Blueprint("mlb", __name__)


@mlb.route('/mlb/games', methods=['POST'])

def mlb_add_game(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['year'], json_dict['date'], json_dict['day_of_the_week'], json_dict['away_team_id'], json_dict['away_score'],
              json_dict['home_team_id'], json_dict['home_score'], json_dict['margin_of_victory'], json_dict['total_runs'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("INSERT INTO mlb_games (year, date, day_of_the_week, away_team_id, away_score, home_team_id, home_score, margin_of_victory, total_runs)"
                   " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    print(f"Game has been added to mlb_games tabel.")
@mlb.route('/mlb/games', methods=['GET'])

def mlb_get_games():
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
    cursor.execute('''SELECT team_h.name AS home_name, team_a.name AS away_name, mlb_g.*
                      FROM mlb_games AS mlb_g
                      LEFT JOIN team AS team_h ON team_h.id = mlb_g.home_team_id
                      LEFT JOIN team AS team_a ON team_a.id = mlb_g.away_team_id
                      WHERE home_team_id = %s OR away_team_id = %s
                      LIMIT 0, %s''',
                   [team_id, team_id, number])
    results = list(cursor.fetchall())

    # LOOP THROUGH RESULTS TO CREATE JSON DOCUMENT
    result_list = []
    for result in results:
        player_dict = {'id': result[2], 'year': result[3], 'date': result[4], 'day_of_the_week': result[5], 'away_team': result[1],
                       'away_score': result[7], 'home_team': result[0], 'home_score': result[9], 'margin_of_victory': result[10],
                       'total_runs': result[11]}
        result_list.append(player_dict)
    final = json.dumps(result_list, indent=2)
    return final
@mlb.route('/mlb/games_vs_opponent', methods=['GET'])

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
    cursor.execute('''SELECT team_h.name AS home_name, team_a.name AS away_name, mlb_g.*
                      FROM mlb_games AS mlb_g
                      LEFT JOIN team AS team_h ON team_h.id = mlb_g.home_team_id
                      LEFT JOIN team AS team_a ON team_a.id = mlb_g.away_team_id
                      WHERE (home_team_id = %s OR away_team_id = %s) AND (home_team_id = %s OR away_team_id = %s)
                      LIMIT 0, %s''',
                   [team_id, team_id, opp_id, opp_id, number])
    results = list(cursor.fetchall())
    # return results

    # LOOP THROUGH RESULTS TO CREATE JSON DOCUMENT
    result_list = []
    for result in results:
        player_dict = {'id': result[2], 'year': result[3], 'date': result[4], 'day_of_the_week': result[5],
                       'away_team': result[1],
                       'away_score': result[7], 'home_team': result[0], 'home_score': result[9],
                       'margin_of_victory': result[10],
                       'total_runs': result[11]}
        result_list.append(player_dict)
    return result_list


@mlb.route('/mlb/team_batting', methods=['POST'])

def mlb_add_team_batting(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['avg_batter_age'], json_dict['runs_scored_per_game'],
    json_dict['plate_appearances'], json_dict['runs_scored'], json_dict['hits'], json_dict['doubles'], json_dict['triples'],
    json_dict['homeruns'], json_dict['runs_batted_in'], json_dict['stolen_bases'], json_dict['caught_stealing'], json_dict['stolen_base_percent'],
    json_dict['walks'], json_dict['strikeouts'], json_dict['batting_average'], json_dict['on_base_percentage'], json_dict['slugging_percentage'],
    json_dict['on_base_plus_slugging'], json_dict['ops_plus'], json_dict['total_bases'], json_dict['babip'], json_dict['iso'], json_dict['home_run_percentage'], json_dict['strikeout_percentage'],
    json_dict['walks_percentage'], json_dict['avg_exit_velocity'], json_dict['hard_hit_rate'], json_dict['line_drive_rate'],
    json_dict['ground_ball_rate'], json_dict['fly_ball_rate'], json_dict['ground_ball_fly_ball_ratio'],
    json_dict['pull_percentage'], json_dict['center_percentage'], json_dict['opp_percentage'], json_dict['at_bats_per_strikeout'],
    json_dict['at_bats_per_homerun'], json_dict['at_bats_per_rbi'], json_dict['strikeout_to_walk_ratio'], json_dict['extra_base_hit_percentage'],
    json_dict['fly_ball_homerun_rate'], json_dict['homeruns_vs_left'], json_dict['homeruns_vs_right'], json_dict['win_prob_added'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("INSERT INTO mlb_team_batting (team_id, year, avg_batter_age, runs_scored_per_game, plate_appearances, runs_scored, hits, doubles, triples, homeruns, runs_batted_in, stolen_bases, caught_stealing, stolen_base_percent, walks, strikeouts, batting_average, on_base_percentage, slugging_percentage, on_base_plus_slugging, ops_plus, total_bases, babip, iso, home_run_percentage, strikeout_percentage, walks_percentage, avg_exit_velocity, hard_hit_rate, line_drive_rate, ground_ball_rate, fly_ball_rate, ground_ball_fly_ball_ratio, pull_percentage, center_percentage, opp_percentage, at_bats_per_strikeout, at_bats_per_homerun, at_bats_per_rbi, strikeout_to_walk_ratio, extra_base_hit_percentage, fly_ball_homerun_rate, homeruns_vs_left, homeruns_vs_right, win_prob_added)"
                   " VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')",
                   (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    print(f"Game has been added to mlb_games tabel.")

@mlb.route('/mlb/team_batting', methods=['PUT'])

def mlb_update_team_batting(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['avg_batter_age'], json_dict['runs_scored_per_game'],
    json_dict['plate_appearances'], json_dict['runs_scored'], json_dict['hits'], json_dict['doubles'], json_dict['triples'],
    json_dict['homeruns'], json_dict['runs_batted_in'], json_dict['stolen_bases'], json_dict['caught_stealing'], json_dict['stolen_base_percent'],
    json_dict['walks'], json_dict['strikeouts'], json_dict['batting_average'], json_dict['on_base_percentage'], json_dict['slugging_percentage'],
    json_dict['on_base_plus_slugging'], json_dict['league_batting_avg'], json_dict['total_bases'], json_dict['league_on_base'],
    json_dict['league_slg'], json_dict['babip'], json_dict['iso'], json_dict['home_run_percentage'], json_dict['strikeout_percentage'],
    json_dict['walks_percentage'], json_dict['avg_exit_velocity'], json_dict['hard_hit_rate'], json_dict['line_drive_rate'],
    json_dict['ground_ball_rate'], json_dict['fly_ball_rate'], json_dict['ground_ball_fly_ball_ratio'],
    json_dict['pull_percentage'], json_dict['center_percentage'], json_dict['opp_percentage'], json_dict['at_bats_per_strikeout'],
    json_dict['at_bats_per_homerun'], json_dict['at_bats_per_rbi'], json_dict['strikeout_to_walk_ratio'], json_dict['extra_base_hit_percentage'],
    json_dict['fly_ball_homerun_rate'], json_dict['homeruns_vs_left'], json_dict['homeruns_vs_right'], json_dict['win_prob_added'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("""UPDATE mlb_team_batting
                      SET team_id = %s, year = %s, avg_batter_age = %s, runs_scored_per_game = %s, plate_appearances = %s, 
                      runs_scored = %s, hits = %s, doubles = %s, triples = %s, homeruns = %s, runs_batted_in = %s, stolen_bases = %s, 
                      caught_stealing = %s, stolen_base_percent = %s, walks = %s, strikeouts = %s, batting_average = %s, 
                      on_base_percentage = %s, slugging_percentage = %s, on_base_plus_slugging = %s, ops_plus = %s, total_bases = %s, 
                      babip = %s, iso = %s,  home_run_percentage = %s, strikeout_percentage = %s, walks_percentage = %s, avg_exit_velocity = %s, 
                      hard_hit_rate = %s, line_drive_rate = %s, ground_ball_rate = %s, fly_ball_rate = %s, ground_ball_fly_ball_ratio = %s,
                      pull_percentage = %s, center_percentage = %s, opp_percentage = %s, at_bats_per_strikeout = %s, at_bats_per_homerun = %s, 
                      at_bats_per_rbi = %s, strikeout_to_walk_ratio = %s, extra_base_hit_percentage = %s, fly_ball_homerun_rate = %s, 
                      homeruns_vs_left = %s, homeruns_vs_right = %s, win_prob_added = %s)""",(values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    return f"mlb_team_batting table has been updated with most recent data."
@mlb.route('/mlb/team_batting')
def mlb_get_team_batting():
    team_id = request.args.get('id', None)
    year = request.args.get('year', None)

    connection = create_connection()
    cursor = connection.cursor()
    print(f"team_id = {team_id}")

    query = f'''SELECT team.name, mlb_team_batting.*
                FROM mlb_team_batting
                JOIN team ON team.id = mlb_team_batting.team_id
                WHERE team.id = %s AND mlb_team_batting.year = %s'''
    vals = [team_id, year]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())
    # return results
    output = []
    for result in results:
        item = {'name': result[0], 'id': result[1], 'team_id': result[2], 'year': result[3], 'avg_batter_age': result[4], 'runs_scored_per_game': result[5],
                'plate_appearances': result[6], 'runs_scored': result[7], 'hits': result[8], 'doubles': result[9], 'triples': result[10],
                'homeruns': result[11], 'runs_batted_in': result[12], 'stolen_bases': result[13], 'caught_stealing': result[14], 'stolen_base_percent': result[15],
                'walks': result[16], 'strikeouts': result[17], 'batting_average': result[18], 'on_base_percentage': result[19],
                'slugging_percentage': result[20], 'on_base_plus_slugging': result[21], 'ops_plus': result[22], 'total_bases': result[23],
                'babip': result[24], 'iso': result[25], 'home_run_percentage': result[26],
                'strikeout_percentage': result[27], 'walks_percentage': result[28], 'avg_exit_velocity': result[29], 'hard_hit_rate': result[30], 'line_drive_rate': result[31],
                'ground_ball_rate': result[32], 'fly_ball_rate': result[33], 'ground_ball_fly_ball_ratio': result[34], 'pull_percentage': result[35],
                'center_percentage': result[36], 'opp_percentage': result[37], 'at_bats_per_strikeout': result[38], 'at_bats_per_homerun': result[39],
                'at_bats_per_rbi': result[40], 'strikeout_to_walk_ratio': result[41], 'extra_base_hit_percentage': result[42],
                'fly_ball_homerun_rate': result[43], 'homeruns_vs_left': result[44], 'homeruns_vs_right': result[45], 'win_prob_added': result[46]}

        if item not in output:
            output.append(item)

    return output


@mlb.route('/mlb/team_pitching', methods=['POST'])
def mlb_add_team_pitching(json_dict):
    #  CREATE A TUPLE OF ALL VALUES TO RUN THROUGH SQL QUERY
    values = (json_dict['team_id'], json_dict['year'], json_dict['avg_pitcher_age'], json_dict['runs_allowed_game'],
    json_dict['earned_run_avg'], json_dict['innings_pitches'], json_dict['hits_allowed'], json_dict['doubles_allowed'], json_dict['triples_allowed'],
    json_dict['home_runs_allowed'], json_dict['steals_allowed'], json_dict['total_bases_allowed'], json_dict['runs_allowed'], json_dict['earned_runs'],
    json_dict['walks_allowed'], json_dict['strikeouts'], json_dict['earned_runs_plus'], json_dict['fip'], json_dict['whip'],
    json_dict['hits_per_nine'], json_dict['home_runs_per_nine'], json_dict['walks_per_nine'], json_dict['strikeouts_per_nine'],
    json_dict['strikeouts_per_walk'], json_dict['runners_left_on_base'], json_dict['batting_avg_against'], json_dict['on_base_percent_allowed'],
    json_dict['slugging_percent_against'], json_dict['ops_allowed'], json_dict['babip_allowed'], json_dict['home_run_allowed_percent'],
    json_dict['strikeout_percentage'], json_dict['walk_allowed_percentage'], json_dict['avg_exit_velocity'], json_dict['hard_hit_rate'],
    json_dict['line_drive_rate'], json_dict['ground_ball_rate'], json_dict['fly_ball_rate'], json_dict['ground_ball_fly_ball_ratio'],
    json_dict['win_probability_added'], json_dict['fly_ball_home_run_percent'], json_dict['extra_base_percentage'])

    # CONNECT TO DB
    connection = create_connection()
    cursor=connection.cursor()

    # EXECUTE SQL TO ADD DATA TO TABLE
    cursor.execute("INSERT INTO mlb_team_pitching (team_id, year, avg_pitcher_age, runs_allowed_game, earned_run_avg, innings_pitches, hits_allowed, doubles_allowed, triples_allowed, home_runs_allowed, steals_allowed, total_bases_allowed, runs_allowed, earned_runs, walks_allowed, strikeouts, earned_runs_plus, fip, whip, hits_per_nine, home_runs_per_nine, walks_per_nine, strikeouts_per_nine, strikeouts_per_walk, runners_left_on_base, batting_avg_against, on_base_percent_allowed, slugging_percent_against, ops_allowed, babip_allowed, home_run_allowed_percent, strikeout_percentage, walk_allowed_percentage, avg_exit_velocity, hard_hit_rate, line_drive_rate, ground_ball_rate, fly_ball_rate, ground_ball_fly_ball_ratio, win_probability_added, fly_ball_home_run_percent, extra_base_percentage)"
                   " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (values))

    # COMMIT/SAVE CHANGES TO DB
    connection.commit()
    print(f"Game has been added to mlb_games tabel.")