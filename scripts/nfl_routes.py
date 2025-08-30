import pandas as pd
import numpy as np
import statistics

from .db import create_connection
import flask
from flask import Blueprint, request, jsonify

nfl = Blueprint("nfl", __name__)
pd.set_option('display.max_columns', 100)

# GET ROUTES
@nfl.route('nfl/player_logs', methods=['GET'])


def nfl_player_logs():
    player_id = request.args.get('id', None)
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = int(request.args.get('value', None))
    loop_years = list(range(2019, 2025))
    rank_years = list(range(2022, 2025))

    teams = []
    limit_stat_dict = {'pass_att': 'pass_att', 'pass_yards': 'pass_att', 'pass_td': 'pass_att', 'pass_comp': 'pass_att',
                       'pass_longest': 'pass_att',
                       'rush_att': 'rush_att', 'rush_yards': 'rush_att', 'rush_td': 'rush_att', 'rush_longest': 'rush_att',
                       'rec': 'targets', 'targets': 'targets', 'rec_yards': 'targets', 'rec_td': 'targets', 'rec_longest': 'targets'}
    limit_stat = limit_stat_dict[column_name]
    json_output = {}
    cols_to_select = f"game_id, player_id, team_id, opp_id, {limit_stat}, {column_name}"

    # GET ALL TEAM OFFENSE STATS - Create a query, cursor and result list. Loop through list and merge to create 'df_team_offense'
    connection = create_connection()
    cursor = connection.cursor()
    team_off_query = f'''SELECT * FROM nfl_team_offense'''

    cursor.execute(team_off_query)
    results = list(cursor.fetchall())
    off_cols = ['id', 'team_id', 'year', 'games', 'dvoa', 'epa_per_play', 'success_rate', 'dropback_epa', 'dropback_sr',
                'rush_epa', 'rush_sr', 'pass_comp', 'pass_att', 'pass_comp_percentage', 'pass_yards', 'pass_td',
                'pass_td_percentage', 'yards_per_att', 'pass_yards_per_comp', 'pass_yards_per_game', 'passer_rating',
                'sacks', 'ints', 'int_percentage', 'rush_att', 'rush_yards', 'rush_td', 'rush_yards_per_att',
                'rush_yards_per_game', 'fumbles', 'points_per_game', 'total_points', 'drives', 'plays', 'scoring_percentage',
                'to_percentage', 'plays_per_drive', 'yards_per_drive', 'points_per_drive', 'third_down_att',
                'third_down_conv', 'third_down_conv_rate', 'fourth_down_att', 'fourth_down_conv',
                'fourth_down_conv_rate', 'rz_att', 'rz_td', 'rz_percentage']
    df_team_offense = pd.DataFrame(results, columns=off_cols).reset_index(drop=True)

    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()
    query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, {cols_to_select}
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN 
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    WHERE nfl_games.year >= 2019'''

    cursor.execute(query)
    results = list(cursor.fetchall())
    df_columns = ['name', 'Year', 'Week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', limit_stat, column_name]
    df_all_games = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)
    df_all_games.reset_index(inplace=True)

    # GET ALL RED ZONE STATS - Create a query, cursor and result list. Loop through list and merge to create 'df_red_zone'
    connection = create_connection()
    cursor = connection.cursor()
    rz_query = f'''SELECT CONCAT(player.first_name, ' ', player.last_name), nfl_redzone_stats.*
                FROM nfl_redzone_stats
                JOIN player ON player.id = nfl_redzone_stats.player_id'''

    cursor.execute(rz_query)
    rz_results = list(cursor.fetchall())
    rz_cols = ['name', 'id', 'player_id', 'year', 'rz_20_pass_att', 'rz_20_pass_comp',  'rz_20_pass_comp_percentage',
               'rz_20_pass_yard', 'rz_20_pass_td', 'rz_20_pass_int', 'rz_10_pass_att', 'rz_10_pass_comp', 'rz_10_comp_percentage',
               'rz_10_pass_yard', 'rz_10_pass_td', 'rz_10_pass_int', 'rz_20_targets', 'rz_20_receptions', 'rz_20_rec_yards',
               'rz_20_catch_percentage', 'rz_20_rec_td', 'rz_20_target_percentage', 'rz_10_targets', 'rz_10_receptions',
               'rz_10_rec_yards', 'rz_10_catch_percentage', 'rz_10_rec_td', 'rz_10_target_percentage', 'rz_20_rush_att',
               'rz_20_rush_yards', 'rz_20_rush_td', 'rz_20_rush_percentage', 'rz_10_rush_att', 'rz_10_rush_yards', 'rz_10_rush_td',
               'rz_10_rush_percentage', 'rz_5_rush_att', 'rz_5_rush_yards', 'rz_5_rush_td', 'rz_5_rush_percentage']
    df_red_zone = pd.DataFrame(rz_results, columns=rz_cols).reset_index(drop=True)

    # GET WEEKLY RANK STATS - Create a query, cursor and result list. Loop through list and merge to create 'df_red_zone'
    if column_name in ['pass_att', 'pass_comp', 'pass_yards',	'pass_td']:
        other_cols = ['pyards_per_att', 'pass_td_per_att', 'pass_yards_rank', 'pass_comp_rank', 'pass_td_rank',
                      'pass_yars_per_att_rank']
        wkly_cols_to_select = f"team_id, year, week, {column_name}, {other_cols[0]}, {other_cols[1]}, {other_cols[2]}, {other_cols[3]}, {other_cols[4]}, {other_cols[5]}"
    elif column_name in ['rush_att', 'rush_yards',	'rush_td']:
        other_cols = ['ryards_per_att', 'rush_td_per_att', 'rush_att_rank', 'rush_yards_rank', 'rush_td_rank',
                      'rush_yars_per_att_rank']
        wkly_cols_to_select = f"team_id, year, week, {column_name}, {other_cols[0]}, {other_cols[1]}, {other_cols[2]}, {other_cols[3]}, {other_cols[4]}, {other_cols[5]}"
    else:
        other_cols = ['rec_td_per_rec', 'rec_yards_rank', 'rec_td_rank', 'rec_rank', 'rec_yars_per_rec_rank']
        wkly_cols_to_select = f"team_id, year, week, {column_name}, {other_cols[0]}, {other_cols[1]}, {other_cols[2]}, {other_cols[3]}, {other_cols[4]}"
    connection = create_connection()
    cursor = connection.cursor()
    weekly_rank_query = f'''SELECT {wkly_cols_to_select} FROM nfl_weekly_rank'''

    cursor.execute(weekly_rank_query)
    weekly_rank_results = list(cursor.fetchall())
    weekly_rank_cols = ['team_id', 'year', 'week', column_name] + other_cols
    df_weekly_rank = pd.DataFrame(weekly_rank_results, columns=weekly_rank_cols).reset_index(drop=True)

    # Get player position and teams they played for.
    df_player_game_logs = df_all_games[df_all_games['player_id'] == int(player_id)].reset_index(drop=True)
    player_position = df_player_game_logs.head(1)['pos'].values.tolist()[0]

    player_teams_dict = {}
    for year in loop_years:
        df_player_teams = df_player_game_logs.copy()[['name', 'Year', 'team_id']].drop_duplicates()
        try:
            player_team = df_player_teams.loc[df_player_teams['Year'] == year]['team_id'].values.tolist()[0]
        except IndexError:
            player_team = 0
        player_teams_dict[year] = player_team

    # Get the weeks player appeared in each year and opponents
    week_dict = {}
    opp_dict = {}
    for year in rank_years:
        opponents = df_player_game_logs.loc[df_player_game_logs['Year'] == year]['opp_id'].values.tolist()
        get_weeks = df_player_game_logs.loc[df_player_game_logs['Year'] == year]['Week'].values.tolist()
        week_dict[year] = get_weeks
        game_dict = {}
        for key in get_weeks:
            for val in opponents:
                game_dict[key] = val
                opponents.remove(val)
                break
        opp_dict[year] = game_dict

    # Update the index column
    df_player_logs_test = pd.DataFrame()
    for year in loop_years:
        df_merge = df_player_game_logs.loc[df_player_game_logs['Year'] == year]
        df_merge.index = np.arange(1, len(df_merge) + 1)
        df_player_logs_test = pd.concat([df_player_logs_test, df_merge])

    # Gets number of games each of the prev 3 years and total career (since 2019)
    total_player_games = len(df_player_game_logs)
    current_total_games = len(df_player_game_logs.loc[df_player_game_logs['Year'] == 2024])
    prior_total_games = len(df_player_game_logs.loc[df_player_game_logs['Year'] == 2023])
    third_total_games = len(df_player_game_logs.loc[df_player_game_logs['Year'] == 2022])

    # Initialize dictionary variables
    year_name_dict = {2022: 'third', 2023: 'prior', 2024: 'current'}
    total_game_dict = {2022: third_total_games, 2023: prior_total_games, 2024: current_total_games}

    # get the occurrence in the previous eight games
    df_last_four = df_player_game_logs.sort_values(by=['Year', 'Week'], ascending=False).head(4)  # sort values by most recent games

    if operator == 'over':
        df_last_four_occur = df_last_four.loc[df_last_four[column_name] > value]
    else:
        df_last_four_occur = df_last_four.loc[df_last_four[column_name] <= value]
    last_four_bet_occurrence = len(df_last_four_occur)
    last_four_percentage = str(round(((last_four_bet_occurrence/4) *100))) + '%'
    json_output.update({'occurrence_count_last_four':last_four_bet_occurrence})
    json_output.update({'occurrence_percentage_last_four': last_four_percentage})
    json_output.update({'last_four_game_logs': df_last_four.to_json()})

    # # get the occurrence in the previous eight games
    df_last_eight = df_player_game_logs.sort_values(by=['Year', 'Week'], ascending=False).head(8)# sort values by most recent games
    if operator == 'over':
        df_last_eight_occur = df_last_eight.loc[df_last_eight[column_name] > value]
    else:
        df_last_eight_occur = df_last_eight.loc[df_last_eight[column_name] <= value]
    last_eight_bet_occurrence = len(df_last_eight_occur)
    last_eight_percentage = str(round(((last_eight_bet_occurrence/8) *100))) + '%'
    json_output.update({'occurrence_count_last_eight':last_eight_bet_occurrence})
    json_output.update({'occurrence_percentage_last_eight': last_eight_percentage})
    json_output.update({'last_eight_game_logs': df_last_eight.to_json()})

    # determine what df_final will be for the total/current/prior/third dataframes
    if operator == 'over':
        df_game_log_bet = df_player_game_logs.loc[df_player_game_logs[column_name] > value]
    else:
        df_game_log_bet = df_player_game_logs.loc[df_player_game_logs[column_name] <= value]

    # Get total bet frequency data
    df_total_occurrence = df_game_log_bet.copy()
    total_bet_occurrence = len(df_total_occurrence)
    total_percentage = str(round(((total_bet_occurrence/total_player_games) *100))) + '%'
    json_output.update({'career_bet_occurrence':total_bet_occurrence})
    json_output.update({'career_bet_occurrence_percentage': total_percentage})
    json_output.update({'career_total_games': total_player_games})

    # Get yearly bet frequency data
    for year in rank_years:
        df_game_log_bet_copy = df_game_log_bet.copy()
        df_bet_occurrence = df_game_log_bet_copy.loc[df_game_log_bet_copy['Year'] == year]
        # print(df_bet_occurrence)
        bet_occurrence_count = len(df_bet_occurrence)
        bet_percentage = str(round(((bet_occurrence_count/total_game_dict[year]) *100), 2)) + '%'
        # print(f"Bet Percentage for {year} = {bet_percentage}")
        json_output.update({f"bet_occurrences_{year_name_dict[year]}": bet_occurrence_count})
        json_output.update({f"bet_occurrence_percentage_{year_name_dict[year]}": bet_percentage})
        json_output.update({f"total_games_{year_name_dict[year]}": total_game_dict[year]})
        json_output.update({f"bet_occurrence_logs_{year_name_dict[year]}": df_bet_occurrence.to_json()})

        # Get total game logs each year
        df_total_game_logs = df_player_game_logs.loc[df_player_game_logs['Year'] == year]
        json_output.update({f"game_logs_{year_name_dict[year]}": df_total_game_logs.to_json()})

    # Get the time between bet occurrences
    for year in rank_years:
        # Get first and last game played by player each year.
        player_weeks = week_dict[year]
        first_game_played = player_weeks[0]
        last_game_played = player_weeks[-1]

        # Get the first and last weeks that bet would have hit.
        df_between_games = df_game_log_bet.loc[df_game_log_bet['Year'] == year]
        weeks_bet_hit_list = df_between_games['Week'].values.tolist()
        try:
            first_game_hit = weeks_bet_hit_list[0]
        except IndexError:
            first_game_hit = 0
        try:
            last_game_hit = weeks_bet_hit_list[-1]
        except IndexError:
            last_game_hit = 0

        # Create list of lengths between bet occurrences then take the average.
        length_btw_list = []
        for ind in range(len(weeks_bet_hit_list)):
            week = weeks_bet_hit_list[ind]
            if ind == 0:
                length = first_game_hit - first_game_played
            elif ind == len(weeks_bet_hit_list) - 1:
                length = last_game_played - last_game_hit
            else:
                length = week - weeks_bet_hit_list[ind - 1] - 1
            length_btw_list.append(length)
        length_btw_list.append(last_game_played - last_game_hit)
        avg_length = sum(length_btw_list)/len(length_btw_list)

        json_output.update({f"avg_time_between_occurrence_{year_name_dict[year]}": avg_length})
        json_output.update({f"avg_time_between_occurrence_list_{year_name_dict[year]}": length_btw_list})

    # Get Red Zone Stats
    for year in rank_years:
        team = player_teams_dict[year]

        # Rank Team RZ Stats Each Year
        df_team_rz_rank = df_team_offense.copy()
        df_team_rz_rank = df_team_rz_rank.loc[df_team_rz_rank['year'] == year]
        df_team_rz_rank["team_rz_percentage rank"] = df_team_rz_rank['rz_percentage'].rank(ascending=False)
        df_team_rz_rank["team_rz_td rank"] = df_team_rz_rank['rz_td'].rank(ascending=False)

        # Get Team Red Zone Stats
        df_team_rz = df_team_offense.copy()
        df_team_rz = df_team_rz.loc[(df_team_rz['team_id'] == team) & (df_team_rz['year'] == year)]
        team_rz_att = df_team_rz['rz_att'].values.tolist()[0]
        team_rz_td = df_team_rz['rz_td'].values.tolist()[0]
        team_rz_sr = df_team_rz['rz_percentage'].values.tolist()[0]

        json_output.update( {f"team_rz_success_rate_rank_{year_name_dict[year]}":
                                 df_team_rz_rank['team_rz_percentage rank'].values.tolist()[0]})
        json_output.update({f"team_rz_td_rank_{year_name_dict[year]}":
                                df_team_rz_rank['team_rz_td rank'].values.tolist()[0]})
        json_output.update({f"team_rz_success_rate_{year_name_dict[year]}": team_rz_sr})
        json_output.update({f"team_rz_touchdowns_{year_name_dict[year]}": team_rz_td})
        json_output.update({f"team_rz_attempts_{year_name_dict[year]}": team_rz_att})

        # Red Zone Stats for Player Each Year
        df_rz_player = df_red_zone.copy()
        df_rz_player = df_rz_player.loc[(df_rz_player['player_id'] == int(player_id)) & (df_rz_player['year'] == year)]

        # Red Zone Passing
        json_output.update({f"rz_total_pass_touchdowns_{year_name_dict[year]}":
                                df_rz_player['rz_20_pass_td'].values.tolist()[0]})
        json_output.update({f"rz_within_10yd_pass_touchdowns_{year_name_dict[year]}":
                                df_rz_player['rz_10_pass_td'].values.tolist()[0]})
        json_output.update({f"pass_td_pct_of_team_rz_td_{year_name_dict[year]}":
                                round((df_rz_player['rz_20_pass_td'].values.tolist()[0] / team_rz_td), 2)})
        json_output.update({f"pass_td_pct_of_rz_drives_{year_name_dict[year]}":
                                round((df_rz_player['rz_20_pass_td'].values.tolist()[0] / team_rz_att), 2)})
        json_output.update(
            {f"rz_total_pass_att_{year_name_dict[year]}": df_rz_player['rz_20_pass_att'].values.tolist()[0]})
        json_output.update(
            {f"rz_within_10yd_pass_att_{year_name_dict[year]}": df_rz_player['rz_20_pass_att'].values.tolist()[0]})

        # Red Zone Rushing
        json_output.update({f"rz_total_rush_touchdowns_{year_name_dict[year]}":
                                df_rz_player['rz_20_rush_td'].values.tolist()[0]})
        json_output.update({f"rush_td_pct_of_team_rz_td_{year_name_dict[year]}":
                                round((df_rz_player['rz_20_rush_td'].values.tolist()[0] / team_rz_td), 2)})
        json_output.update({f"rush_td_pct_of_rz_drives_{year_name_dict[year]}":
                                round((df_rz_player['rz_20_rush_td'].values.tolist()[0] / team_rz_att), 2)})
        json_output.update({f"pct_of_total_rz_rushes_{year_name_dict[year]}":
                                df_rz_player['rz_20_rush_percentage'].values.tolist()[0]})
        json_output.update({f"pct_of_within_10yd_rz_rushes_{year_name_dict[year]}":
                                df_rz_player['rz_10_rush_percentage'].values.tolist()[0]})
        json_output.update({f"pct_of_within_5yd_rz_rushes_{year_name_dict[year]}":
                                df_rz_player['rz_5_rush_percentage'].values.tolist()[0]})

        # Red Zone Receiving
        json_output.update({f"rz_total_rec_touchdowns_{year_name_dict[year]}":
                                df_rz_player['rz_20_rec_td'].values.tolist()[0]})
        json_output.update({f"rz_within_10yd_rec_touchdowns_{year_name_dict[year]}":
                                df_rz_player['rz_10_rec_td'].values.tolist()[0]})
        json_output.update({f"rec_td_pct_of_team_rz_td_{year_name_dict[year]}":
                                round((df_rz_player['rz_20_rec_td'].values.tolist()[0] / team_rz_td), 2)})
        json_output.update({f"rec_td_pct_of_rz_drives_{year_name_dict[year]}":
                                round((df_rz_player['rz_20_rec_td'].values.tolist()[0] / team_rz_att), 2)})
        json_output.update({f"rz_total_tgt_percentage_{year_name_dict[year]}":
                                df_rz_player['rz_20_target_percentage'].values.tolist()[0]})
        json_output.update({f"rz_within_10yd_tgt_percentage_{year_name_dict[year]}":
                                df_rz_player['rz_10_target_percentage'].values.tolist()[0]})
        try:
            json_output.update({f"rz_touchdown_per_target_{year_name_dict[year]}":
                                round((df_rz_player['rz_20_rec_td'].values.tolist()[0] /
                                       df_rz_player['rz_20_targets'].values.tolist()[0]), 2)})
            json_output.update({f"rz_touchdown_per_target_within_10yd_{year_name_dict[year]}":
                                round((df_rz_player['rz_10_rec_td'].values.tolist()[0] /
                                       df_rz_player['rz_10_targets'].values.tolist()[0]), 2)})
        except ZeroDivisionError:
            json_output.update({f"rz_touchdown_per_target_{year_name_dict[year]}": 0})
            json_output.update({f"rz_touchdown_per_target_within_10yd_{year_name_dict[year]}": 0})

    if column_name not in ['pass_att', 'pass_yards', 'pass_td', 'pass_comp', 'pass_longest']:
        # GOAL - To get the players stat total as a percentage of team total.
        for year in rank_years:
            # Get df of games player appeared in. Includes player and all teammate data.
            plyr_team_id = player_teams_dict[year]
            df_plyr_team_games = df_all_games.copy()
            df_plyr_team_games = df_plyr_team_games.loc[
                (df_plyr_team_games['Year'] == year) & (df_plyr_team_games['team_id'] == plyr_team_id)]

            # List of game_ids for games player appeared in
            df_log = df_player_game_logs.copy()
            df_log = df_log.loc[df_log['Year'] == year]
            games_player_appeared_in = df_log['game_id'].values.tolist()

            y_team_total = {}
            z_pct_team_total = {}
            for game in games_player_appeared_in:
                df = df_plyr_team_games.copy()
                df = df.loc[df['game_id'] == game]
                week = df['Week'].values.tolist()[0]
                df_plyr = df.loc[df['player_id'] == int(player_id)]
                player_stat_total = df_plyr[column_name].values.tolist()[0]
                team_stat_total = df[column_name].sum()
                player_pct_of_total = round(round((player_stat_total / team_stat_total), 2) * 100)

                # Add to y/z-coordinate lists
                y_team_total[week] = int(team_stat_total)
                z_pct_team_total[week] = int(player_pct_of_total)
            json_output.update(
                {f"y_coord_team_stat_total_{year_name_dict[year]}": list(y_team_total.values())})
            json_output.update(
                {f"z_coord_plyr_pct_of_stat_total_{year_name_dict[year]}": list(z_pct_team_total.values())})

    # Graph Related Items
    for year in rank_years:
        # Get Limit Stat Value
        if column_name in ['pass_att', 'pass_yards', 'pass_td', 'pass_comp', 'pass_longest']:
            limit_stat_val = 10
        elif column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
            limit_stat_val = 3
        else:
            limit_stat_val = 3

        # X-Coordinates (weeks)
        weeks = week_dict[year]
        json_output.update({f"x_cord_player_weeks_{year_name_dict[year]}": weeks})

        # GRAPH - Player Weekly Stat Total vs League Average
        df_player_wkly_stats = df_player_game_logs.loc[df_player_game_logs['Year'] == year]
        # Get Y (stat_value) coordinates:
        plyr_weekly_stat_totals = df_player_wkly_stats[column_name].values.tolist()
        json_output.update({f"y_coord_plyr_weekly_stat_total_{year_name_dict[year]}": plyr_weekly_stat_totals})

        # Get Y Coordinate Weekly League Average Stat Total for Pos
        df_league_wkly_stats_avg = df_all_games.copy()
        df_league_wkly_stats_avg = df_league_wkly_stats_avg.loc[(df_league_wkly_stats_avg['Year'] == year) &
                                                                (df_league_wkly_stats_avg['pos'] == player_position) &
                                                                (df_league_wkly_stats_avg[limit_stat] >= limit_stat_val)]
        league_wkly_avg_val_dict = {}
        for week in weeks:
            df_loop = df_league_wkly_stats_avg.copy()
            df_loop = df_loop.loc[df_loop['Week'] == week]
            league_weekly_avg_val = df_loop[column_name].mean()
            league_wkly_avg_val_dict[week] = round(league_weekly_avg_val)
        json_output.update(
            {f"z_coord_league_avg_weekly_stat_total_{year_name_dict[year]}": list(league_wkly_avg_val_dict.values())})

    for year in rank_years:
        df_weekly_rank_copy = df_weekly_rank.copy()
        df_weekly_rank_copy = df_weekly_rank_copy.loc[df_weekly_rank_copy['year'] == year]
        opp_weekly_total = {}
        opp_per_att = {}
        opp_td_rank = {}
        opp_per_att_rank = {}
        for wk, opp in opp_dict[year].items():
            df_week = df_weekly_rank_copy.loc[
                (df_weekly_rank_copy['team_id'] == opp) & (df_weekly_rank_copy['week'] == wk)]
            data_list = df_week.values.tolist()[0]
            opp_weekly_total[wk] = data_list[3]
            opp_per_att[wk] = data_list[4]
            opp_td_rank[wk] = data_list[7]
            opp_per_att_rank[wk] = data_list[8]

        json_output.update({f"opponent_weeks_{year_name_dict[year]}": list(opp_weekly_total.keys())})
        json_output.update({f"opp_stat_totals_{year_name_dict[year]}": list(opp_weekly_total.values())})
        json_output.update({f"opp_per_att_totals_{year_name_dict[year]}": list(opp_per_att.values())})
        json_output.update({f"opp_td_weekly_ranks_{year_name_dict[year]}": list(opp_td_rank.values())})
        json_output.update({f"opp_per_att_ranks_{year_name_dict[year]}": list(opp_per_att_rank.values())})

    # Enable Access-Control-Allow-Origin
    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output


@nfl.route('nfl/bet_occurrence', methods=['GET'])
def nfl_get_bet_occurrences():
    player_id = request.args.get('id', None)
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = int(request.args.get('value', None))

    limit_stat_dict = {'pass_att': 'pass_att', 'pass_yards': 'pass_att', 'pass_td': 'pass_att', 'pass_comp': 'pass_att',
                       'pass_longest': 'pass_att',
                       'rush_att': 'rush_att', 'rush_yards': 'rush_att', 'rush_td': 'rush_att', 'rush_longest': 'rush_att',
                       'rec': 'targets', 'targets': 'targets', 'rec_yards': 'targets', 'rec_td': 'targets', 'rec_longest': 'targets'}
    limit_stat = limit_stat_dict[column_name]
    cols_to_select = f"game_id, player_id, team_id, opp_id, {limit_stat}, {column_name}"
    json_output = {}

    # GET ALL GAME LOGS - Create a query, cursor and result list. Loop through list and merge to create 'df_all_games'
    connection = create_connection()
    cursor = connection.cursor()

    player_query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, {cols_to_select}
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN 
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    WHERE nfl_games.year >= 2019 AND nfl_player_stats.player_id = %s'''
    values = [player_id]
    cursor.execute(player_query, values)

    results = list(cursor.fetchall())

    df_columns = ['name', 'Year', 'Week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', limit_stat, column_name]
    df_player_logs = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)

    # Total Bet Occurrences
    if operator == 'over':
        df_total_occurrence = df_player_logs.loc[df_player_logs[column_name] > value]
    else:
        df_total_occurrence = df_player_logs.loc[df_player_logs[column_name] <= value]
    total_occurrence_percentage = round((len(df_total_occurrence) / len(df_player_logs) * 100), 1)
    json_output.update({'career_bet_occurrence': total_occurrence_percentage})


    # Prior Year Occurrences
    total_prior_games = len(df_player_logs.loc[df_player_logs['Year'] == 2024])
    if operator == 'over':
        df_prior_occurrences = df_player_logs.loc[
            (df_player_logs[column_name] > value) & (df_player_logs['Year'] == 2024)]
    else:
        df_prior_occurrences = df_player_logs.loc[
            (df_player_logs[column_name] <= value) & (df_player_logs['Year'] == 2024)]
    prior_occurrence_percentage = round(((len(df_prior_occurrences) / total_prior_games) * 100), 1)
    json_output.update({'prior_bet_occurrence': prior_occurrence_percentage})


    total_third_games = len(df_player_logs.loc[df_player_logs['Year'] == 2023])
    if operator == 'over':
        df_third_occurrences = df_player_logs.loc[
            (df_player_logs[column_name] > value) & (df_player_logs['Year'] == 2023)]
    else:
        df_third_occurrences = df_player_logs.loc[
            (df_player_logs[column_name] <= value) & (df_player_logs['Year'] == 2023)]
    third_occurrence_percentage = round(((len(df_third_occurrences) / total_third_games) * 100), 1)
    json_output.update({'third_bet_occurrence': third_occurrence_percentage})


    df_last_four = df_player_logs.tail(4)
    if operator == 'over':
        df_last_four_occurrence = df_last_four.loc[df_last_four[column_name] > value]
    else:
        df_last_four_occurrence = df_last_four.loc[ df_player_logs[column_name] <= value]
    last_four_occur_percentage = round(((len(df_last_four_occurrence) / 4) * 100), 1)
    json_output.update({'last_four_bet_occurrence': last_four_occur_percentage})


    df_last_eight = df_player_logs.tail(8)
    if operator == 'over':
        df_last_eight_occurrence = df_last_eight.loc[df_last_eight[column_name] > value]
    else:
        df_last_eight_occurrence = df_last_eight.loc[ df_last_eight[column_name] <= value]
    last_eight_occur_percentage = round(((len(df_last_eight_occurrence) / 8) * 100), 1)
    json_output.update({'last_eight_bet_occurrence': last_eight_occur_percentage})


    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output




@nfl.route('/nfl/team_stats', methods=['GET'])
def nfl_team_stats():
    team_id = request.args.get('team_id', None)
    # stat = request.args.get('stat', None)
    connection = create_connection()
    cursor = connection.cursor()
    year_name_dict = {2022: 'third', 2023: 'prior', 2024: 'current'}
    loop_years = list(range(2019, 2025))
    rank_years = list(range(2022, 2025))
    json_output = {}

    query = f'''SELECT * FROM nfl_team_offense'''
    cursor.execute(query)
    cols = ['id', 'team_id', 'year', 'games', 'dvoa', 'epa_per_play', 'success_rate', 'dropback_epa', 'dropback_sr',
        'rush_epa', 'rush_sr', 'pass_comp', 'pass_att', 'pass_comp_percentage', 'pass_yards', 'pass_td', 'pass_td_percentage',
        'yards_per_att', 'pass_yards_per_comp', 'pass_yards_per_game', 'passer_rating', 'sacks', 'ints', 'int_percentage',
        'rush_att', 'rush_yards', 'rush_td', 'rush_yards_per_att', 'rush_yards_per_game', 'fumbles', 'points_per_game',
        'total_points', 'drives', 'plays', 'scoring_percentage', 'to_percentage', 'plays_per_drive', 'yards_per_drive',
        'points_per_drive', 'third_down_att', 'third_down_conv', 'third_down_conv_rate', 'fourth_down_att', 'fourth_down_conv',
        'fourth_down_conv_rate', 'rz_att', 'rz_td', 'rz_percentage']
    results = list(cursor.fetchall())

    df_off_hold = pd.DataFrame(results, columns=cols).reset_index(drop=True)

    # Rank data
    df_ranked = pd.DataFrame()
    for year in loop_years:
        df_rank = df_off_hold.copy()
        df_rank = df_rank.loc[df_rank['year'] == year]

        # rank pass stats
        df_rank["pass_comp rank"] = df_rank['pass_comp'].rank(ascending=False)
        df_rank["pass_yards rank"] = df_rank['pass_yards'].rank(ascending=False)
        df_rank["pass_td rank"] = df_rank['pass_td'].rank(ascending=False)
        df_rank["yards_per_att rank"] = df_rank['yards_per_att'].rank(ascending=False)
        df_rank["pass_yards_per_comp rank"] = df_rank['pass_yards_per_comp'].rank(ascending=False)
        df_rank["pass_yards_per_game rank"] = df_rank['pass_yards_per_game'].rank(ascending=False)

        # rank rush stats
        df_rank["rush_att rank"] = df_rank['rush_att'].rank(ascending=False)
        df_rank["rush_yards rank"] = df_rank['rush_yards'].rank(ascending=False)
        df_rank["rush_td rank"] = df_rank['rush_td'].rank(ascending=False)
        df_rank["rush_yards_per_att rank"] = df_rank['rush_yards_per_att'].rank(ascending=False)
        df_rank["rush_yards_per_game rank"] = df_rank['rush_yards_per_game'].rank(ascending=False)

        # rank per drive stats
        df_rank["points_per_game rank"] = df_rank['points_per_game'].rank(ascending=False)
        df_rank["total_points rank"] = df_rank['total_points'].rank(ascending=False)
        df_rank["plays_per_drive rank"] = df_rank['plays_per_drive'].rank(ascending=False)
        df_rank["yards_per_drive rank"] = df_rank['yards_per_drive'].rank(ascending=False)
        df_rank["points_per_drive rank"] = df_rank['points_per_drive'].rank(ascending=False)

        # rank red zone stats
        df_rank["rz_td rank"] = df_rank['rz_td'].rank(ascending=False)
        df_rank["rz_percentage rank"] = df_rank['rz_percentage'].rank(ascending=False)

        df_ranked = pd.concat([df_ranked, df_rank])
        print('==============================================')

    # Get offensive stats by year
    for year in rank_years:
        df_red_zone = df_ranked[['team_id', 'year', 'games', 'rz_td', 'rz_td rank', 'rz_percentage', 'rz_percentage rank']]
        df_red_zone = df_red_zone.loc[df_red_zone['team_id'] == int(team_id)]

        # get red zone data third year
        df_red_zone_third = df_red_zone.loc[df_red_zone['year'] == year]
        json_output.update({f"rz_td_{year_name_dict[year]}": df_red_zone_third['rz_td'].values.tolist()[0]})
        json_output.update({f"rz_td_rank_{year_name_dict[year]}": df_red_zone_third['rz_td rank'].values.tolist()[0]})
        json_output.update({f"rz_percentage_{year_name_dict[year]}": df_red_zone_third['rz_percentage'].values.tolist()[0]})
        json_output.update({f"rz_percentage_rank_{year_name_dict[year]}": df_red_zone_third['rz_percentage rank'].values.tolist()[0]})

        # PASSING DATA
        df_passing = df_ranked[['team_id', 'year', 'games', 'pass_comp', 'pass_comp rank', 'pass_yards', 'pass_yards rank',
                               'pass_td', 'pass_td rank', 'yards_per_att', 'yards_per_att rank', 'pass_yards_per_comp',
                               'pass_yards_per_comp rank', 'pass_yards_per_game', 'pass_yards_per_game rank']]
        df_passing = df_passing.loc[df_passing['team_id'] == int(team_id)]

        # get passing data third year
        df_passing_third = df_passing.loc[df_passing['year'] == year]
        json_output.update({f"pass_comp_{year_name_dict[year]}": df_passing_third['pass_comp'].values.tolist()[0]})
        json_output.update(
            {f"pass_comp_rank_{year_name_dict[year]}": df_passing_third['pass_comp rank'].values.tolist()[0]})
        json_output.update({f"pass_yards_{year_name_dict[year]}": df_passing_third['pass_yards'].values.tolist()[0]})
        json_output.update({f"pass_yards_rank_{year_name_dict[year]}": df_passing_third['pass_yards rank'].values.tolist()[0]})
        json_output.update({f"pass_td_{year_name_dict[year]}": df_passing_third['pass_td'].values.tolist()[0]})
        json_output.update({f"pass_td_rank_{year_name_dict[year]}": df_passing_third['pass_td rank'].values.tolist()[0]})
        json_output.update(
            {f"yards_per_att_{year_name_dict[year]}": df_passing_third['yards_per_att'].values.tolist()[0]})
        json_output.update(
            {f"yards_per_att_rank_{year_name_dict[year]}": df_passing_third['yards_per_att rank'].values.tolist()[0]})
        json_output.update(
            {f"pass_yards_per_comp_{year_name_dict[year]}": df_passing_third['pass_yards_per_comp'].values.tolist()[0]})
        json_output.update(
            {f"pass_yards_per_comp_rank_{year_name_dict[year]}": df_passing_third['pass_yards_per_comp rank'].values.tolist()[0]})
        json_output.update(
            {f"pass_yards_per_game_{year_name_dict[year]}": df_passing_third['pass_yards_per_game'].values.tolist()[0]})
        json_output.update(
            {f"pass_yards_per_game_rank_{year_name_dict[year]}": df_passing_third['pass_yards_per_game rank'].values.tolist()[0]})

        # RUSHING DATA
        df_rushing = df_ranked[['team_id', 'year', 'games', 'rush_att', 'rush_att rank', 'rush_yards', 'rush_yards rank',
                               'rush_td', 'rush_td rank', 'rush_yards_per_att', 'rush_yards_per_att rank', 'rush_yards_per_game',
                               'rush_yards_per_game rank']]
        df_rushing = df_rushing.loc[df_rushing['team_id'] == int(team_id)]

        # get rushing data third year
        df_rushing_third = df_rushing.loc[df_rushing['year'] == year]
        json_output.update(
            {f"rush_att_{year_name_dict[year]}": df_rushing_third['rush_att'].values.tolist()[0]})
        json_output.update(
            {"rush_att_rank_{year_name_dict[year]}": df_rushing_third['rush_att rank'].values.tolist()[0]})
        json_output.update(
            {f"rush_yards_{year_name_dict[year]}": df_rushing_third['rush_yards'].values.tolist()[0]})
        json_output.update(
            {f"rush_yards_rank_{year_name_dict[year]}": df_rushing_third['rush_yards rank'].values.tolist()[0]})
        json_output.update(
            {f"rush_td_{year_name_dict[year]}": df_rushing_third['rush_td'].values.tolist()[0]})
        json_output.update(
            {f"rush_td_rank_{year_name_dict[year]}": df_rushing_third['rush_td rank'].values.tolist()[0]})
        json_output.update(
            {f"rush_yards_per_att_{year_name_dict[year]}": df_rushing_third['rush_yards_per_att'].values.tolist()[0]})
        json_output.update(
            {f"rush_yards_per_att_{year_name_dict[year]}": df_rushing_third['rush_yards_per_att rank'].values.tolist()[0]})
        json_output.update(
            {f"rush_yards_per_game_{year_name_dict[year]}": df_rushing_third['rush_yards_per_game'].values.tolist()[0]})
        json_output.update(
            {f"rush_yards_per_game_rank_{year_name_dict[year]}": df_rushing_third['rush_yards_per_game rank'].values.tolist()[0]})

        # DRIVE DATA
        df_drive = df_ranked[['team_id', 'year', 'games', 'points_per_game', 'points_per_game rank', 'total_points',
                             'total_points rank', 'plays_per_drive', 'plays_per_drive rank', 'yards_per_drive', 'yards_per_drive rank',
                             'points_per_drive', 'points_per_drive rank']]
        df_drive = df_drive.loc[df_drive['team_id'] == int(team_id)]

        # get drive data third year
        df_drive_third = df_drive.loc[df_drive['year'] == year]
        json_output.update(
            {f"points_per_game_{year_name_dict[year]}": df_drive_third['points_per_game'].values.tolist()[0]})
        json_output.update(
            {f"points_per_game_rank_{year_name_dict[year]}": df_drive_third['points_per_game rank'].values.tolist()[0]})
        json_output.update(
            {f"total_points_{year_name_dict[year]}": df_drive_third['total_points'].values.tolist()[0]})
        json_output.update(
            {f"total_points_rank_{year_name_dict[year]}": df_drive_third['total_points rank'].values.tolist()[0]})
        json_output.update(
            {f"plays_per_drive_{year_name_dict[year]}":  df_drive_third['plays_per_drive'].values.tolist()[0]})
        json_output.update(
            {f"plays_per_drive_rank_{year_name_dict[year]}": df_drive_third['plays_per_drive rank'].values.tolist()[0]})
        json_output.update(
            {f"yards_per_drive_att_{year_name_dict[year]}": df_drive_third['yards_per_drive'].values.tolist()[0]})
        json_output.update(
            {f"yards_per_drive_att_{year_name_dict[year]}": df_drive_third['yards_per_drive rank'].values.tolist()[0]})
        json_output.update(
            {f"points_per_drive_{year_name_dict[year]}": df_drive_third['points_per_drive'].values.tolist()[0]})
        json_output.update(
            {f"points_per_drive_rank_{year_name_dict[year]}": df_drive_third['points_per_drive rank'].values.tolist()[0]})

    # Get teams standings over the past three years - current/prior/third
    standings_query = f'''select * from nfl_standings
                where team_id = %s'''
    vals = [team_id]
    cursor.execute(standings_query, vals)

    standing_results = list(cursor.fetchall())
    standing_cols = ['id', 'year', 'team_id', 'wins', 'losses', 'ties', 'win_loss_percentage', 'points_for', 'points_against',
                     'point_diff', 'avg_margin_of_victory', 'strength_of_schedule']
    df_standings_hold = pd.DataFrame(standing_results, columns=standing_cols).reset_index(drop=True)

    for year in rank_years:
        df_standings = df_standings_hold.loc[df_standings_hold['year'] == year]
        record = f"{df_standings['wins'].values.tolist()[0]}-{df_standings['losses'].values.tolist()[0]}-{df_standings['ties'].values.tolist()[0]}"
        json_output.update({f"team_record_{year_name_dict[year]}": record})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output

@nfl.route('/nfl/opponent_stats', methods=['GET'])
def nfl_opponent_information():
    # initialize variables
    team_id = request.args.get('team_id', None)
    player_id = request.args.get('id', None)
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = float(request.args.get('value', None))
    pos = request.args.get('position', None).upper()

    year_name_dict = {2022: 'third', 2023: 'prior', 2024: 'current'}
    loop_years = list(range(2019, 2025))
    rank_years = list(range(2022, 2025))

    json_output = {}

    if column_name in ['rush_att', 'rush_yards', 'rush_td', 'rush_longest']:
        limit_stat = 'rush_att'
    elif column_name in ['pass_att', 'pass_yards', 'pass_td', 'pass_longest']:
        limit_stat = 'pass_att'
    else:
        limit_stat = 'targets'

    # Get team defense and rank stats
    connection = create_connection()
    cursor = connection.cursor()
    team_def_query = f'''SELECT * FROM nfl_team_defense'''
    cursor.execute(team_def_query)

    team_def_results = list(cursor.fetchall())
    cols = ['id', 'team_id', 'year', 'games', 'dvoa', 'epa_per_play', 'success_rate', 'dropback_epa', 'dropback_sr',
        'rush_epa', 'rush_sr', 'pass_comp', 'pass_att', 'pass_comp_percentage', 'pass_yards', 'pass_td', 'pass_td_percentage',
        'yards_per_att', 'pass_yards_per_comp', 'pass_yards_per_game', 'passer_rating', 'qb_hits', 'sacks', 'ints', 'int_percentage',
        'pass_deflections', 'rush_att', 'rush_yards', 'rush_td', 'rush_yards_per_att', 'rush_yards_per_game', 'points_per_game',
        'total_points', 'drives', 'plays', 'scoring_percentage', 'to_percentage', 'plays_per_drive', 'yards_per_drive',
        'points_per_drive', 'third_down_att', 'third_down_conv', 'third_down_conv_rate', 'fourth_down_att', 'fourth_down_conv',
        'fourth_down_conv_rate', 'rz_att', 'rz_td', 'rz_percentage', 'qb_rush_att', 'qb_rush_yards', 'qb_rush_td',
        'rb_att', 'rb_yards', 'rb_td', 'rb_targets', 'rb_rec', 'rb_rec_yards', 'rb_rec_td', 'wr_targets','wr_rec',
        'wr_yards', 'wr_td', 'te_targets', 'te_rec', 'te_yards', 'te_td']
    df_def_hold = pd.DataFrame(team_def_results, columns=cols).reset_index(drop=True)

    # RANK COLUMNS AND ADD TO DATAFRAME
    df_ranked = pd.DataFrame()
    for year in loop_years:
        df_rank = df_def_hold.copy()
        df_rank = df_rank.loc[df_rank['year'] == year]

        # rank pass stats
        df_rank["pass_comp rank"] = df_rank['pass_comp'].rank()
        df_rank["pass_yards rank"] = df_rank['pass_yards'].rank()
        df_rank["pass_td rank"] = df_rank['pass_td'].rank()
        df_rank["yards_per_att rank"] = df_rank['yards_per_att'].rank()
        df_rank["pass_yards_per_comp rank"] = df_rank['pass_yards_per_comp'].rank()
        df_rank["pass_yards_per_game rank"] = df_rank['pass_yards_per_game'].rank()

        # rank rush stats
        df_rank["rush_att rank"] = df_rank['rush_att'].rank()
        df_rank["rush_yards rank"] = df_rank['rush_yards'].rank()
        df_rank["rush_td rank"] = df_rank['rush_td'].rank()
        df_rank["rush_yards_per_att rank"] = df_rank['rush_yards_per_att'].rank()
        df_rank["rush_yards_per_game rank"] = df_rank['rush_yards_per_game'].rank()

        # rank per drive stats
        df_rank["points_per_game rank"] = df_rank['points_per_game'].rank(ascending=True)
        df_rank["total_points rank"] = df_rank['total_points'].rank(ascending=True)
        df_rank["plays_per_drive rank"] = df_rank['plays_per_drive'].rank(ascending=True)
        df_rank["yards_per_drive rank"] = df_rank['yards_per_drive'].rank(ascending=True)
        df_rank["points_per_drive rank"] = df_rank['points_per_drive'].rank(ascending=True)

        # rank red zone stats
        df_rank["rz_td rank"] = df_rank['rz_td'].rank(ascending=True)
        df_rank["rz_percentage rank"] = df_rank['rz_percentage'].rank(ascending=True)

        df_ranked = pd.concat([df_ranked, df_rank])
        print('==============================================')

    for year in rank_years:
        # RED ZONE DATA
        df_red_zone = df_ranked[
            ['team_id', 'year', 'games', 'rz_td', 'rz_td rank', 'rz_percentage', 'rz_percentage rank']]
        df_red_zone = df_red_zone.loc[df_red_zone['team_id'] == int(team_id)]

        df_red_zone_third = df_red_zone.loc[df_red_zone['year'] == year]
        json_output.update({f"rz_td_{year_name_dict[year]}": df_red_zone_third['rz_td'].values.tolist()[0]})
        json_output.update({f"rz_td_rank_{year_name_dict[year]}": df_red_zone_third['rz_td rank'].values.tolist()[0]})
        json_output.update({f"rz_percentage_{year_name_dict[year]}": df_red_zone_third['rz_percentage'].values.tolist()[0]})
        json_output.update({f"rz_percentage_rank_{year_name_dict[year]}": df_red_zone_third['rz_percentage rank'].values.tolist()[0]})

        # PASSING DATA
        df_passing = df_ranked[['team_id', 'year', 'games', 'pass_comp', 'pass_comp rank', 'pass_yards', 'pass_yards rank',
                               'pass_td', 'pass_td rank', 'yards_per_att', 'yards_per_att rank', 'pass_yards_per_comp',
                               'pass_yards_per_comp rank', 'pass_yards_per_game', 'pass_yards_per_game rank']]
        df_passing = df_passing.loc[df_passing['team_id'] == int(team_id)]

        df_passing_third = df_passing.loc[df_passing['year'] == year]
        json_output.update({f"pass_comp_{year_name_dict[year]}": df_passing_third['pass_comp'].values.tolist()[0]})
        json_output.update({f"pass_comp_rank_{year_name_dict[year]}": df_passing_third['pass_comp rank'].values.tolist()[0]})
        json_output.update({f"pass_yards_{year_name_dict[year]}": df_passing_third['pass_yards'].values.tolist()[0]})
        json_output.update({f"pass_yards_rank_{year_name_dict[year]}": df_passing_third['pass_yards rank'].values.tolist()[0]})
        json_output.update({f"pass_td_{year_name_dict[year]}": df_passing_third['pass_td'].values.tolist()[0]})
        json_output.update({f"pass_td_rank_{year_name_dict[year]}": df_passing_third['pass_td rank'].values.tolist()[0]})
        json_output.update({f"yards_per_att_{year_name_dict[year]}": df_passing_third['yards_per_att'].values.tolist()[0]})
        json_output.update({f"yards_per_att_rank_{year_name_dict[year]}": df_passing_third['yards_per_att rank'].values.tolist()[0]})
        json_output.update({f"pass_yards_per_comp_{year_name_dict[year]}": df_passing_third['pass_yards_per_comp'].values.tolist()[0]})
        json_output.update({f"pass_yards_per_comp_rank_{year_name_dict[year]}": df_passing_third['pass_yards_per_comp rank'].values.tolist()[0]})
        json_output.update({f"pass_yards_per_game_{year_name_dict[year]}": df_passing_third['pass_yards_per_game'].values.tolist()[0]})
        json_output.update({f"pass_yards_per_game_rank_{year_name_dict[year]}": df_passing_third['pass_yards_per_game rank'].values.tolist()[0]})

        # RUSHING DATA
        df_rushing = df_ranked[['team_id', 'year', 'games', 'rush_att', 'rush_att rank', 'rush_yards', 'rush_yards rank',
                               'rush_td', 'rush_td rank', 'rush_yards_per_att', 'rush_yards_per_att rank', 'rush_yards_per_game',
                               'rush_yards_per_game rank']]
        df_rushing = df_rushing.loc[df_rushing['team_id'] == int(team_id)]

        df_rushing_third = df_rushing.loc[df_rushing['year'] == year]
        json_output.update({f"rush_att_{year_name_dict[year]}": df_rushing_third['rush_att'].values.tolist()[0]})
        json_output.update({f"rush_att_rank_{year_name_dict[year]}": df_rushing_third['rush_att rank'].values.tolist()[0]})
        json_output.update({f"rush_yards_{year_name_dict[year]}": df_rushing_third['rush_yards'].values.tolist()[0]})
        json_output.update({f"rush_yards_rank_{year_name_dict[year]}": df_rushing_third['rush_yards rank'].values.tolist()[0]})
        json_output.update({f"rush_td_{year_name_dict[year]}": df_rushing_third['rush_td'].values.tolist()[0]})
        json_output.update({f"rush_td_rank_{year_name_dict[year]}": df_rushing_third['rush_td rank'].values.tolist()[0]})
        json_output.update({f"rush_yards_per_att_{year_name_dict[year]}": df_rushing_third['rush_yards_per_att'].values.tolist()[0]})
        json_output.update({f"rush_yards_per_att_{year_name_dict[year]}": df_rushing_third['rush_yards_per_att rank'].values.tolist()[0]})
        json_output.update({f"rush_yards_per_game_{year_name_dict[year]}": df_rushing_third['rush_yards_per_game'].values.tolist()[0]})
        json_output.update({f"rush_yards_per_game_rank_{year_name_dict[year]}": df_rushing_third['rush_yards_per_game rank'].values.tolist()[0]})

        # DRIVE DATA
        df_drive = df_ranked[['team_id', 'year', 'games', 'points_per_game', 'points_per_game rank', 'total_points',
                             'total_points rank', 'plays_per_drive', 'plays_per_drive rank', 'yards_per_drive', 'yards_per_drive rank',
                             'points_per_drive', 'points_per_drive rank']]
        df_drive = df_drive.loc[df_drive['team_id'] == int(team_id)]

        df_drive_third = df_drive.loc[df_drive['year'] == year]
        json_output.update({f"points_per_game_{year_name_dict[year]}": df_drive_third['points_per_game'].values.tolist()[0]})
        json_output.update({f"points_per_game_rank_{year_name_dict[year]}": df_drive_third['points_per_game rank'].values.tolist()[0]})
        json_output.update({f"total_points_{year_name_dict[year]}": df_drive_third['total_points'].values.tolist()[0]})
        json_output.update({f"total_points_rank_{year_name_dict[year]}": df_drive_third['total_points rank'].values.tolist()[0]})
        json_output.update({f"plays_per_drive_{year_name_dict[year]}": df_drive_third['plays_per_drive'].values.tolist()[0]})
        json_output.update({f"plays_per_drive_rank_{year_name_dict[year]}": df_drive_third['plays_per_drive rank'].values.tolist()[0]})
        json_output.update({f"yards_per_drive_att_{year_name_dict[year]}": df_drive_third['yards_per_drive'].values.tolist()[0]})
        json_output.update({f"yards_per_drive_att_{year_name_dict[year]}": df_drive_third['yards_per_drive rank'].values.tolist()[0]})
        json_output.update({f"points_per_drive_{year_name_dict[year]}": df_drive_third['points_per_drive'].values.tolist()[0]})
        json_output.update({f"points_per_drive_rank_{year_name_dict[year]}": df_drive_third['points_per_drive rank'].values.tolist()[0]})

    # Get game logs where team was the opponent vs position
    opp_game_log_query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, team.name, nfl_player_stats.*
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN 
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    JOIN
                    team on team.id = nfl_player_stats.opp_id
                    WHERE nfl_player_stats.opp_id = %s'''
    vals = [team_id]
    cursor.execute(opp_game_log_query, vals)
    game_log_results = list(cursor.fetchall())

    game_log_cols = ['name', 'Year', 'Week', 'pos', 'opponent_name', 'id', 'game_id', 'player_id', 'team_id', 'opp_id',
                'pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest', 'ints', 'sacks', 'rush_att',
                'rush_yards', 'rush_td', 'rush_longest', 'targets', 'rec', 'rec_yards', 'rec_td', 'rec_longest', 'fumbles']
    df_game_logs = pd.DataFrame(game_log_results, columns=game_log_cols).reset_index(drop=True)

    df_pos = df_game_logs.loc[df_game_logs['pos'] == pos]
    for year in rank_years:
        df_bet = df_pos.loc[(df_pos['Year'] == year) & (df_pos[limit_stat] >= 1)]
        total_pos_faced_current = len(df_bet)

        if operator == 'under':
            df_bet = df_bet.loc[df_bet[column_name] < value]
            bet_allowed_current = len(df_bet)
        else:
            df_bet = df_bet.loc[df_bet[column_name] > value]
            bet_allowed_current = len(df_bet)

        df_bet = df_bet[
            ['name', 'Year', 'Week', 'pos', 'opponent_name', limit_stat, column_name]].reset_index(drop=True)

        json_output.update({f"opp_allowed_bet_{year_name_dict[year]}": round(((bet_allowed_current / total_pos_faced_current) * 100), 1)})
        json_output.update({f"opp_allowed_bet_log_{year_name_dict[year]}": df_bet.to_json()})

    # Get the game logs where the opponent played against the player
    log_vs_player_query = f'''SELECT
                    CONCAT(player.first_name, ' ', player.last_name) AS player_name, nfl_games.year, nfl_games.week,
                    player.position, team.name, nfl_player_stats.*
                    FROM
                    nfl_player_stats
                    JOIN
                    player ON player.id = nfl_player_stats.player_id
                    JOIN 
                    nfl_games on nfl_games.id = nfl_player_stats.game_id
                    JOIN
                    team on team.id = nfl_player_stats.opp_id
                    WHERE nfl_player_stats.opp_id = %s AND nfl_player_stats.player_id = %s'''
    vals = [team_id, player_id]
    cursor.execute(log_vs_player_query, vals)
    player_log_results = list(cursor.fetchall())

    log_vs_player_cols = ['name', 'Year', 'Week', 'pos', 'opponent_name', 'id', 'game_id', 'player_id', 'team_id', 'opp_id',
                     'pass_att', 'pass_comp', 'pass_yards', 'pass_td', 'pass_longest', 'ints', 'sacks', 'rush_att',
                     'rush_yards', 'rush_td', 'rush_longest', 'targets', 'rec', 'rec_yards', 'rec_td', 'rec_longest',
                     'fumbles']
    df_vs_player = pd.DataFrame(player_log_results, columns=log_vs_player_cols).reset_index(drop=True)

    df_vs_player = df_vs_player.reset_index(drop=True)
    json_output.update({f"player_game_logs_vs_opponent": df_vs_player.to_json()})

    # Get total touchdowns allowed to RB, TE, and WR
    for year in rank_years:
        df_rb = df_game_logs.loc[(df_game_logs['pos'] == 'RB') & (df_game_logs['Year'] ==  year)]
        rb_rush_td_total = df_rb['rush_td'].sum()
        rb_rec_td_total = df_rb['rec_td'].sum()
        json_output.update({f"rb_rush_td_total_{year_name_dict[year]}": int(rb_rush_td_total)})
        json_output.update({f"rb_rec_td_total_{year_name_dict[year]}": int(rb_rec_td_total)})

        df_wr = df_game_logs.loc[(df_game_logs['pos'] == 'WR') & (df_game_logs['Year'] ==  year)]
        wr_rush_td_total = df_wr['rush_td'].sum()
        wr_rec_td_total = df_wr['rec_td'].sum()
        json_output.update({f"wr_rush_td_total_{year_name_dict[year]}": int(wr_rush_td_total)})
        json_output.update({f"wr_rec_td_total_{year_name_dict[year]}": int(wr_rec_td_total)})

        df_qb = df_game_logs.loc[(df_game_logs['pos'] == 'QB') & (df_game_logs['Year'] ==  year)]
        qb_rush_td_total = df_qb['rush_td'].sum()
        json_output.update({f"qb_rush_td_total_{year_name_dict[year]}": int(qb_rush_td_total)})

        df_te = df_game_logs.loc[(df_game_logs['pos'] == 'QB') & (df_game_logs['Year'] ==  year)]
        te_rec_td_total = df_te['rush_td'].sum()
        json_output.update({f"te_rec_td_total_{year_name_dict[year]}": int(te_rec_td_total)})



    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output










# UPLOAD/ADD ROUTES
@nfl.route('/nfl/games', methods=['POST', 'PUT'])
def nfl_game_info():
    file = request.files['nfl_game_info']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add Games:
        if flask.request.method == 'POST':
            json_dict = {'week': int(row['week']), 'year': int(row['year']), 'home_id': int(row['home_id']), 'home_score': int(row['home_score']),
                'away_id ': int(row['away_id']), 'away_score': int(row['away_score']), 'winner': int(row['winner']),
                'margin_of_victory': int(row['margin_of_victory']), 'weather_id': int(row['weather_id']), 'vegas_line': row['vegas_line'],
                'vegas_line_result': row['vegas_line_result'], 'over_under': float(row['over_under']), 'total_points': int(row['total_points']),
                'over_under_result': row['over_under_result']}
            values = list(json_dict.values())
            print(values)

            cursor.execute('''INSERT INTO nfl_games (week, year, home_id, home_score, away_id, away_score, winner, 
            margin_of_victory, weather_id, vegas_line, vegas_line_result, over_under, total_points, over_under_result) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (values))

        # Update Game Info:
        elif flask.request.method == 'PUT':
            json_dict = {'week': int(row['week']), 'year': int(row['year']), 'home_score': int(row['home_score']),
                     'away_score': int(row['away_score']), 'winner': int(row['winner']), 'margin_of_victory': int(row['margin_of_victory']),
                     'weather_id': int(row['weather_id']), 'vegas_line': row['vegas_line'], 'vegas_line_result': row['vegas_line_result'],
                     'over_under': float(row['over_under']), 'total_points': int(row['total_points']),
                     'over_under_result': row['over_under_result'], 'id': int(row['id']), 'home_id': int(row['home_id']),
                     'away_id': int(row['away_id'])}
            values = list(json_dict.values())

            cursor.execute('''UPDATE nfl_games
                    SET week = %s, year = %s, home_score = %s, away_score = %s, winner = %s, margin_of_victory = %s, weather_id = %s, vegas_line = %s,
                    vegas_line_result = %s, over_under = %s, total_points = %s, over_under_result = %s
                    WHERE nfl_games.id = %s AND nfl_games.home_id = %s AND nfl_games.away_id = %s''', (values))

        connection.commit()

    return f"nfl_games has been updated with the most recent game data."

@nfl.route('/nfl/team_defense', methods=['POST', 'PUT'])
def nfl_team_defense():
    file = request.files['nfl_team_defense']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add data
        if flask.request.method == 'POST':
            json_dict = {'team_id': row['team_id'], 'year': row['year'], 'games': row['games'],

                     'dvoa': row['dvoa'], 'epa_per_play': row['epa_per_play'], 'success_rate': row['success_rate'],
                     'dropback_epa': row['dropback_epa'], 'dropback_sr': row['dropback_sr'], 'rush_epa': row['rush_epa'],
                     'rush_sr': row['rush_sr'],

                     'pass_comp': row['pass_comp'], 'pass_att': row['pass_att'], 'pass_comp_percentage': row['pass_comp_percentage'],
                     'pass_yards': row['pass_yards'], 'pass_td': row['pass_td'], 'pass_td_percentage': row['pass_td_percentage'],
                     'yards_per_att': row['yards_per_att'],  'pass_yards_per_comp': row['pass_yards_per_comp'],
                     'pass_yards_per_game': row['pass_yards_per_game'], 'passer_rating': row['passer_rating'],
                     'qb_hits': row['qb_hits'], 'sacks': row['sacks'], 'ints': row['ints'], 'int_percentage': row['int_percentage'],
                     'pass_deflections': row['pass_deflections'],

                     'rush_att': row['rush_att'], 'rush_yards': row['rush_yards'], 'rush_td': row['rush_td'],
                     'rush_yards_per_att': row['rush_yards_per_att'], 'rush_yards_per_game': row['rush_yards_per_game'],

                     'points_per_game': row['points_per_game'], 'total_points': row['total_points'], 'drives': row['drives'],
                     'plays': row['plays'], 'scoring_percentage': row['scoring_percentage'], 'to_percentage': row['to_percentage'],
                     'plays_per_drive': row['plays_per_drive'], 'yards_per_drive': row['yards_per_drive'],
                     'points_per_drive': row['points_per_drive'],

                     'third_down_att': row['third_down_att'], 'third_down_conv': row['third_down_conv'],
                     'third_down_conv_rate': row['third_down_conv_rate'], 'fourth_down_att': row['fourth_down_att'],
                     'fourth_down_conv': row['fourth_down_conv'], 'fourth_down_conv_rate': row['fourth_down_conv_rate'],

                     'rz_att': row['rz_att'], 'rz_td': row['rz_td'], 'rz_percentage': row['rz_percentage'],

                     'qb_rush_att': row['qb_rush_att'], 'qb_rush_yards': row['qb_rush_yards'], 'qb_rush_td': row['qb_rush_td'],
                     'rb_att': row['rb_att'], 'rb_yards': row['rb_yards'], 'rb_td': row['rb_td'], 'rb_targets': row['rb_targets'],
                     'rb_rec': row['rb_rec'], 'rb_rec_yards': row['rb_rec_yards'], 'rb_rec_td': row['rb_rec_td'],
                     'wr_targets': row['wr_targets'], 'wr_rec': row['wr_rec'], 'wr_yards': row['wr_yards'], 'wr_td': row['wr_td'],
                     'te_targets': row['te_targets'], 'te_rec': row['te_rec'], 'te_yards': row['te_yards'], 'te_td': row['te_td']}
            values = list(json_dict.values())

            cursor.execute('''INSERT INTO nfl_team_defense (team_id, year, games, dvoa, epa_per_play, success_rate, dropback_epa, 
            dropback_sr, rush_epa, rush_sr, pass_comp, pass_att, pass_comp_percentage, pass_yards, pass_td, pass_td_percentage,
            yards_per_att, pass_yards_per_comp, pass_yards_per_game, passer_rating, qb_hits, sacks, ints, int_percentage, 
            pass_deflections, rush_att, rush_yards, rush_td, rush_yards_per_att, rush_yards_per_game, points_per_game, total_points, 
            drives, plays, scoring_percentage, to_percentage, plays_per_drive, yards_per_drive, points_per_drive, third_down_att,
            third_down_conv, third_down_conv_rate, fourth_down_att, fourth_down_conv, fourth_down_conv_rate, rz_att, rz_td, 
            rz_percentage, qb_rush_att, qb_rush_yards, qb_rush_td, rb_att, rb_yards, rb_td, rb_targets, rb_rec, rb_rec_yards,
            rb_rec_td, wr_targets, wr_rec, wr_yards, wr_td, te_targets, te_rec, te_yards, te_td) VALUES (%s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s)''', (values))

        # Update data
        elif flask.request.method == 'PUT':
            json_dict = {'games': row['games'],

                         'dvoa': row['dvoa'], 'epa_per_play': row['epa_per_play'], 'success_rate': row['success_rate'],
                         'dropback_epa': row['dropback_epa'], 'dropback_sr': row['dropback_sr'], 'rush_epa': row['rush_epa'],
                         'rush_sr': row['rush_sr'],

                         'pass_comp': row['pass_comp'], 'pass_att': row['pass_att'], 'pass_comp_percentage': row['pass_comp_percentage'],
                         'pass_yards': row['pass_yards'], 'pass_td': row['pass_td'], 'pass_td_percentage': row['pass_td_percentage'],
                         'yards_per_att': row['yards_per_att'], 'pass_yards_per_comp': row['pass_yards_per_comp'],
                         'pass_yards_per_game': row['pass_yards_per_game'], 'passer_rating': row['passer_rating'],
                         'qb_hits': row['qb_hits'], 'sacks': row['sacks'], 'ints': row['ints'], 'int_percentage': row['int_percentage'],
                         'pass_deflections': row['pass_deflections'],

                         'rush_att': row['rush_att'], 'rush_yards': row['rush_yards'], 'rush_td': row['rush_td'],
                         'rush_yards_per_att': row['rush_yards_per_att'], 'rush_yards_per_game': row['rush_yards_per_game'],

                         'points_per_game': row['points_per_game'], 'total_points': row['total_points'], 'drives': row['drives'],
                         'plays': row['plays'], 'scoring_percentage': row['scoring_percentage'], 'to_percentage': row['to_percentage'],
                         'plays_per_drive': row['plays_per_drive'], 'yards_per_drive': row['yards_per_drive'],
                         'points_per_drive': row['points_per_drive'],

                         'third_down_att': row['third_down_att'], 'third_down_conv': row['third_down_conv'],
                         'third_down_conv_rate': row['third_down_conv_rate'], 'fourth_down_att': row['fourth_down_att'],
                         'fourth_down_conv': row['fourth_down_conv'], 'fourth_down_conv_rate': row['fourth_down_conv_rate'],

                         'rz_att': row['rz_att'], 'rz_td': row['rz_td'], 'rz_percentage': row['rz_percentage'],

                         'qb_rush_att': row['qb_rush_att'], 'qb_rush_yards': row['qb_rush_yards'], 'qb_rush_td': row['qb_rush_td'],
                         'rb_att': row['rb_att'], 'rb_yards': row['rb_yards'], 'rb_td': row['rb_td'],'rb_targets': row['rb_targets'],
                         'rb_rec': row['rb_rec'], 'rb_rec_yards': row['rb_rec_yards'], 'rb_rec_td': row['rb_rec_td'],
                         'wr_targets': row['wr_targets'], 'wr_rec': row['wr_rec'], 'wr_yards': row['wr_yards'], 'wr_td': row['wr_td'],
                         'te_targets': row['te_targets'], 'te_rec': row['te_rec'], 'te_yards': row['te_yards'], 'te_td': row['te_td'],

                         'team_id': row['team_id'], 'year': row['year']}
            values = list(json_dict.values())
            print(values)

            cursor.execute("""UPDATE nfl_team_defense
                SET games = %s, dvoa = %s, epa_per_play = %s, success_rate = %s, dropback_epa = %s, dropback_sr = %s, rush_epa = %s, 
                rush_sr = %s, pass_comp = %s, pass_att = %s, pass_comp_percentage = %s, pass_yards = %s, pass_td = %s, 
                pass_td_percentage = %s, yards_per_att = %s, pass_yards_per_comp = %s, pass_yards_per_game = %s, passer_rating = %s, 
                qb_hits = %s, sacks = %s, ints = %s, int_percentage = %s, pass_deflections = %s, rush_att = %s, rush_yards = %s,
                rush_td = %s, rush_yards_per_att = %s, rush_yards_per_game = %s, points_per_game = %s, total_points = %s, drives = %s, 
                plays = %s, scoring_percentage = %s, to_percentage = %s, plays_per_drive = %s, yards_per_drive = %s, points_per_drive = %s,
                third_down_att = %s, third_down_conv = %s, third_down_conv_rate = %s, fourth_down_att = %s, fourth_down_conv = %s,
                fourth_down_conv_rate = %s, rz_att = %s, rz_td = %s, rz_percentage = %s, qb_rush_att = %s, qb_rush_yards = %s,
                qb_rush_td = %s, rb_att = %s, rb_yards = %s, rb_td = %s, rb_targets = %s, rb_rec = %s, rb_rec_yards = %s,
                rb_rec_td = %s, wr_targets = %s, wr_rec = %s, wr_yards = %s, wr_td = %s, te_targets = %s, te_rec = %s, te_yards = %s, te_td = %s
                WHERE nfl_team_defense.team_id = %s AND nfl_team_defense.year = %s""", (values))

        connection.commit()

    return f"nfl_team_defense has been updated with the most recent years data."

@nfl.route('/nfl/team_offense', methods=['POST', 'PUT'])
def nfl_team_offense():
    file = request.files['nfl_team_offense']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add data
        if flask.request.method == 'POST':
            json_dict = {'team_id': row['team_id'],
                         'year': row['year'],
                         'games': row['games'],
                         'dvoa': row['dvoa'],
                         'epa_per_play': row['epa_per_play'],
                         'success_rate': row['success_rate'],
                         'dropback_epa': row['dropback_epa'],
                         'dropback_sr': row['dropback_sr'],
                         'rush_epa': row['rush_epa'],
                         'rush_sr': row['rush_sr'],
                         'pass_comp': row['pass_comp'],
                         'pass_att': row['pass_att'],
                         'pass_comp_percentage': row['pass_comp_percentage'],
                         'pass_yards': row['pass_yards'],
                         'pass_td': row['pass_td'],
                         'pass_td_percentage': row['pass_td_percentage'],
                         'yards_per_att': row['yards_per_att'],
                         'pass_yards_per_comp': row['pass_yards_per_comp'],
                         'pass_yards_per_game': row['pass_yards_per_game'],
                         'passer_rating': row['passer_rating'],
                         'sacks': row['sacks'],
                         'ints': row['ints'],
                         'int_percentage': row['int_percentage'],
                         'rush_att': row['rush_att'],
                         'rush_yards': row['rush_yards'],
                         'rush_td': row['rush_td'],
                         'rush_yards_per_att': row['rush_yards_per_att'],
                         'rush_yards_per_game': row['rush_yards_per_game'],
                         'fumbles': row['fumbles'],
                         'points_per_game': row['points_per_game'],
                         'total_points': row['total_points'],
                         'drives': row['drives'],
                         'plays': row['plays'],
                         'scoring_percentage': row['scoring_percentage'],
                         'to_percentage': row['to_percentage'],
                         'plays_per_drive': row['plays_per_drive'],
                         'yards_per_drive': row['yards_per_drive'],
                         'points_per_drive': row['points_per_drive'],
                         'third_down_att': row['third_down_att'],
                         'third_down_conv': row['third_down_conv'],
                         'third_down_conv_rate': row['third_down_conv_rate'],
                         'fourth_down_att': row['fourth_down_att'],
                         'fourth_down_conv': row['fourth_down_conv'],
                         'fourth_down_conv_rate': row['fourth_down_conv_rate'],
                         'rz_att': row['rz_att'],
                         'rz_td': row['rz_td'],
                         'rz_percentage': row['rz_percentage']}
            values = list(json_dict.values())

            cursor.execute("""INSERT INTO nfl_team_offense (team_id, year, games, dvoa, epa_per_play, success_rate,
             dropback_epa, dropback_sr, rush_epa, rush_sr, pass_comp, pass_att, pass_comp_percentage, pass_yards, pass_td, 
             pass_td_percentage, yards_per_att, pass_yards_per_comp, pass_yards_per_game, passer_rating, sacks, ints, 
             int_percentage, rush_att, rush_yards, rush_td, rush_yards_per_att, rush_yards_per_game, fumbles, total_points,
             points_per_game, drives, plays, scoring_percentage, to_percentage, plays_per_drive, yards_per_drive, points_per_drive,
             third_down_att, third_down_conv, third_down_conv_rate, fourth_down_att,fourth_down_conv, fourth_down_conv_rate, rz_att, rz_td, rz_percentage) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

        # Update Data
        elif flask.request.method == 'PUT':
            json_dict = {'games': row['games'],
                         'dvoa': row['dvoa'],
                         'epa_per_play': row['epa_per_play'],
                         'success_rate': row['success_rate'],
                         'dropback_epa': row['dropback_epa'],
                         'dropback_sr': row['dropback_sr'],
                         'rush_epa': row['rush_epa'],
                         'rush_sr': row['rush_sr'],
                         'pass_comp': row['pass_comp'],
                         'pass_att': row['pass_att'],
                         'pass_comp_percentage': row['pass_comp_percentage'],
                         'pass_yards': row['pass_yards'],
                         'pass_td': row['pass_td'],
                         'pass_td_percentage': row['pass_td_percentage'],
                         'yards_per_att': row['yards_per_att'],
                         'pass_yards_per_comp': row['pass_yards_per_comp'],
                         'pass_yards_per_game': row['pass_yards_per_game'],
                         'passer_rating': row['passer_rating'],
                         'sacks': row['sacks'],
                         'ints': row['ints'],
                         'int_percentage': row['int_percentage'],
                         'rush_att': row['rush_att'],
                         'rush_yards': row['rush_yards'],
                         'rush_td': row['rush_td'],
                         'rush_yards_per_att': row['rush_yards_per_att'],
                         'rush_yards_per_game': row['rush_yards_per_game'],
                         'fumbles': row['fumbles'],
                         'points_per_game': row['points_per_game'],
                         'total_points': row['total_points'],
                         'drives': row['drives'],
                         'plays': row['plays'],
                         'scoring_percentage': row['scoring_percentage'],
                         'to_percentage': row['to_percentage'],
                         'plays_per_drive': row['plays_per_drive'],
                         'yards_per_drive': row['yards_per_drive'],
                         'points_per_drive': row['points_per_drive'],
                         'third_down_att': row['third_down_att'],
                         'third_down_conv': row['third_down_conv'],
                         'third_down_conv_rate': row['third_down_conv_rate'],
                         'fourth_down_att': row['fourth_down_att'],
                         'fourth_down_conv': row['fourth_down_conv'],
                         'fourth_down_conv_rate': row['fourth_down_conv_rate'],
                         'rz_att': row['rz_att'], 'rz_td': row['rz_td'],
                         'rz_percentage': row['rz_percentage'],
                         'team_id': row['team_id'],
                         'year': row['year']}
            values = list(json_dict.values())

            cursor.execute("""UPDATE nfl_team_offense 
                    SET games = %s, dvoa = %s, epa_per_play = %s, success_rate = %s, dropback_epa = %s, dropback_sr = %s, 
                    rush_epa = %s, rush_sr = %s, pass_comp = %s, pass_att = %s, pass_comp_percentage = %s, pass_yards = %s, 
                    pass_td = %s, pass_td_percentage = %s, yards_per_att = %s, pass_yards_per_comp = %s, pass_yards_per_game = %s,
                    passer_rating = %s, sacks = %s, ints = %s, int_percentage = %s, rush_att = %s, rush_yards = %s, 
                    rush_td = %s, rush_yards_per_att = %s, rush_yards_per_game = %s, fumbles = %s, total_points = %s,
                    points_per_game = %s, drives = %s, plays = %s, scoring_percentage = %s, to_percentage = %s, plays_per_drive = %s, 
                    yards_per_drive = %s, points_per_drive = %s, third_down_att = %s, third_down_conv = %s, third_down_conv_rate = %s, 
                    fourth_down_att = %s, fourth_down_conv = %s, fourth_down_conv_rate = %s, rz_att = %s, rz_td = %s, rz_percentage = %s
                    WHERE nfl_team_offense.team_id = %s AND nfl_team_offense.year = %s""",(values))

        connection.commit()

    return f"nfl_team_offense has been updated with the most recent years data."

@nfl.route('/nfl/standings', methods=['POST', 'PUT'])
def nfl_standings():
    file = request.files['nfl_standings']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add data
        if flask.request.method == 'POST':
            json_dict = {'year': row['year'],
                         'team_id': row['team_id'],
                         'wins': row['wins'],
                         'losses': row['losses'],
                         'ties': row['ties'],
                         'win_loss_percentage': row['win_loss_percentage'],
                         'points_for': row['points_for'],
                         'points_against': row['points_against'],
                         'point_diff': row['point_diff'],
                         'avg_margin_of_victory': row['avg_margin_of_victory'],
                         'strength_of_schedule': row['strength_of_schedule']}
            values = list(json_dict.values())

            cursor.execute("""INSERT INTO nfl_standings (year, team_id, wins, losses, ties, win_loss_percentage, points_for, 
                            points_against, point_diff,
                            avg_margin_of_victory, strength_of_schedule) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (values))
        # Update Data
        elif flask.request.method == 'PUT':
            json_dict = {'wins': row['wins'],
                         'losses': row['losses'],
                         'ties': row['ties'],
                         'win_loss_percentage': row['win_loss_percentage'],
                         'points_for': row['points_for'],
                         'points_against': row['points_against'],
                         'point_diff': row['point_diff'],
                         'avg_margin_of_victory': row['avg_margin_of_victory'],
                         'strength_of_schedule': row['strength_of_schedule'],
                         'team_id': row['team_id'],
                         'year': row['year']}
            values = list(json_dict.values())

            cursor.execute("""UPDATE  nfl_standings 
                        SET wins = %s, losses = %s, ties = %s, win_loss_percentage = %s, points_for = %s,
                         points_against = %s, point_diff = %s, avg_margin_of_victory = %s, strength_of_schedule = %s
                        WHERE nfl_standings.team_id = %s and nfl_standings.year = %s""", (values))

        connection.commit()

    return f"nfl_team_offense has been updated with the most recent years data."

@nfl.route('/nfl/red_zone', methods=['POST', 'PUT'])
def nfl_red_zone():
    file = request.files['nfl_red_zone']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        # Add data
        if flask.request.method == 'POST':
            json_dict = {'player_id': row['player_id'],
                         'year': row['year'],
                         'rz_20_pass_att': row['rz_20_pass_att'],
                         'rz_20_pass_comp': row['rz_20_pass_comp'],
                         'rz_20_comp_percentage': row['rz_20_comp_percentage'],
                         'rz_20_pass_yards': row['rz_20_pass_yards'],
                         'rz_20_pass_td': row['rz_20_pass_td'],
                         'rz_20_pass_int': row['rz_20_pass_int'],
                         'rz_10_pass_att': row['rz_10_pass_att'],
                         'rz_10_pass_comp': row['rz_10_pass_comp'],
                         'rz_10_comp_percentage': row['rz_10_comp_percentage'],
                         'rz_10_pass_yards': row['rz_10_pass_yards'],
                         'rz_10_pass_td': row['rz_10_pass_td'],
                         'rz_10_pass_int': row['rz_10_pass_int'],
                         'rz_20_targets': row['rz_20_targets'],
                         'rz_20_receptions': row['rz_20_receptions'],
                         'rz_20_rec_yards': row['rz_20_rec_yards'],
                         'rz_20_catch_percentage': row['rz_20_catch_percentage'],
                         'rz_20_rec_td': row['rz_20_rec_td'],
                         'rz_20_target_percentage': row['rz_20_target_percentage'],
                         'rz_10_targets': row['rz_10_targets'],
                         'rz_10_receptions': row['rz_10_receptions'],
                         'rz_10_rec_yards': row['rz_10_rec_yards'],
                         'rz_10_catch_percentage': row['rz_10_catch_percentage'],
                         'rz_10_rec_td': row['rz_10_rec_td'],
                         'rz_10_target_percentage': row['rz_10_target_percentage'],
                         'rz_20_rush_att': row['rz_20_rush_att'],
                         'rz_20_rush_yards': row['rz_20_rush_yards'],
                         'rz_20_rush_td': row['rz_20_rush_td'],
                         'rz_20_rush_percentage': row['rz_20_rush_percentage'],
                         'rz_10_rush_att': row['rz_10_rush_att'],
                         'rz_10_rush_yards': row['rz_10_rush_yards'],
                         'rz_10_rush_td': row['rz_10_rush_td'],
                         'rz_10_rush_percentage': row['rz_10_rush_percentage'],
                         'rz_5_rush_att': row['rz_5_rush_att'],
                         'rz_5_rush_yards': row['rz_5_rush_yards'],
                         'rz_5_rush_td': row['rz_5_rush_td'],
                         'rz_5_rush_percentage': row['rz_5_rush_percentage']}
            values = list(json_dict.values())

            cursor.execute("""INSERT INTO nfl_redzone_stats (player_id, year, rz_20_pass_att, rz_20_pass_comp, rz_20_comp_percentage,
                 rz_20_pass_yards, rz_20_pass_td, rz_20_pass_int, rz_10_pass_att, rz_10_pass_comp, rz_10_comp_percentage, 
                 rz_10_pass_yards, rz_10_pass_td, rz_10_pass_int, rz_20_targets, rz_20_receptions, rz_20_rec_yards, 
                 rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions, rz_10_rec_yards,
                 rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_yards, rz_20_rush_td,
                 rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_yards, rz_10_rush_td, rz_10_rush_percentage, rz_5_rush_att, 
                 rz_5_rush_yards, rz_5_rush_td, rz_5_rush_percentage) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (values))

        # Update Data
        elif flask.request.method == 'PUT':
            json_dict = {'rz_20_pass_att': row['rz_20_pass_att'],
                         'rz_20_pass_comp': row['rz_20_pass_comp'],
                         'rz_20_comp_percentage': row['rz_20_comp_percentage'],
                         'rz_20_pass_yards': row['rz_20_pass_yards'],
                         'rz_20_pass_td': row['rz_20_pass_td'],
                         'rz_20_pass_int': row['rz_20_pass_int'],
                         'rz_10_pass_att': row['rz_10_pass_att'],
                         'rz_10_pass_comp': row['rz_10_pass_comp'],
                         'rz_10_comp_percentage': row['rz_10_comp_percentage'],
                         'rz_10_pass_yards': row['rz_10_pass_yards'],
                         'rz_10_pass_td': row['rz_10_pass_td'],
                         'rz_10_pass_int': row['rz_10_pass_int'],
                         'rz_20_targets': row['rz_20_targets'],
                         'rz_20_receptions': row['rz_20_receptions'],
                         'rz_20_rec_yards': row['rz_20_rec_yards'],
                         'rz_20_catch_percentage': row['rz_20_catch_percentage'],
                         'rz_20_rec_td': row['rz_20_rec_td'],
                         'rz_20_target_percentage': row['rz_20_target_percentage'],
                         'rz_10_targets': row['rz_10_targets'],
                         'rz_10_receptions': row['rz_10_receptions'],
                         'rz_10_rec_yards': row['rz_10_rec_yards'],
                         'rz_10_catch_percentage': row['rz_10_catch_percentage'],
                         'rz_10_rec_td': row['rz_10_rec_td'],
                         'rz_10_target_percentage': row['rz_10_target_percentage'],
                         'rz_20_rush_att': row['rz_20_rush_att'],
                         'rz_20_rush_yards': row['rz_20_rush_yards'],
                         'rz_20_rush_td': row['rz_20_rush_td'],
                         'rz_20_rush_percentage': row['rz_20_rush_percentage'],
                         'rz_10_rush_att': row['rz_10_rush_att'],
                         'rz_10_rush_yards': row['rz_10_rush_yards'],
                         'rz_10_rush_td': row['rz_10_rush_td'],
                         'rz_10_rush_percentage': row['rz_10_rush_percentage'],
                         'rz_5_rush_att': row['rz_5_rush_att'],
                         'rz_5_rush_yards': row['rz_5_rush_yards'],
                         'rz_5_rush_td': row['rz_5_rush_td'],
                         'rz_5_rush_percentage': row['rz_5_rush_percentage'],
                         'player_id': row['player_id'],
                         'year': row['year']}
            values = list(json_dict.values())

            cursor.execute("""UPDATE nfl_redzone_stats 
                    SET rz_20_pass_att = %s, rz_20_pass_comp = %s, rz_20_comp_percentage = %s, rz_20_pass_yards = %s, rz_20_pass_td = %s, rz_20_pass_int = %s,
                        rz_10_pass_att = %s, rz_10_pass_comp = %s, rz_10_comp_percentage = %s, rz_10_pass_yards = %s, rz_10_pass_td = %s, 
                        rz_10_pass_int = %s, rz_20_targets = %s, rz_20_receptions = %s, rz_20_rec_yards = %s, rz_20_catch_percentage = %s, 
                        rz_20_rec_td = %s, rz_20_target_percentage = %s, rz_10_targets = %s, rz_10_receptions = %s, rz_10_rec_yards = %s, 
                        rz_10_catch_percentage = %s, rz_10_rec_td = %s, rz_10_target_percentage = %s, rz_20_rush_att = %s, rz_20_rush_td = %s,
                        rz_20_rush_yards = %s, rz_20_rush_percentage = %s, rz_10_rush_att = %s, rz_10_rush_td = %s, rz_10_rush_yards = %s, 
                        rz_10_rush_percentage = %s, rz_5_rush_att = %s, rz_5_rush_td = %s, rz_5_rush_yards = %s, rz_5_rush_percentage = %s 
                    WHERE nfl_redzone_stats.player_id = %s AND nfl_redzone_stats.year = %s""", (values))

        connection.commit()

    return f"nfl_redzone_stats has been updated with the most recent years data."

@nfl.route('/nfl/player_stats', methods=['POST'])
def nfl_player_stats():
    file = request.files['nfl_game_log']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        json_dict = {'game_id': int(row['game_id']),
                     'player_id': int(row['player_id']),
                     'team_id': int(row['team_id']),
                     'opp_id': int(row['opp_id']),
                     'pass_att': int(row['pass_att']),
                     'pass_comp': int(row['pass_comp']),
                     'pass_yards': int(row['pass_yards']),
                     'pass_td': int(row['pass_td']),
                     'pass_longest': int(row['pass_longest']),
                     'int': int(row['int']),
                     'sacks': int(row['sacks']),
                     'rush_att': int(row['rush_att']),
                     'rush_yards': int(row['rush_yards']),
                     'rush_td': int(row['rush_td']),
                     'rush_longest': int(row['rush_longest']),
                     'targets': int(row['targets']),
                     'rec': int(row['rec']),
                     'rec_yards': int(row['rec_yards']),
                     'rec_td': int(row['rec_td']),
                     'rec_longest': int(row['rec_longest']),
                     'fumbles': int(row['fumbles'])}
        values = list(json_dict.values())

        cursor.execute("""INSERT INTO nfl_player_stats (game_id, player_id, team_id, opp_id, pass_att, pass_comp, pass_yards, pass_td, pass_longest, 
                        ints, sacks, rush_att, rush_yards, rush_td, rush_longest, targets, rec, rec_yards, rec_td, rec_longest, fumbles) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       (values))

        connection.commit()
        print(f"game_stats have been added to nfl_player_stats table.")


    return f"nfl_player_stats has been u[dated ."


@nfl.route('/nfl/weekly_rank', methods=['POST'])
def nfl_weekly_ranks():
    file = request.files['nfl_weekly_rank']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        json_dict = {'team_id': int(row['team_id']),
                     'year': int(row['year']),
                     'week': int(row['week']),
                     'pass_att': int(row['pass_att']),
                     'pass_comp': int(row['pass_comp']),
                     'pass_yards': int(row['pass_yards']),
                     'pass_td': int(row['pass_td']),
                     'rush_att': int(row['rush_att']),
                     'rush_yards': int(row['rush_yards']),
                     'rush_td': int(row['rush_td']),
                     'targets': int(row['targets']),
                     'rec': int(row['rec']),
                     'rec_yards': int(row['rec_yards']),
                     'rec_td': int(row['rec_td']),
                     'pyards_per_att': float(row['pyards_per_att']),
                     'ryards_per_att': float(row['ryards_per_att']),
                     'ryards_per_recs': float(row['ryards_per_recs']),
                     'pass_td_per_att': float(row['pass_td_per_att']),
                     'rush_td_per_att': float(row['rush_td_per_att']),
                     'rec_td_per_rec': float(row['rec_td_per_rec']),
                     'pass_yards_rank': int(row['pass_yards_rank']),
                     'rush_yards_rank': int(row['rush_yards_rank']),
                     'rec_yards_rank': int(row['rec_yards_rank']),
                     'pass_td_rank': int(row['pass_td_rank']),
                     'rush_td_rank': int(row['rush_td_rank']),
                     'rec_td_rank': int(row['rec_td_rank']),
                     'pass_comp_rank': int(row['pass_comp_rank']),
                     'rush_att_rank': int(row['rush_att_rank']),
                     'rec_rank': int(row['rec_rank']),
                     'pass_yars_per_att_rank': int(row['pass_yars_per_att_rank']),
                     'rush_yars_per_att_rank': int(row['rush_yars_per_att_rank']),
                     'rec_yars_per_rec_rank': int(row['rec_yars_per_rec_rank'])}
        values = list(json_dict.values())

        cursor.execute("""INSERT INTO nfl_weekly_rank (team_id, year, week, pass_att, pass_comp, pass_yards,
         pass_td, rush_att, rush_yards, rush_td, targets, rec, rec_yards, rec_td, pyards_per_att, 
         ryards_per_att, ryards_per_recs, pass_td_per_att, rush_td_per_att, rec_td_per_rec, pass_yards_rank, 
         rush_yards_rank, rec_yards_rank, pass_td_rank, rush_td_rank, rec_td_rank, pass_comp_rank,
         rush_att_rank, rec_rank, pass_yars_per_att_rank, rush_yars_per_att_rank, rec_yars_per_rec_rank) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       (values))

        connection.commit()
        print(f"game_stats have been added to nfl_player_stats table.")


    return f"nfl_weekly_rank has been updated ."
