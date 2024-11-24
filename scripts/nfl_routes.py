import pandas as pd
import numpy as np
import statistics

from .db import create_connection
from flask import Blueprint, request, jsonify

nfl = Blueprint("nfl", __name__)
pd.set_option('display.max_columns', 100)


@nfl.route('nfl/player_logs', methods=['GET'])
def nfl_player_logs():
    player_id = request.args.get('id', None)
    column_name = request.args.get('stat', None)
    operator = request.args.get('operator', None)
    value = float(request.args.get('value', None))
    loop_years = list(range(2019, 2025))
    rank_years = list(range(2022, 2025))

    limit_stat_dict = {'pass_att': 'pass_att', 'pass_yards': 'pass_att', 'pass_td': 'pass_att', 'pass_comp': 'pass_att',
                       'rush_att': 'rush_att', 'rush_yards': 'rush_att', 'rush_td': 'rush_att',
                       'rec': 'targets', 'targets': 'targets', 'rec_yards': 'targets', 'rec_td': 'targets',}
    limit_stat = limit_stat_dict[column_name]
    print(limit_stat)
    # json_output = []
    json_output = {}
    cols_to_select = f"game_id, player_id, team_id, opp_id, {limit_stat}, {column_name}"

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
                    WHERE nfl_games.year >= 2022'''

    df_columns = ['name', 'Year', 'Week', 'pos', 'game_id', 'player_id', 'team_id', 'opp_id', limit_stat, column_name]
    cursor.execute(query)
    results = list(cursor.fetchall())

    df_all_games = pd.DataFrame(results, columns=df_columns).reset_index(drop=True)
    df_all_games.reset_index(inplace=True)

    # Get player position, teams they played for, weeks for each year they played.
    df_player_game_logs_index_needed = df_all_games[df_all_games['player_id'] == int(player_id)]
    player_position = df_player_game_logs_index_needed.head(1)['pos'].values.tolist()[0]

    get_teams = df_player_game_logs_index_needed.loc[df_player_game_logs_index_needed['Year'] >= 2022]
    raw_player_teams = get_teams['team_id'].values.tolist()
    player_teams = []
    for team in raw_player_teams:
        if team not in player_teams: player_teams.append(team)

    week_dict = {}
    for year in rank_years:
        get_weeks = df_player_game_logs_index_needed.loc[df_player_game_logs_index_needed['Year'] == year]['Week'].values.tolist()
        week_dict[year] = get_weeks

    # Update the index column
    df_player_game_logs = pd.DataFrame()
    for year in loop_years:
        df_merge = df_player_game_logs_index_needed.loc[df_player_game_logs_index_needed['Year'] == year]
        df_merge.index = np.arange(1, len(df_merge) + 1)

        df_player_game_logs = pd.concat([df_player_game_logs, df_merge])

    # Create total player game counts
    total_player_games = len(df_player_game_logs)
    current_total_games = len(df_player_game_logs.loc[df_player_game_logs['Year'] == 2024])
    prior_total_games = len(df_player_game_logs.loc[df_player_game_logs['Year'] == 2023])
    third_total_games = len(df_player_game_logs.loc[df_player_game_logs['Year'] == 2022])

    # Initialize dictionary variables
    year_name_dict = {2022: 'third', 2023: 'prior', 2024: 'current'}
    total_game_dict = {2022: third_total_games, 2023: prior_total_games, 2024: current_total_games}

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

    # get the occurrence in the previous eight games
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
    df_total_occurrence = df_game_log_bet
    total_bet_occurrence = len(df_total_occurrence)
    total_percentage = str(round(((total_bet_occurrence/total_player_games) *100))) + '%'
    json_output.update({'career_bet_occurrence':total_bet_occurrence})
    json_output.update({'career_bet_occurrence_percentage': total_percentage})
    json_output.update({'career_total_games': total_player_games})

    # Get yearly bet frequency data
    for year in rank_years:
        df_bet_occurrence = df_game_log_bet.loc[df_game_log_bet['Year'] == year]
        bet_occurrence_count = len(df_bet_occurrence)
        bet_percentage = str(round(((bet_occurrence_count/total_game_dict[year]) *100), 2)) + '%'
        json_output.update({f"bet_occurrences_{year_name_dict[year]}": bet_occurrence_count})
        json_output.update({f"bet_occurrence_percentage_{year_name_dict[year]}": bet_percentage})
        json_output.update({f"total_games_{year_name_dict[year]}": total_game_dict[year]})
        json_output.update({f"bet_occurrence_logs_{year_name_dict[year]}": df_bet_occurrence.to_json()})

        # Get total game logs each year
        df_total_game_logs = df_player_game_logs.loc[df_player_game_logs['Year'] == year]
        json_output.update({f"game_logs_{year_name_dict[year]}": df_total_game_logs.to_json()})

    # Get the time between bet occurrences
    for year in rank_years:
        week_between_list = []

        # Get first and last game played by player each year.
        player_weeks = week_dict[year]
        first_game_played = player_weeks[0]
        last_game_played = player_weeks[-1]

        # Get the weeks that players bet would have hit.
        df_between_games = df_game_log_bet.loc[df_game_log_bet['Year'] == year]
        weeks_bet_hit_list = list(df_between_games.index)
        first_game_hit = weeks_bet_hit_list[0]
        last_game_hit = weeks_bet_hit_list[-1]

        games_btw_first_game_and_first_hit = first_game_hit - first_game_played
        games_btw_last_game_and_last_hit = last_game_played - last_game_hit

        if games_btw_first_game_and_first_hit != 0:
            week_between_list.append(games_btw_first_game_and_first_hit)

        for ind in range(len(weeks_bet_hit_list)):
            if ind != 0:
                weeks_since = (weeks_bet_hit_list[ind] - weeks_bet_hit_list[ind - 1]) - 1
                week_between_list.append(weeks_since)

        if games_btw_last_game_and_last_hit != 0:
            week_between_list.append(games_btw_last_game_and_last_hit)

        json_output.update({f"avg_time_between_occurrence_{year_name_dict[year]}": statistics.mean(week_between_list)})

    # Get coordinates for graphs
    for year in rank_years:
        stat_weekly_league_avg_dict = {}

        df_graph = df_player_game_logs.loc[df_player_game_logs['Year'] == year]
        weeks = df_graph['Week'].values.tolist()

        # Get X and Y coordinates:
        json_output.update({f"x_coordinates_{year_name_dict[year]}": df_graph['Week'].values.tolist()})
        json_output.update({f"y_coordinates_{year_name_dict[year]}": df_graph[column_name].values.tolist()})

        # Run query to get nfl games
        connection = create_connection()
        cursor = connection.cursor()
        games_query = f'''SELECT * from nfl_games'''
        cursor.execute(games_query)
        results = list(cursor.fetchall())
        game_table_cols = ['id', 'week', 'year', 'home_id', 'home_score', 'away_id', 'away_score', 'winner', 'margin_of_victory',
                      'weather_id', 'vegas_line', 'vegas_line_result', 'over_under', 'total_points', 'over_under_result']

        df_games_table = pd.DataFrame(results, columns=game_table_cols).reset_index(drop=True)
        for week in weeks:
            df_game_copy = df_games_table
            df_week_game = df_game_copy.loc[(df_game_copy['year'] == year) & (df_game_copy['week'] == week)]
            number_of_teams_playing = len(df_week_game) * 2

            df_week_total = df_all_games.reset_index(drop=True)
            df_week_total = df_week_total.loc[(df_week_total['pos'] == player_position) & (df_week_total['Week'] == week)
                                              & (df_week_total['Year'] == year) & (df_week_total[limit_stat] >= 5)]
            weekly_avg = round(((df_week_total[column_name].sum())/number_of_teams_playing), 2)
            stat_weekly_league_avg_dict[week] = weekly_avg

        # Get league average for each week as X2 coordinates
        json_output.update({f"weekly_league_avg_stat_{year_name_dict[year]}": list(stat_weekly_league_avg_dict.values())})
    #
    # Get position list variable based on player position
    if player_position == 'QB':
        position_list = ['RB', 'WR', 'TE']
    elif player_position == 'WR':
        position_list = ['QB', 'RB', 'TE']
    elif player_position == 'RB':
        position_list = ['QB', 'WR', 'TE']
    else:
        position_list = ['QB', 'WR', 'RB']

    # Get yearly breakdown of position stats with QB
    for year in [2022, 2023, 2024, 'all']:
        df_player_games = df_all_games.loc[df_all_games['player_id'] == int(player_id)]

        if year == 'all':
            games_with_player_ids = df_player_games.loc[df_player_games['Year'].isin(rank_years)]['game_id'].values.tolist()
        else:
            games_with_player_ids = df_player_games.loc[df_player_games['Year'] == year]['game_id'].values.tolist()
        df_player_games = df_all_games.loc[(df_all_games['game_id'].isin(games_with_player_ids)) &
                                           (df_all_games['team_id'].isin(player_teams))]

        game_dict = {}
        for position in position_list:
            stats_with_player = df_player_games.loc[df_player_games['pos'] == position]
            loop_stats = [limit_stat, column_name]
    #
            # Get game stats for each game
            for game in games_with_player_ids:
                game_stat_dict = {}
    #
                for stat in loop_stats:
                    pos_game = stats_with_player.loc[stats_with_player['game_id'] == game]
                    pos_stat = sum(pos_game[stat].values.tolist())
                    game_stat_dict[stat] = pos_stat
                game_dict[game] = game_stat_dict
    #
            # Get weekly average for each stat
            played_games = len(game_dict)
            for stat in loop_stats:
                stat_list = []
                for key in game_dict.keys():
                    stat_list.append(game_dict[key][stat])
                weekly_stat_avg = round(sum(stat_list)/played_games, 2)

                if year == 'all':
                    # json_output[f"{position.lower()}_avg_weekly_{stat}_total"] = weekly_stat_avg
                    json_output.update({f"{position.lower()}_avg_weekly_{stat}_total": weekly_stat_avg})
                else:
                    # json_output[f"{position.lower()}_avg_weekly_{stat}_{year_name_dict[year]}"] = weekly_stat_avg
                    json_output.update({f"{position.lower()}_avg_weekly_{stat}_{year_name_dict[year]}": weekly_stat_avg})
    #
    if player_position != 'QB':
        # Get the players stat as a percentage of the average
        for year in rank_years:
            # x and y coordinates
            week_list = []
            value_list = []

            # need to loop through games
            df_player_games = df_all_games.loc[df_all_games['player_id'] == int(player_id)]
            games_with_player_ids = df_player_games.loc[df_player_games['Year'] == year]['game_id'].values.tolist()
            df_game_logs_with_player = df_all_games.loc[
                (df_all_games['game_id'].isin(games_with_player_ids)) & (df_all_games['team_id'].isin(player_teams))]

            test_pos = 'WR'
            df_team_pos = df_game_logs_with_player.loc[df_game_logs_with_player['pos'] == test_pos]

            for game_id in games_with_player_ids:
                df_weekly_team_total = df_team_pos
                df_weekly_team_total = df_weekly_team_total.loc[df_weekly_team_total['game_id'] == game_id]

                weekly_team_total = df_weekly_team_total[column_name].sum()
                raw_week = df_weekly_team_total['Week'].values.tolist()[0]

                df_player_weekly_total = df_team_pos
                df_player_weekly_total = df_player_weekly_total.loc[(df_player_weekly_total['game_id'] == game_id) &
                                                                    (df_player_weekly_total['player_id'] == int(player_id))]
                player_total = df_player_weekly_total[column_name].values.tolist()[0]
                percentage_of_team_total = round((player_total/weekly_team_total) * 100)

                # add x and y coordinates
                week_list.append(raw_week)
                value_list.append(percentage_of_team_total)

            # Get X and Y coordinates:
            json_output.update({f"player_percentage_x_coordinates_{year_name_dict[year]}": week_list})
            json_output.update({f"player_percentage_y_coordinates_{year_name_dict[year]}": value_list})

    # Red zone stats
    connection = create_connection()
    cursor = connection.cursor()

    rz_query = f'''SELECT CONCAT(player.first_name, ' ', player.last_name), nfl_redzone_stats.*
                FROM nfl_redzone_stats
                JOIN player ON player.id = nfl_redzone_stats.player_id'''

    # rz_vals = [player_id]
    cursor.execute(rz_query)

    rz_cols = ['name', 'id', 'player_id', 'year', 'rz_20_pass_att', 'rz_20_pass_comp',  'rz_20_pass_comp_percentage',
               'rz_20_pass_yard', 'rz_20_pass_td', 'rz_20_pass_int', 'rz_10_pass_att', 'rz_10_pass_comp', 'rz_10_comp_percentage',
               'rz_10_pass_yard', 'rz_10_pass_td', 'rz_10_pass_int', 'rz_20_targets', 'rz_20_receptions', 'rz_20_rec_yards',
               'rz_20_catch_percentage', 'rz_20_rec_td', 'rz_20_target_percentage', 'rz_10_targets', 'rz_10_receptions',
               'rz_10_rec_yards', 'rz_10_catch_percentage', 'rz_10_rec_td', 'rz_10_target_percentage', 'rz_20_rush_att',
               'rz_20_rush_yards', 'rz_20_rush_td', 'rz_20_rush_percentage', 'rz_10_rush_att', 'rz_10_rush_yards', 'rz_10_rush_td',
               'rz_10_rush_percentage', 'rz_5_rush_att', 'rz_5_rush_yards', 'rz_5_rush_td', 'rz_5_rush_percentage']
    rz_results = list(cursor.fetchall())
    df_red_zone = pd.DataFrame(rz_results, columns=rz_cols).reset_index(drop=True)
    print(df_red_zone)


    # Enable Access-Control-Allow-Origin
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
    json_output = []

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
        json_output.append({f"rz_td_{year_name_dict[year]}": df_red_zone_third['rz_td'].values.tolist()[0]})
        # json_output[f"rz_td_{year_name_dict[year]}"] = df_red_zone_third['rz_td'].values.tolist()[0]
        json_output.append({f"rz_td_rank_{year_name_dict[year]}": df_red_zone_third['rz_td rank'].values.tolist()[0]})
        # json_output[f"rz_td_rank_{year_name_dict[year]}"] = df_red_zone_third['rz_td rank'].values.tolist()[0]
        json_output.append({f"rz_percentage_{year_name_dict[year]}": df_red_zone_third['rz_percentage'].values.tolist()[0]})
        # json_output[f"rz_percentage_{year_name_dict[year]}"] = df_red_zone_third['rz_percentage'].values.tolist()[0]
        json_output.append({f"rz_percentage_rank_{year_name_dict[year]}": df_red_zone_third['rz_percentage rank'].values.tolist()[0]})
        # json_output[f"rz_percentage_rank_{year_name_dict[year]}"] = df_red_zone_third['rz_percentage rank'].values.tolist()[0]

        # PASSING DATA
        df_passing = df_ranked[['team_id', 'year', 'games', 'pass_comp', 'pass_comp rank', 'pass_yards', 'pass_yards rank',
                               'pass_td', 'pass_td rank', 'yards_per_att', 'yards_per_att rank', 'pass_yards_per_comp',
                               'pass_yards_per_comp rank', 'pass_yards_per_game', 'pass_yards_per_game rank']]
        df_passing = df_passing.loc[df_passing['team_id'] == int(team_id)]

        # get passing data third year
        df_passing_third = df_passing.loc[df_passing['year'] == year]
        json_output.append({f"pass_comp_{year_name_dict[year]}": df_passing_third['pass_comp'].values.tolist()[0]})
        # json_output[f"pass_comp_{year_name_dict[year]}"] = df_passing_third['pass_comp'].values.tolist()[0]
        json_output.append(
            {f"pass_comp_rank_{year_name_dict[year]}": df_passing_third['pass_comp rank'].values.tolist()[0]})
        # json_output[f"pass_comp_rank_{year_name_dict[year]}"] = df_passing_third['pass_comp rank'].values.tolist()[0]
        json_output.append({f"pass_yards_{year_name_dict[year]}": df_passing_third['pass_yards'].values.tolist()[0]})
        # json_output[f"pass_yards_{year_name_dict[year]}"] = df_passing_third['pass_yards'].values.tolist()[0]
        json_output.append({f"pass_yards_rank_{year_name_dict[year]}": df_passing_third['pass_yards rank'].values.tolist()[0]})
        # json_output[f"pass_yards_rank_{year_name_dict[year]}"] = df_passing_third['pass_yards rank'].values.tolist()[0]
        json_output.append({f"pass_td_{year_name_dict[year]}": df_passing_third['pass_td'].values.tolist()[0]})
        # json_output[f"pass_td_{year_name_dict[year]}"] = df_passing_third['pass_td'].values.tolist()[0]
        json_output.append({f"pass_td_rank_{year_name_dict[year]}": df_passing_third['pass_td rank'].values.tolist()[0]})
        # json_output[f"pass_td_rank_{year_name_dict[year]}"] = df_passing_third['pass_td rank'].values.tolist()[0]
        json_output.append(
            {f"yards_per_att_{year_name_dict[year]}": df_passing_third['yards_per_att'].values.tolist()[0]})
        # json_output[f"yards_per_att_{year_name_dict[year]}"] = df_passing_third['yards_per_att'].values.tolist()[0]
        json_output.append(
            {f"yards_per_att_rank_{year_name_dict[year]}": df_passing_third['yards_per_att rank'].values.tolist()[0]})
        # json_output[f"yards_per_att_rank_{year_name_dict[year]}"] = df_passing_third['yards_per_att rank'].values.tolist()[0]
        json_output.append(
            {f"pass_yards_per_comp_{year_name_dict[year]}": df_passing_third['pass_yards_per_comp'].values.tolist()[0]})
        # json_output[f"pass_yards_per_comp_{year_name_dict[year]}"] = df_passing_third['pass_yards_per_comp'].values.tolist()[0]
        json_output.append(
            {f"pass_yards_per_comp_rank_{year_name_dict[year]}": df_passing_third['pass_yards_per_comp rank'].values.tolist()[0]})
        # json_output[f"pass_yards_per_comp_rank_{year_name_dict[year]}"] = df_passing_third['pass_yards_per_comp rank'].values.tolist()[0]
        json_output.append(
            {f"pass_yards_per_game_{year_name_dict[year]}": df_passing_third['pass_yards_per_game'].values.tolist()[0]})
        # json_output[f"pass_yards_per_game_{year_name_dict[year]}"] = df_passing_third['pass_yards_per_game'].values.tolist()[0]
        json_output.append(
            {f"pass_yards_per_game_rank_{year_name_dict[year]}": df_passing_third['pass_yards_per_game rank'].values.tolist()[0]})
        # json_output[f"pass_yards_per_game_rank_{year_name_dict[year]}"] = df_passing_third['pass_yards_per_game rank'].values.tolist()[0]

        # RUSHING DATA
        df_rushing = df_ranked[['team_id', 'year', 'games', 'rush_att', 'rush_att rank', 'rush_yards', 'rush_yards rank',
                               'rush_td', 'rush_td rank', 'rush_yards_per_att', 'rush_yards_per_att rank', 'rush_yards_per_game',
                               'rush_yards_per_game rank']]
        df_rushing = df_rushing.loc[df_rushing['team_id'] == int(team_id)]

        # get rushing data third year
        df_rushing_third = df_rushing.loc[df_rushing['year'] == year]
        json_output.append(
            {f"rush_att_{year_name_dict[year]}": df_rushing_third['rush_att'].values.tolist()[0]})
        # json_output[f"rush_att_{year_name_dict[year]}"] = df_rushing_third['rush_att'].values.tolist()[0]
        json_output.append(
            {"rush_att_rank_{year_name_dict[year]}": df_rushing_third['rush_att rank'].values.tolist()[0]})
        # json_output[f"rush_att_rank_{year_name_dict[year]}"] = df_rushing_third['rush_att rank'].values.tolist()[0]
        json_output.append(
            {f"rush_yards_{year_name_dict[year]}": df_rushing_third['rush_yards'].values.tolist()[0]})
        # json_output[f"rush_yards_{year_name_dict[year]}"] = df_rushing_third['rush_yards'].values.tolist()[0]
        json_output.append(
            {f"rush_yards_rank_{year_name_dict[year]}": df_rushing_third['rush_yards rank'].values.tolist()[0]})
        # json_output[f"rush_yards_rank_{year_name_dict[year]}"] = df_rushing_third['rush_yards rank'].values.tolist()[0]
        json_output.append(
            {f"rush_td_{year_name_dict[year]}": df_rushing_third['rush_td'].values.tolist()[0]})
        # json_output[f"rush_td_{year_name_dict[year]}"] = df_rushing_third['rush_td'].values.tolist()[0]
        json_output.append(
            {f"rush_td_rank_{year_name_dict[year]}": df_rushing_third['rush_td rank'].values.tolist()[0]})
        # json_output[f"rush_td_rank_{year_name_dict[year]}"] = df_rushing_third['rush_td rank'].values.tolist()[0]
        json_output.append(
            {f"rush_yards_per_att_{year_name_dict[year]}": df_rushing_third['rush_yards_per_att'].values.tolist()[0]})
        # json_output[f"rush_yards_per_att_{year_name_dict[year]}"] = df_rushing_third['rush_yards_per_att'].values.tolist()[0]
        json_output.append(
            {f"rush_yards_per_att_{year_name_dict[year]}": df_rushing_third['rush_yards_per_att rank'].values.tolist()[0]})
        # json_output[f"rush_yards_per_att_{year_name_dict[year]}"] = df_rushing_third['rush_yards_per_att rank'].values.tolist()[0]
        json_output.append(
            {f"rush_yards_per_game_{year_name_dict[year]}": df_rushing_third['rush_yards_per_game'].values.tolist()[0]})
        # json_output[f"rush_yards_per_game_{year_name_dict[year]}"] = df_rushing_third['rush_yards_per_game'].values.tolist()[0]
        json_output.append(
            {f"rush_yards_per_game_rank_{year_name_dict[year]}": df_rushing_third['rush_yards_per_game rank'].values.tolist()[0]})
        # json_output[f"rush_yards_per_game_rank_{year_name_dict[year]}"] = df_rushing_third['rush_yards_per_game rank'].values.tolist()[0]

        # DRIVE DATA
        df_drive = df_ranked[['team_id', 'year', 'games', 'points_per_game', 'points_per_game rank', 'total_points',
                             'total_points rank', 'plays_per_drive', 'plays_per_drive rank', 'yards_per_drive', 'yards_per_drive rank',
                             'points_per_drive', 'points_per_drive rank']]
        df_drive = df_drive.loc[df_drive['team_id'] == int(team_id)]

        # get drive data third year
        df_drive_third = df_drive.loc[df_drive['year'] == year]
        json_output.append(
            {f"points_per_game_{year_name_dict[year]}": df_drive_third['points_per_game'].values.tolist()[0]})
        # json_output[f"points_per_game_{year_name_dict[year]}"] = df_drive_third['points_per_game'].values.tolist()[0]
        json_output.append(
            {f"points_per_game_rank_{year_name_dict[year]}": df_drive_third['points_per_game rank'].values.tolist()[0]})
        # json_output[f"points_per_game_rank_{year_name_dict[year]}"] = df_drive_third['points_per_game rank'].values.tolist()[0]
        json_output.append(
            {f"total_points_{year_name_dict[year]}": df_drive_third['total_points'].values.tolist()[0]})
        # json_output[f"total_points_{year_name_dict[year]}"] = df_drive_third['total_points'].values.tolist()[0]
        json_output.append(
            {f"total_points_rank_{year_name_dict[year]}": df_drive_third['total_points rank'].values.tolist()[0]})
        # json_output[f"total_points_rank_{year_name_dict[year]}"] = df_drive_third['total_points rank'].values.tolist()[0]
        json_output.append(
            {f"plays_per_drive_{year_name_dict[year]}":  df_drive_third['plays_per_drive'].values.tolist()[0]})
        # json_output[f"plays_per_drive_{year_name_dict[year]}"] = df_drive_third['plays_per_drive'].values.tolist()[0]
        json_output.append(
            {f"plays_per_drive_rank_{year_name_dict[year]}": df_drive_third['plays_per_drive rank'].values.tolist()[0]})
        # json_output[f"plays_per_drive_rank_{year_name_dict[year]}"] = df_drive_third['plays_per_drive rank'].values.tolist()[0]
        json_output.append(
            {f"yards_per_drive_att_{year_name_dict[year]}": df_drive_third['yards_per_drive'].values.tolist()[0]})
        # json_output[f"yards_per_drive_att_{year_name_dict[year]}"] = df_drive_third['yards_per_drive'].values.tolist()[0]
        json_output.append(
            {f"yards_per_drive_att_{year_name_dict[year]}": df_drive_third['yards_per_drive rank'].values.tolist()[0]})
        # json_output[f"yards_per_drive_att_{year_name_dict[year]}"] = df_drive_third['yards_per_drive rank'].values.tolist()[0]
        json_output.append(
            {f"points_per_drive_{year_name_dict[year]}": df_drive_third['points_per_drive'].values.tolist()[0]})
        # json_output[f"points_per_drive_{year_name_dict[year]}"] = df_drive_third['points_per_drive'].values.tolist()[0]
        json_output.append(
            {f"points_per_drive_rank_{year_name_dict[year]}": df_drive_third['points_per_drive rank'].values.tolist()[0]})
        # json_output[f"points_per_drive_rank_{year_name_dict[year]}"] = df_drive_third['points_per_drive rank'].values.tolist()[0]

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
        json_output.append({f"team_record_{year_name_dict[year]}": record})

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

    json_output = []

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
        json_output.append({f"rz_td_{year_name_dict[year]}": df_red_zone_third['rz_td'].values.tolist()[0]})
        json_output.append({f"rz_td_rank_{year_name_dict[year]}": df_red_zone_third['rz_td rank'].values.tolist()[0]})
        json_output.append({f"rz_percentage_{year_name_dict[year]}": df_red_zone_third['rz_percentage'].values.tolist()[0]})
        json_output.append({f"rz_percentage_rank_{year_name_dict[year]}": df_red_zone_third['rz_percentage rank'].values.tolist()[0]})

        # PASSING DATA
        df_passing = df_ranked[['team_id', 'year', 'games', 'pass_comp', 'pass_comp rank', 'pass_yards', 'pass_yards rank',
                               'pass_td', 'pass_td rank', 'yards_per_att', 'yards_per_att rank', 'pass_yards_per_comp',
                               'pass_yards_per_comp rank', 'pass_yards_per_game', 'pass_yards_per_game rank']]
        df_passing = df_passing.loc[df_passing['team_id'] == int(team_id)]

        df_passing_third = df_passing.loc[df_passing['year'] == year]
        json_output.append({f"pass_comp_{year_name_dict[year]}": df_passing_third['pass_comp'].values.tolist()[0]})
        json_output.append({f"pass_comp_rank_{year_name_dict[year]}": df_passing_third['pass_comp rank'].values.tolist()[0]})
        json_output.append({f"pass_yards_{year_name_dict[year]}": df_passing_third['pass_yards'].values.tolist()[0]})
        json_output.append({f"pass_yards_rank_{year_name_dict[year]}": df_passing_third['pass_yards rank'].values.tolist()[0]})
        json_output.append({f"pass_td_{year_name_dict[year]}": df_passing_third['pass_td'].values.tolist()[0]})
        json_output.append({f"pass_td_rank_{year_name_dict[year]}": df_passing_third['pass_td rank'].values.tolist()[0]})
        json_output.append({f"yards_per_att_{year_name_dict[year]}": df_passing_third['yards_per_att'].values.tolist()[0]})
        json_output.append({f"yards_per_att_rank_{year_name_dict[year]}": df_passing_third['yards_per_att rank'].values.tolist()[0]})
        json_output.append({f"pass_yards_per_comp_{year_name_dict[year]}": df_passing_third['pass_yards_per_comp'].values.tolist()[0]})
        json_output.append({f"pass_yards_per_comp_rank_{year_name_dict[year]}": df_passing_third['pass_yards_per_comp rank'].values.tolist()[0]})
        json_output.append({f"pass_yards_per_game_{year_name_dict[year]}": df_passing_third['pass_yards_per_game'].values.tolist()[0]})
        json_output.append({f"pass_yards_per_game_rank_{year_name_dict[year]}": df_passing_third['pass_yards_per_game rank'].values.tolist()[0]})

        # RUSHING DATA
        df_rushing = df_ranked[['team_id', 'year', 'games', 'rush_att', 'rush_att rank', 'rush_yards', 'rush_yards rank',
                               'rush_td', 'rush_td rank', 'rush_yards_per_att', 'rush_yards_per_att rank', 'rush_yards_per_game',
                               'rush_yards_per_game rank']]
        df_rushing = df_rushing.loc[df_rushing['team_id'] == int(team_id)]

        df_rushing_third = df_rushing.loc[df_rushing['year'] == year]
        json_output.append({f"rush_att_{year_name_dict[year]}": df_rushing_third['rush_att'].values.tolist()[0]})
        json_output.append({f"rush_att_rank_{year_name_dict[year]}": df_rushing_third['rush_att rank'].values.tolist()[0]})
        json_output.append({f"rush_yards_{year_name_dict[year]}": df_rushing_third['rush_yards'].values.tolist()[0]})
        json_output.append({f"rush_yards_rank_{year_name_dict[year]}": df_rushing_third['rush_yards rank'].values.tolist()[0]})
        json_output.append({f"rush_td_{year_name_dict[year]}": df_rushing_third['rush_td'].values.tolist()[0]})
        json_output.append({f"rush_td_rank_{year_name_dict[year]}": df_rushing_third['rush_td rank'].values.tolist()[0]})
        json_output.append({f"rush_yards_per_att_{year_name_dict[year]}": df_rushing_third['rush_yards_per_att'].values.tolist()[0]})
        json_output.append({f"rush_yards_per_att_{year_name_dict[year]}": df_rushing_third['rush_yards_per_att rank'].values.tolist()[0]})
        json_output.append({f"rush_yards_per_game_{year_name_dict[year]}": df_rushing_third['rush_yards_per_game'].values.tolist()[0]})
        json_output.append({f"rush_yards_per_game_rank_{year_name_dict[year]}": df_rushing_third['rush_yards_per_game rank'].values.tolist()[0]})

        # DRIVE DATA
        df_drive = df_ranked[['team_id', 'year', 'games', 'points_per_game', 'points_per_game rank', 'total_points',
                             'total_points rank', 'plays_per_drive', 'plays_per_drive rank', 'yards_per_drive', 'yards_per_drive rank',
                             'points_per_drive', 'points_per_drive rank']]
        df_drive = df_drive.loc[df_drive['team_id'] == int(team_id)]

        df_drive_third = df_drive.loc[df_drive['year'] == year]
        json_output.append({f"points_per_game_{year_name_dict[year]}": df_drive_third['points_per_game'].values.tolist()[0]})
        json_output.append({f"points_per_game_rank_{year_name_dict[year]}": df_drive_third['points_per_game rank'].values.tolist()[0]})
        json_output.append({f"total_points_{year_name_dict[year]}": df_drive_third['total_points'].values.tolist()[0]})
        json_output.append({f"total_points_rank_{year_name_dict[year]}": df_drive_third['total_points rank'].values.tolist()[0]})
        json_output.append({f"plays_per_drive_{year_name_dict[year]}": df_drive_third['plays_per_drive'].values.tolist()[0]})
        json_output.append({f"plays_per_drive_rank_{year_name_dict[year]}": df_drive_third['plays_per_drive rank'].values.tolist()[0]})
        json_output.append({f"yards_per_drive_att_{year_name_dict[year]}": df_drive_third['yards_per_drive'].values.tolist()[0]})
        json_output.append({f"yards_per_drive_att_{year_name_dict[year]}": df_drive_third['yards_per_drive rank'].values.tolist()[0]})
        json_output.append({f"points_per_drive_{year_name_dict[year]}": df_drive_third['points_per_drive'].values.tolist()[0]})
        json_output.append({f"points_per_drive_rank_{year_name_dict[year]}": df_drive_third['points_per_drive rank'].values.tolist()[0]})

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

        json_output.append({f"opp_allowed_bet_{year_name_dict[year]}": round(((bet_allowed_current / total_pos_faced_current) * 100), 1)})
        json_output.append({f"opp_allowed_bet_log_{year_name_dict[year]}": df_bet.to_json()})

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
    json_output.append({f"player_game_logs_vs_opponent": df_vs_player.to_json()})

    # Get total touchdowns allowed to RB, TE, and WR
    for year in rank_years:
        df_rb = df_game_logs.loc[(df_game_logs['pos'] == 'RB') & (df_game_logs['Year'] ==  year)]
        rb_rush_td_total = df_rb['rush_td'].sum()
        rb_rec_td_total = df_rb['rec_td'].sum()
        json_output.append({f"rb_rush_td_total_{year_name_dict[year]}": int(rb_rush_td_total)})
        json_output.append({f"rb_rec_td_total_{year_name_dict[year]}": int(rb_rec_td_total)})

        df_wr = df_game_logs.loc[(df_game_logs['pos'] == 'WR') & (df_game_logs['Year'] ==  year)]
        wr_rush_td_total = df_wr['rush_td'].sum()
        wr_rec_td_total = df_wr['rec_td'].sum()
        json_output.append({f"wr_rush_td_total_{year_name_dict[year]}": int(wr_rush_td_total)})
        json_output.append({f"wr_rec_td_total_{year_name_dict[year]}": int(wr_rec_td_total)})

        df_qb = df_game_logs.loc[(df_game_logs['pos'] == 'QB') & (df_game_logs['Year'] ==  year)]
        qb_rush_td_total = df_qb['rush_td'].sum()
        json_output.append({f"qb_rush_td_total_{year_name_dict[year]}": int(qb_rush_td_total)})

        df_te = df_game_logs.loc[(df_game_logs['pos'] == 'QB') & (df_game_logs['Year'] ==  year)]
        te_rec_td_total = df_te['rush_td'].sum()
        json_output.append({f"te_rec_td_total_{year_name_dict[year]}": int(te_rec_td_total)})

    json_output = jsonify(json_output)
    json_output.headers.add("Access-Control-Allow-Origin", "*")
    return json_output


@nfl.route('/nfl/rz_stat', methods=['GET'])
def nfl_get_rz_stat():
    player_id = request.args.get('player_id', None)
    year = request.args.get('year', None)
    connection = create_connection()
    cursor = connection.cursor()

    query = f'''SELECT CONCAT(player.first_name, ' ', player.last_name), nfl_redzone_stats.*
                FROM nfl_redzone_stats
                JOIN player ON player.id = nfl_redzone_stats.player_id
                WHERE nfl_redzone_stats.player_id = %s AND nfl_redzone_stats.year = %s'''

    vals = [player_id, year]
    cursor.execute(query, vals)

    results = list(cursor.fetchall())

    output = []
    for result in results:
        item = {'name': result[0], 'id': result[1], 'player_id': result[2], 'year': result[3],
        'rz_20_pass_att': result[4], 'rz_20_pass_comp': result[5],  'rz_20_pass_comp_percentage': result[6], 'rz_20_pass_yard': result[7],
                'rz_20_pass_td': result[8], 'rz_20_pass_int': result[9],
        'rz_10_pass_att': result[10], 'rz_10_pass_comp': result[11], 'rz_10_comp_percentage': result[12], 'rz_10_pass_yard': result[13],
                'rz_10_pass_td': result[14], 'rz_10_pass_int': result[15],
        'rz_20_targets': result[16], 'rz_20_receptions': result[17], 'rz_20_rec_yards': result[18], 'rz_20_catch_percentage': result[19],
                'rz_20_rec_td': result[20], 'rz_20_target_percentage': result[21],
        'rz_10_targets': result[22], 'rz_10_receptions': result[23], 'rz_10_rec_yards': result[24], 'rz_10_catch_percentage': result[25],
              'rz_10_rec_td': result[26], 'rz_10_target_percentage': result[27],
        'rz_20_rush_att': result[28], 'rz_20_rush_yards': result[29], 'rz_20_rush_td': result[30], 'rz_20_rush_percentage': result[31],
        'rz_10_rush_att': result[32], 'rz_10_rush_yards': result[33], 'rz_10_rush_td': result[34], 'rz_10_rush_percentage': result[35],
        'rz_5_rush_att': result[36], 'rz_5_rush_yards': result[37], 'rz_5_rush_td': result[38], 'rz_5_rush_percentage': result[39]}
        if item not in output:
            output.append(item)

    # Enable Access-Control-Allow-Origin
    output = jsonify(output)
    output.headers.add("Access-Control-Allow-Origin", "*")
    return output


# @nfl.route('/nfl/games', methods=['GET'])
# def nfl_get_games():
#     id = request.args.get('id', None)
#     connection = create_connection()
#     cursor = connection.cursor()
#     cursor.execute('''SELECT * FROM nfl_games
#                     WHERE home_id = %s OR away_id = %s ''',
#                    [id, id])
#     results = list(cursor.fetchall())
#     result_list = []
#     for result in results:
#         player_dict = {'id': result[0], 'week': result[1], 'year': result[2], 'home_id': result[3], 'home_score': result[4],
#                        'away_team_id': result[5], 'away_score': result[6], 'winner': result[7], 'margin_of_victory': result[8],
#                        'weather': result[9], 'vegas_line': result[10], 'vegas_line_result': result[11], 'over_under': result[12],
#                        'over_under_result': result[13]}
#         result_list.append(player_dict)
#
#     # Enable Access-Control-Allow-Origin
#     result_list = jsonify(result_list)
#     result_list.headers.add("Access-Control-Allow-Origin", "*")
#     return result_list
