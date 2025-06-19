from .db import create_connection
from flask import Blueprint, request
import flask
import pandas as pd


mlb = Blueprint("mlb", __name__)


# UPLOAD [PUT/POST] ROUTES
@mlb.route('/mlb/games', methods=['POST'])
def mlb_game_info():
    # Initialize variables
    file = request.files['mlb_game_info']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        # Connect to DB
        connection = create_connection()
        cursor = connection.cursor()

        json_dict = {'year': int(row['year']),
                     'date': row['date'],
                     'day_of_the_week': row['day_of_the_week'],
                     'away_team_id': int(row['away_team_id']),
                     'away_score ': int(row['away_score']),
                     'home_team_id': int(row['home_team_id']),
                     'home_score': int(row['home_score']),
                     'margin_of_victory': int(row['margin_of_victory']),
                     'total_runs': int(row['total_runs'])}
        values = list(json_dict.values())

        # SQL Query
        cursor.execute('''INSERT INTO mlb_games (year, date, day_of_the_week, away_team_id, away_score, home_team_id,
        home_score, margin_of_victory, total_runs) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', (values))

        # Commit changes
        connection.commit()

    return f"mlb_games table has been updated with the most recent game data."


@mlb.route('/mlb/player_stats', methods=['POST'])
def mlb_player_stats():
    run_stat = request.args.get('stat', None)
    # Initialize variables
    bat_file = request.files['mlb_batting_log']
    pitch_file = request.files['mlb_pitching_log']

    # Read CSV data
    df_bat = pd.read_csv(bat_file)
    df_pitch = pd.read_csv(pitch_file)

    # BATTING DATA
    if run_stat == 'batting':
        for ind, row in df_bat.iterrows():
            # Connect to DB
            connection = create_connection()
            cursor = connection.cursor()

            json_dict = {'year': int(row['year']),
                         'month': row['month'],
                         'game_id': int(row['game_id']),
                         'player_id': int(row['player_id']),
                         'team_id': int(row['team_id']),
                         'opp_id': int(row['opp_id']),
                         'at_bats': int(row['at_bats']),
                         'runs': int(row['runs']),
                         'hits': int(row['hits']),
                         'runs_batted_in': int(row['runs_batted_in']),
                         'walks': int(row['walks']),
                         'strikeouts': int(row['strikeouts']),
                         'batting_avg': float(row['batting_avg']),
                         'on_base_percentage': float(row['on_base_percentage']),
                         'slugging_percentage': float(row['slugging_percentage']),
                         'on_base_plus_slug_percentage': float(row['on_base_plus_slug_percentage']),
                         'doubles': int(row['doubles']),
                         'triples': int(row['triples']),
                         'homeruns': int(row['homeruns']),
                         'total_bases': int(row['total_bases']),
                         'stolen_bases': int(row['stolen_bases']),
                         'caught_stealing': int(row['caught_stealing']),
                         'stolen_base_percentage': float(row['stolen_base_percentage'])}
            values = list(json_dict.values())

            # SQL Query
            cursor.execute("""INSERT INTO mlb_player_batting (year, month, game_id, player_id, team_id, opp_id, at_bats, runs, hits,
             runs_batted_in, walks, strikeouts, batting_avg, on_base_percentage, slugging_percentage, on_base_plus_slug_percentage, 
             doubles, triples, homeruns, total_bases, stolen_bases, caught_stealing, stolen_base_percentage) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

            # Commit changes
            connection.commit()
        print(f"game_stats have been added to mlb_player_batting table.")
        return f"mlb_player_batting has been updated."


    # PITCHING DATA
    elif run_stat == 'pitching':
        for ind, row in df_pitch.iterrows():
            # Connect to DB
            connection = create_connection()
            cursor = connection.cursor()

            json_dict = {'year': int(row['year']),
                         'month': row['month'],
                         'game_id': int(row['game_id']),
                         'player_id': int(row['player_id']),
                         'team_id': int(row['team_id']),
                         'opp_id': int(row['opp_id']),
                         'innings_pitched': int(row['innings_pitched']),
                         'hits_allowed': int(row['hits_allowed']),
                         'runs_allowed': int(row['runs_allowed']),
                         'earned_runs_allowed': int(row['earned_runs_allowed']),
                         'walks_allowed': int(row['walks_allowed']),
                         'strikeouts': int(row['strikeouts']),
                         'homeruns': int(row['homeruns']),
                         'earned_run_avg': float(row['earned_run_avg']),
                         'batters_faced': int(row['batters_faced']),
                         'pitches_thrown': int(row['pitches_thrown']),
                         'strikes_thrown': int(row['strikes_thrown']),
                         'swinging_strikes': int(row['swinging_strikes']),
                         'ground_balls': int(row['ground_balls']),
                         'fly_balls': int(row['fly_balls']),
                         'gamescore': float(row['gamescore']),
                         'win_prob_added': float(row['win_prob_added'])}
            values = list(json_dict.values())

            # SQL Query
            cursor.execute("""INSERT INTO mlb_player_pitching (year, month, game_id, player_id, team_id, opp_id, innings_pitched, hits_allowed, runs_allowed,
             earned_runs_allowed, walks_allowed, strikeouts, homeruns, earned_run_avg, batters_faced, pitches_thrown, 
             strikes_thrown, swinging_strikes, ground_balls, fly_balls, gamescore, win_prob_added) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                           (values))

            connection.commit()
        print(f"stats have been added to mlb_player_pitching table.")
        return f"mlb_player_batting has been updated."

    else:
        raise Exception (f"{run_stat} is not a valid game log.")

@mlb.route('/mlb/standings', methods=['POST', 'PUT'])
def mlb_standings():
    # Initialize variables
    file = request.files['mlb_standings']
    year = 0

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        # Connect to DB
        connection = create_connection()
        cursor = connection.cursor()

        year = row['year']
        # Add data
        if flask.request.method == 'POST':
            json_dict = {'team_id': row['team_id'],
                         'year': row['year'],
                         'wins': row['wins'],
                         'losses': row['losses'],
                         'win_loss_percent': row['win_loss_percent'],
                         'runs_scored': row['runs_scored'],
                         'runs_allowed': row['runs_allowed'],
                         'run_diff': row['run_diff'],
                         'home_rec': row['home_rec'],
                         'away_rec': row['away_rec'],
                         'one_run_rec': row['one_run_rec'],
                         'vs_left': row['vs_left'],
                         'vs_right': row['vs_right'],
                         'over_five_hundred': row['over_five_hundred'],
                         'below_five_hundred': row['runs_allowed'],
                         'last_ten': row['last_ten'],
                         'last_twenty': row['last_twenty'],
                         'last_thirty': row['last_thirty'],
                         }
            values = list(json_dict.values())

            # SQL Query
            cursor.execute("""INSERT INTO mlb_standings (team_id, year, wins, losses, win_loss_percent, runs_scored,
             runs_allowed, run_diff, home_rec, away_rec, one_run_rec, vs_left, vs_right, over_five_hundred, below_five_hundred,
             last_ten, last_twenty, last_thirty) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (values))

            # Commit changes
            connection.commit()
            print(f"stats have been added to mlb_player_batting table.")

        # Update Data
        elif flask.request.method == 'PUT':
            json_dict = {'wins': row['wins'],
                         'losses': row['losses'],
                         'win_loss_percent': row['win_loss_percent'],
                         'runs_scored': row['runs_scored'],
                         'runs_allowed': row['runs_allowed'],
                         'run_diff': row['run_diff'],
                         'home_rec': row['home_rec'],
                         'away_rec': row['away_rec'],
                         'one_run_rec': row['one_run_rec'],
                         'vs_left': row['vs_left'],
                         'vs_right': row['vs_right'],
                         'over_five_hundred': row['over_five_hundred'],
                         'below_five_hundred': row['runs_allowed'],
                         'last_ten': row['last_ten'],
                         'last_twenty': row['last_twenty'],
                         'last_thirty': row['last_thirty'],
                         'team_id': row['team_id'],
                         'year': row['year']
                         }
            values = list(json_dict.values())

            # SQL Query
            cursor.execute("""UPDATE  mlb_standings 
                        SET wins = %s, losses = %s, win_loss_percent = %s, runs_scored = %s, runs_allowed = %s,
                        run_diff = %s, home_rec = %s, away_rec = %s, one_run_rec = %s, vs_left = %s, vs_right = %s,
                        over_five_hundred = %s, below_five_hundred = %s, last_ten = %s, last_twenty = %s, last_thirty = %s
                        WHERE mlb_standings.team_id = %s and mlb_standings.year = %s""", (values))

        # Commit changes
        connection.commit()

    return f"mlb_standings updated with {year} standings."


@mlb.route('/mlb/team_stats', methods=['POST', 'PUT'])
def mlb_team_stats():
    # Initialize variables
    year = 0
    bat_file = request.files['mlb_team_batting']
    pitch_file = request.files['mlb_team_pitching']

    # Read CSV data
    df_bat = pd.read_csv(bat_file)
    df_pitch = pd.read_csv(pitch_file)


    # TEAM BATTING
    for ind, row in df_bat.iterrows():
        year = row['year']

        connection = create_connection()
        cursor = connection.cursor()

        # Add data
        if flask.request.method == 'POST':
            json_dict = {'team_id': row['team_id'],
                           'year': row['year'],
                           'avg_batter_age': row['avg_batter_age'],
                           'runs_scored_per_game': row['runs_scored_per_game'],
                           'plate_appearances': row['plate_appearances'],
                           'runs_scored': row['runs_scored'],
                           'hits': row['hits'],
                           'doubles': row['doubles'],
                           'triples': row['triples'],
                           'homeruns': row['homeruns'],
                           'runs_batted_in': row['runs_batted_in'],
                           'stolen_bases': row['stolen_bases'],
                           'caught_stealing': row['caught_stealing'],
                           'stolen_base_percent': row['stolen_base_percent'],
                           'walks': row['walks'],
                           'strikeouts': row['strikeouts'],
                           'batting_average': row['batting_average'],
                           'on_base_percentage': row['on_base_percentage'],
                           'slugging_percentage': row['slugging_percentage'],
                           'on_base_plus_slugging': row['on_base_plus_slugging'],
                           'ops_plus': row['ops_plus'],
                           'total_bases': row['total_bases'],
                           'babip': row['babip'],
                           'iso': row['iso'],
                           'home_run_percentage': float(row['home_run_percentage']),
                           'strikeout_percentage': float(row['strikeout_percentage']),
                           'walks_percentage': float(row['walks_percentage']),
                           'avg_exit_velocity': row['avg_exit_velocity'],
                           'hard_hit_rate': float(row['hard_hit_rate']),
                           'line_drive_rate': float(row['line_drive_rate']),
                           'ground_ball_rate': float(row['ground_ball_rate']),
                           'fly_ball_rate': float(row['fly_ball_rate']),
                           'ground_ball_fly_ball_ratio': row['ground_ball_fly_ball_ratio'],
                           'pull_percentage': float(row['pull_percentage']),
                           'center_percentage': float(row['center_percentage']),
                           'opp_percentage': float(row['opp_percentage']),
                           'at_bats_per_strikeout': row['at_bats_per_strikeout'],
                           'at_bats_per_homerun': row['at_bats_per_homerun'],
                           'at_bats_per_rbi': row['at_bats_per_rbi'],
                           'strikeout_to_walk_ratio': row['strikeout_to_walk_ratio'],
                           'extra_base_hit_percentage': float(row['extra_base_hit_percentage']),
                           'fly_ball_homerun_rate': float(row['fly_ball_homerun_rate']),
                           'homeruns_vs_left': row['homeruns_vs_left'],
                           'homeruns_vs_right': row['homeruns_vs_right'],
                           'war': 0.0}
            values = list(json_dict.values())

            cursor.execute("""INSERT INTO mlb_team_batting (team_id, year, avg_batter_age, runs_scored_per_game, 
            plate_appearances, runs_scored, hits, doubles, triples, homeruns, runs_batted_in, stolen_bases, 
            caught_stealing, stolen_base_percent, walks, strikeouts, batting_average, on_base_percentage,
            slugging_percentage, on_base_plus_slugging, ops_plus, total_bases, babip, iso, home_run_percentage,
            strikeout_percentage, walks_percentage, avg_exit_velocity, hard_hit_rate, line_drive_rate, ground_ball_rate,
            fly_ball_rate, ground_ball_fly_ball_ratio, pull_percentage, center_percentage, opp_percentage, 
            at_bats_per_strikeout, at_bats_per_homerun, at_bats_per_rbi, strikeout_to_walk_ratio, 
            extra_base_hit_percentage, fly_ball_homerun_rate, homeruns_vs_left, homeruns_vs_right, war)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (values))
        # Upload data
        elif flask.request.method == 'PUT':
            json_dict = {'avg_batter_age': row['avg_batter_age'],
                         'runs_scored_per_game': row['runs_scored_per_game'],
                         'plate_appearances': row['plate_appearances'],
                         'runs_scored': row['runs_scored'],
                         'hits': row['hits'],
                         'doubles': row['doubles'],
                         'triples': row['triples'],
                         'homeruns': row['homeruns'],
                         'runs_batted_in': row['runs_batted_in'],
                         'stolen_bases': row['stolen_bases'],
                         'caught_stealing': row['caught_stealing'],
                         'stolen_base_percent': row['stolen_base_percent'],
                         'walks': row['walks'],
                         'strikeouts': row['strikeouts'],
                         'batting_average': row['batting_average'],
                         'on_base_percentage': row['on_base_percentage'],
                         'slugging_percentage': row['slugging_percentage'],
                         'on_base_plus_slugging': row['on_base_plus_slugging'],
                         'ops_plus': row['ops_plus'],
                         'total_bases': row['total_bases'],
                         'babip': row['babip'],
                         'iso': row['iso'],
                         'home_run_percentage': float(row['home_run_percentage']),
                         'strikeout_percentage': float(row['strikeout_percentage']),
                         'walks_percentage': float(row['walks_percentage']),
                         'avg_exit_velocity': row['avg_exit_velocity'],
                         'hard_hit_rate': float(row['hard_hit_rate']),
                         'line_drive_rate': float(row['line_drive_rate']),
                         'ground_ball_rate': float(row['ground_ball_rate']),
                         'fly_ball_rate': float(row['fly_ball_rate']),
                         'ground_ball_fly_ball_ratio': row['ground_ball_fly_ball_ratio'],
                         'pull_percentage': float(row['pull_percentage']),
                         'center_percentage': float(row['center_percentage']),
                         'opp_percentage': float(row['opp_percentage']),
                         'at_bats_per_strikeout': row['at_bats_per_strikeout'],
                         'at_bats_per_homerun': row['at_bats_per_homerun'],
                         'at_bats_per_rbi': row['at_bats_per_rbi'],
                         'strikeout_to_walk_ratio': row['strikeout_to_walk_ratio'],
                         'extra_base_hit_percentage': float(row['extra_base_hit_percentage']),
                         'fly_ball_homerun_rate': float(row['fly_ball_homerun_rate']),
                         'homeruns_vs_left': row['homeruns_vs_left'],
                         'homeruns_vs_right': row['homeruns_vs_right'],
                         'war': 0.0,
                         'team_id': row['team_id'],
                         'year': row['year']}
            values = list(json_dict.values())

            cursor.execute("""UPDATE  mlb_team_batting 
                        SET avg_batter_age = %s, runs_scored_per_game = %s, plate_appearances, runs_scored = %s,
                    hits = %s, doubles = %s, triples = %s, homeruns = %s, runs_batted_in = %s, stolen_bases = %s, 
                    caught_stealing = %s, stolen_base_percent = %s, walks = %s, strikeouts = %s, batting_average = %s, 
                    on_base_percentage = %s, slugging_percentage = %s, on_base_plus_slugging = %s, ops_plus = %s,
                    total_bases = %s, babip = %s, iso = %s, home_run_percentage = %s, strikeout_percentage = %s,
                    walks_percentage = %s, avg_exit_velocity = %s, hard_hit_rate = %s, line_drive_rate = %s, 
                    ground_ball_rate = %s, fly_ball_rate = %s, ground_ball_fly_ball_ratio = %s, pull_percentage = %s,
                    center_percentage = %s, opp_percentage = %s, at_bats_per_strikeout = %s, at_bats_per_homerun = %s,
                    at_bats_per_rbi = %s, strikeout_to_walk_ratio = %s, extra_base_hit_percentage = %s, 
                    fly_ball_homerun_rate = %s, homeruns_vs_left = %s, homeruns_vs_right = %s, war = %s
                    WHERE mlb_team_batting.team_id = %s and mlb_team_batting.year = %s""", (values))

        connection.commit()
    print(f"mlb_team_pitching has been updated with {year} data.")

    # TEAM PITCHING
    for ind, row in df_pitch.iterrows():
        year = row['year']

        connection = create_connection()
        cursor = connection.cursor()

        # Add data
        if flask.request.method == 'POST':
            json_dict = {'team_id': row['team_id'],
                           'year': row['year'],
                           'avg_pitcher_age': row['avg_pitcher_age'],
                           'runs_allowed_game': row['runs_allowed_game'],
                           'earned_run_avg': row['earned_run_avg'],
                           'innings_pitches': row['innings_pitches'],
                           'hits_allowed': row['hits_allowed'],
                           'doubles_allowed': row['doubles_allowed'],
                           'triples_allowed': row['triples_allowed'],
                           'home_runs_allowed': row['home_runs_allowed'],
                           'steals_allowed': row['steals_allowed'],
                           'total_bases_allowed': row['total_bases_allowed'],
                           'runs_allowed': row['runs_allowed'],
                           'earned_runs': row['earned_runs'],
                           'walks_allowed': row['walks_allowed'],
                           'strikeouts': row['strikeouts'],
                           'earned_runs_plus': row['earned_runs_plus'],
                           'fip': row['fip'],
                           'whip': row['whip'],
                           'hits_per_nine': row['hits_per_nine'],
                           'home_runs_per_nine': row['home_runs_per_nine'],
                           'walks_per_nine': row['walks_per_nine'],
                           'strikeouts_per_nine': row['strikeouts_per_nine'],
                           'strikeouts_per_walk': row['strikeouts_per_walk'],
                           'runners_left_on_base': row['runners_left_on_base'],
                           'batting_avg_against': row['batting_avg_against'],
                           'on_base_percent_allowed': row['on_base_percent_allowed'],
                           'slugging_percent_against': row['slugging_percent_against'],
                           'ops_allowed': row['ops_allowed'],
                           'babip_allowed': row['babip_allowed'],
                           'home_run_allowed_percent': row['home_run_allowed_percent'],
                           'strikeout_percentage': row['strikeout_percentage'],
                           'walk_allowed_percentage': row['walk_allowed_percentage'],
                           'avg_exit_velocity': row['avg_exit_velocity'],
                           'hard_hit_rate': row['hard_hit_rate'],
                           'line_drive_rate': row['line_drive_rate'],
                           'ground_ball_rate': row['ground_ball_rate'],
                           'fly_ball_rate': row['fly_ball_rate'],
                           'ground_ball_fly_ball_ratio': row['ground_ball_fly_ball_ratio'],
                           'win_probability_added': row['win_probability_added'],
                           'fly_ball_home_run_percent': row['fly_ball_home_run_percent'],
                           'extra_base_percentage': row['extra_base_percentage']}
            values = list(json_dict.values())

            cursor.execute("""INSERT INTO mlb_team_pitching (team_id, year, avg_pitcher_age, runs_allowed_game, 
            earned_run_avg, innings_pitches, hits_allowed, doubles_allowed, triples_allowed, home_runs_allowed,
            steals_allowed, total_bases_allowed, runs_allowed, earned_runs, walks_allowed, strikeouts, earned_runs_plus,
            fip, whip, hits_per_nine, home_runs_per_nine, walks_per_nine, strikeouts_per_nine, strikeouts_per_walk, 
            runners_left_on_base, batting_avg_against, on_base_percent_allowed, slugging_percent_against, ops_allowed,
            babip_allowed, home_run_allowed_percent, strikeout_percentage, walk_allowed_percentage, avg_exit_velocity,
            hard_hit_rate, line_drive_rate, ground_ball_rate, fly_ball_rate, ground_ball_fly_ball_ratio, 
            win_probability_added, fly_ball_home_run_percent, extra_base_percentage)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (values))
        # Upload data
        elif flask.request.method == 'PUT':
            json_dict = {'avg_pitcher_age': row['avg_pitcher_age'],
                         'runs_allowed_game': row['runs_allowed_game'],
                         'earned_run_avg': row['earned_run_avg'],
                         'innings_pitches': row['innings_pitches'],
                         'hits_allowed': row['hits_allowed'],
                         'doubles_allowed': row['doubles_allowed'],
                         'triples_allowed': row['triples_allowed'],
                         'home_runs_allowed': row['home_runs_allowed'],
                         'steals_allowed': row['steals_allowed'],
                         'total_bases_allowed': row['total_bases_allowed'],
                         'runs_allowed': row['runs_allowed'],
                         'earned_runs': row['earned_runs'],
                         'walks_allowed': row['walks_allowed'],
                         'strikeouts': row['strikeouts'],
                         'earned_runs_plus': row['earned_runs_plus'],
                         'fip': row['fip'],
                         'whip': row['whip'],
                         'hits_per_nine': row['hits_per_nine'],
                         'home_runs_per_nine': row['home_runs_per_nine'],
                         'walks_per_nine': row['walks_per_nine'],
                         'strikeouts_per_nine': row['strikeouts_per_nine'],
                         'strikeouts_per_walk': row['strikeouts_per_walk'],
                         'runners_left_on_base': row['runners_left_on_base'],
                         'batting_avg_against': row['batting_avg_against'],
                         'on_base_percent_allowed': row['on_base_percent_allowed'],
                         'slugging_percent_against': row['slugging_percent_against'],
                         'ops_allowed': row['ops_allowed'],
                         'babip_allowed': row['babip_allowed'],
                         'home_run_allowed_percent': row['home_run_allowed_percent'],
                         'strikeout_percentage': row['strikeout_percentage'],
                         'walk_allowed_percentage': row['walk_allowed_percentage'],
                         'avg_exit_velocity': row['avg_exit_velocity'],
                         'hard_hit_rate': row['hard_hit_rate'],
                         'line_drive_rate': row['line_drive_rate'],
                         'ground_ball_rate': row['ground_ball_rate'],
                         'fly_ball_rate': row['fly_ball_rate'],
                         'ground_ball_fly_ball_ratio': row['ground_ball_fly_ball_ratio'],
                         'win_probability_added': row['win_probability_added'],
                         'fly_ball_home_run_percent': row['fly_ball_home_run_percent'],
                         'extra_base_percentage': row['extra_base_percentage'],
                         'team_id': row['team_id'],
                         'year': row['year']}
            values = list(json_dict.values())

            # SQL Query
            cursor.execute("""UPDATE  mlb_team_pitching
                        SET avg_pitcher_age = %s, runs_allowed_game = %s, earned_run_avg = %s, innings_pitches = %s,
                hits_allowed = %s, doubles_allowed = %s, triples_allowed = %s, home_runs_allowed = %s, 
                steals_allowed = %s, total_bases_allowed = %s, runs_allowed = %s, earned_runs = %s, walks_allowed = %s, 
                strikeouts = %s, earned_runs_plus = %s, fip = %s, whip = %s, hits_per_nine = %s, home_runs_per_nine = %s, 
                walks_per_nine = %s, strikeouts_per_nine = %s, strikeouts_per_walk = %s, runners_left_on_base = %s, 
                batting_avg_against = %s, on_base_percent_allowed = %s, slugging_percent_against = %s, ops_allowed = %s,
                babip_allowed = %s, home_run_allowed_percent = %s, strikeout_percentage = %s, walk_allowed_percentage = %s,
                avg_exit_velocity = %s, hard_hit_rate = %s, line_drive_rate = %s, ground_ball_rate = %s,
                fly_ball_rate = %s, ground_ball_fly_ball_ratio = %s, win_probability_added = %s,
                fly_ball_home_run_percent = %s, extra_base_percentage = %s
                WHERE mlb_team_pitching.team_id = %s and mlb_team_pitching.year = %s""", (values))

        # Commit changes
        connection.commit()
    print(f"mlb_team_pitching has been updated with {year} data.")


    return f"mlb_team tables have been updated."