from .db import create_connection
from flask import Blueprint, request
import pandas as pd

import json

mlb = Blueprint("mlb", __name__)


@mlb.route('/mlb/games', methods=['POST'])
def mlb_game_info():
    file = request.files['mlb_game_info']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add Games:
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
        print(values)

        cursor.execute('''INSERT INTO mlb_games (year, date, day_of_the_week, away_team_id, away_score, home_team_id,
        home_score, margin_of_victory, total_runs) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', (values))

        connection.commit()

    return f"mlb_games table has been updated with the most recent game data."


@mlb.route('/mlb/player_batting', methods=['POST'])
def mlb_player_batting():
    bat_file = request.files['mlb_batting_log']
    pitch_file = request.files['mlb_pitching_log']

    # Read CSV data
    df_bat = pd.read_csv(bat_file)
    df_pitch = pd.read_csv(pitch_file)

    for ind, row in df_bat.iterrows():
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

        cursor.execute("""INSERT INTO mlb_player_batting (year, month, game_id, player_id, team_id, opp_id, at_bats, runs, hits,
         runs_batted_in, walks, strikeouts, batting_avg, on_base_percentage, slugging_percentage, on_base_plus_slug_percentage, 
         doubles, triples, homeruns, total_bases, stolen_bases, caught_stealing, stolen_base_percentage) 
         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

        connection.commit()
        print(f"game_stats have been added to nfl_player_stats table.")

    for ind, row in df_pitch.iterrows():
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

        cursor.execute("""INSERT INTO mlb_player_pitching (year, month, game_id, player_id, team_id, opp_id, innings_pitched, hits_allowed, runs_allowed,
         earned_runs_allowed, walks_allowed, strikeouts, homeruns, earned_run_avg, batters_faced, pitches_thrown, 
         strikes_thrown, swinging_strikes, ground_balls, fly_balls, gamescore, win_prob_added) 
         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       (values))

        connection.commit()
        print(f"stats have been added to mlb_player_batting table.")


    return f"mlb_player_batting has been updated."