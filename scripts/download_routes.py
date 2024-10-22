import pandas as pd

from .db import create_connection
from flask import Blueprint, request, jsonify

from variables.nfl_variables import nfl_current_season, nfl_current_season_table

docs = Blueprint("docs", __name__)

@docs.route('docs/nfl_data', methods = ['GET'])
def download_nfl_data():
    connection = create_connection()
    cursor = connection.cursor()

    query = f'''SELECT * FROM nfl_team_defense
                WHERE year = 2023'''

    cursor.execute(query)

    results = cursor.fetchall()

    df_final = pd.DataFrame()
    for result in results:
        item = {'id':result[0], 'team_id': result[1],  'year': result[2], 'games':  result[3], 'dvoa': result[4], 'epa_per_play': result[5],
        'success_rate': result[6], 'dropback_epa': result[7], 'dropback_sr': result[8], 'rush_epa': result[9], 'rush_sr': result[10],
        'pass_comp': result[11], 'pass_att': result[12], 'pass_comp_percentage': result[13], 'pass_yards': result[14], 'pass_td': result[15],
        'pass_td_percentage': result[16], 'yards_per_att': result[17], 'pass_yards_per_comp': result[18], 'pass_yards_per_game': result[19],
        'passer_rating': result[20], 'qb_hits': result[21], 'sacks': result[22], 'ints': result[23], 'int_percentage': result[24],
        'pass_deflections': result[25], 'rush_att': result[26], 'rush_yards': result[27], 'rush_td': result[28], 'rush_yards_per_att': result[29],
        'rush_yards_per_game': result[30], 'total_points': result[31], 'points_per_game': result[32], 'rz_att': result[33],
        'rz_td': result[34], 'rz_percentage': result[35], 'drives': result[36], 'plays': result[37], 'scoring_percentage': result[38],
        'to_percentage': result[39], 'plays_per_drive': result[40], 'yards_per_drive': result[41], 'points_per_drive': result[42],
        'third_down_att': result[43], 'third_down_conv': result[44], 'third_down_conv_rate': result[45], 'fourth_down_att': result[46],
        'fourth_down_conv': result[47], 'fourth_down_conv_rate': result[48], 'qb_rush_att': result[49], 'qb_rush_yards': result[50],
        'qb_rush_td': result[51], 'rb_att': result[52], 'rb_yards': result[53], 'rb_td': result[54], 'rb_targets': result[55],
        'rb_rec': result[56], 'rb_rec_yards': result[57], 'rb_rec_td': result[58], 'wr_targets': result[59], 'wr_rec': result[60],
        'wr_yards': result[61], 'wr_td': result[62], 'te_targets': result[63], 'te_rec': result[64], 'te_yards': result[65],
        'te_td': result[66]}

        df_merge = pd.DataFrame(item, index=[0])  # CREATE THE DATAFRAME THAT WILL BE MERGED
        df_final = pd.concat([df_final, df_merge])

    print(df_final)
    file = '/Users/martymcflynn/Desktop/OneDrive/betting_buddy/betting-buddy-api/docs/test.csv'
    df_final.to_csv(file)
    return f"Data has been downloaded"



from variables.nfl_variables import nfl_player_db_file
@docs.route('docs/nfl_players', methods = ['GET'])
def download_nfl_players():
    # INITIALIZE VARIABLES
    file = nfl_player_db_file
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute('''SELECT * FROM player
            WHERE position = 'QB' OR position = 'RB' OR position = 'WR' OR position = 'FB' OR position = 'TE'
            ORDER BY id
            ''')

    results = cursor.fetchall()

    print(results)
    # initialize the final dataframe
    df_final = pd.DataFrame(columns=['id', 'last_name', 'first_name', 'position', 'current_team', 'currently_playing'])
    index_val = 0
    for result in results:
        item = {'id': result[0], 'last_name': result[1], 'first_name': result[2], 'position': result[3], 'current_team': result[5],
                'currently_playing': result[6]}
        print(item)
        df_merge = pd.DataFrame(item, index=[index_val])  # CREATE THE DATAFRAME THAT WILL BE MERGED
        df_final = pd.concat([df_final, df_merge])
        index_val += 1

    # reset the index of the final dataframe
    df_final = df_final.reset_index(drop=True)

    # add column full_name to final dataframe
    for ind, row in df_final.iterrows():
        full_name = row['first_name'] + ' ' + row['last_name']
        df_final.at[ind, 'full_name'] = full_name

    df_final.to_csv(file)
    return f"nfl_player_table.csv has been updated with the moost upto date NFL players."


@docs.route('docs/nfl_schedule', methods=['GET'])
def download_nfl_current_schedule():
    # INITIALIZE VARIABLES
    file = nfl_current_season_table
    connection = create_connection()
    cursor = connection.cursor()


    query = '''SELECT * FROM nfl_games
                    WHERE year = %s'''
    vals = [nfl_current_season]

    # run query and get results as a list
    cursor.execute(query, vals)
    results = cursor.fetchall()

    # initialize the final dataframe
    df_final = pd.DataFrame(columns=['id', 'week', 'year', 'home_id', 'home_score', 'away_id', 'away_score',
                                     'winner', 'margin_of_victory', 'weather_id', 'vegas_line', 'vegas_line_result',
                                     'over_under', 'total_points', 'over_under_result'])

    index_val = 0
    for result in results:
        item = {'id': result[0], 'week': result[1], 'year': result[2], 'home_id': result[3], 'home_score': result[4],
         'away_id': result[5], 'away_score': result[6], 'winner': result[7], 'margin_of_victory': result[8], 'weather_id': result[9],
         'vegas_line': result[10], 'vegas_line_result': result[11], 'over_under': result[12], 'total_points': result[13],
         'over_under_result': result[14]}

        df_merge = pd.DataFrame(item, index=[index_val])  # CREATE THE DATAFRAME THAT WILL BE MERGED
        df_final = pd.concat([df_final, df_merge])
        index_val += 1

    # reset the index of the final dataframe
    df_final = df_final.reset_index(drop=True)

    df_final.to_csv(file)
    return f"nfl_current_season_schedule.csv has been updated with the most upto date NFL games."


