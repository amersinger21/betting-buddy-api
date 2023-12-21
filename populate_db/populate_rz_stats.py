import pandas as pd

import sqlite3

from scripts.rz_stats import add_rz_stat


pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', None)

db_file = '/Users/martymcflynn/Projects/betting_buddy_local/betting_buddy_local.db'

# Get a list of Players:
# Connect to the local DB:
conn = sqlite3.connect(db_file)
c = conn.cursor()

# Get the player_id from the player table:
c.execute("""SELECT id, last_name, first_name, position FROM player""")
results = list(c.fetchall())
conn.close()  # close our connection
plyr_list = []
years = [2018, 2019, 2020, 2021, 2022]


for result in results:
    name = result[2] + ' ' + result[1]
    add_list = [result[0], name, result[3]]
    plyr_list.append(add_list)

for item in plyr_list:
    player = item[1]
    player_split = player.split()
    first_name = player_split[0]
    last_name = player_split[1]
    print(player)

    # Get player_id:
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute("""SELECT id, last_name, first_name, position
                                 FROM player
                                 WHERE last_name=?
                                    and first_name=?""",
              ([last_name, first_name]))
    try:
        player_id = list(c.fetchone())[0]
    except TypeError:
        continue

    for year in years:
        df_rzpass = pd.read_csv('/Users/martymcflynn/Documents/Football_Documents/red_zone_stats/rz_passing.csv',
                                index_col=0)
        df_rzpass = df_rzpass.loc[(df_rzpass['Player'] == player) & (df_rzpass['Year'] == year)]

        df_rzrush = pd.read_csv('/Users/martymcflynn/Documents/Football_Documents/red_zone_stats/rz_rushing.csv',
                                index_col=0)
        df_rzrush = df_rzrush.loc[(df_rzrush['Player'] == player) & (df_rzrush['Year'] == year)]
        df_rzrec = pd.read_csv('/Users/martymcflynn/Documents/Football_Documents/red_zone_stats/rz_receiving.csv',
                               index_col=0)
        df_rzrec = df_rzrec.loc[(df_rzrec['Player'] == player) & (df_rzrec['Year'] == year)]

        while True:
            row_dict = {'player_id': 0,
                        'team_id': 0,
                        'year': 0,
                        'rz_20_pass_att': 0,
                        'rz_20_pass_yards': 0,
                        'rz_20_pass_td': 0,
                        'rz_20_pass_int': 0,
                        'rz_20_comp_percentage': 0,
                        'rz_10_pass_att': 0,
                        'rz_10_pass_yards': 0,
                        'rz_10_pass_td': 0,
                        'rz_10_pass_int': 0,
                        'rz_10_comp_percentage': 0,
                        'rz_20_targets': 0,
                        'rz_20_receptions': 0,
                        'rz_20_rec_yards': 0,
                        'rz_20_catch_percentage': 0,
                        'rz_20_rec_td': 0,
                        'rz_20_target_percentage': 0,
                        'rz_10_targets': 0,
                        'rz_10_receptions': 0,
                        'rz_10_rec_yards': 0,
                        'rz_10_catch_percentage': 0,
                        'rz_10_rec_td': 9,
                        'rz_10_target_percentage': 0,
                        'rz_20_rush_att': 0,
                        'rz_20_rush_td': 0,
                        'rz_20_rush_yards': 0,
                        'rz_20_rush_percentage': 0,
                        'rz_10_rush_att': 0,
                        'rz_10_rush_td': 0,
                        'rz_10_rush_yards': 0,
                        'rz_10_rush_percentage': 0,
                        'rz_5_rush_att': 0,
                        'rz_5_rush_td': 0,
                        'rz_5_rush_yards': 0,
                        'rz_5_rush_percentage': 0}

            row_dict['player_id'] = player_id

        #
            for index, row in df_rzpass.iterrows():
                # print(row)
                team_abbr = row['Team']
                # Get the team ID:
                conn = sqlite3.connect(db_file)
                c = conn.cursor()

                c.execute("""SELECT id
                                             FROM team
                                             WHERE name=?""",
                          ([team_abbr]))
                team_id = list(c.fetchone())[0]
                row_dict['team_id'] = team_id
                row_dict['year'] = row["Year"]
                row_dict['rz_20_pass_att'] = row['Att']
                row_dict['rz_20_pass_yards'] = row['Yds']
                row_dict['rz_20_pass_td'] = row['TD']
                row_dict['rz_20_pass_int'] = row['Int']
                row_dict['rz_20_comp_percentage'] = row['Cmp%']
                row_dict['rz_10_pass_att'] = row['10yd_Att']
                row_dict['rz_10_pass_yards'] = row['10yd_Yds']
                row_dict['rz_10_pass_td'] = row['10yd_TD']
                row_dict['rz_10_pass_int'] = row['10yd_Int']
                row_dict['rz_10_pass_comp_percentage'] = row['10yd_Cmp%']

            for index, row in df_rzrush.iterrows():
                # print(row)
                team_abbr = row['Team']
                # Get the team ID:
                conn = sqlite3.connect(db_file)
                c = conn.cursor()

                c.execute("""SELECT id
                                                             FROM team
                                                             WHERE name=?""",
                          ([team_abbr]))
                team_id = list(c.fetchone())[0]
                row_dict['team_id'] = team_id
                row_dict['year'] = row["Year"]
                row_dict['year'] = row['Year']
                row_dict['team_id'] = team_id
                row_dict['rz_20_rush_att'] = row['Att']
                row_dict['rz_20_rush_yards'] = row['Yds']
                row_dict['rz_20_rush_td'] = row['TD']
                row_dict['rz_20_rush_percentage'] = row['%Rush'] * 100
                row_dict['rz_10_rush_att'] = row['10yd_Att']
                row_dict['rz_10_rush_yards'] = row['10yd_Yds']
                row_dict['rz_10_rush_td'] = row['10yd_TD']
                row_dict['rz_10_rush_percentage'] = row['10yd_%Rush'] * 100
                row_dict['rz_5_rush_att'] = row['5yd_Att']
                row_dict['rz_5_rush_yards'] = row['5yd_Yds']
                row_dict['rz_5_rush_td'] = row['5yd_TD']
                row_dict['rz_5_rush_percentage'] = row['5yd_%Rush'] * 100

            for index, row in df_rzrec.iterrows():
                team_abbr = row['Team']
                # Get the team ID:
                conn = sqlite3.connect(db_file)
                c = conn.cursor()

                c.execute("""SELECT id
                                            FROM team
                                            WHERE name=?""",
                          ([team_abbr]))
                team_id = list(c.fetchone())[0]
                row_dict['team_id'] = team_id
                row_dict['year'] = row["Year"]
                row_dict['year'] = row['Year']
                row_dict['rz_20_targets'] = row['Tgt']
                row_dict['rz_20_receptions'] = row['Rec']
                row_dict['rz_20_rec_yards'] = row['Yds']
                row_dict['rz_20_rec_td'] = row['TD']
                row_dict['rz_20_target_percentage'] = row['%Tgt']
                row_dict['rz_10_targets'] = row['10ydTgt']
                row_dict['rz_10_receptions'] = row['10ydRec']
                row_dict['rz_10_rec_yards'] = row['10ydYds']
                row_dict['rz_10_rec_td'] = row['10ydTD']
                row_dict['rz_10_target_percentage'] = row['10yd%Tgt']

            if row_dict['year'] == 0:
                print('No Player')
            else:
                print(row_dict)
                add_rz_stat(row_dict)
            break
