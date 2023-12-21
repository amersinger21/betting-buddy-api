import pandas as pd

import sqlite3
import pickle


from scripts.player_games import add_player_games
db_file = '/Users/martymcflynn/Projects/betting_buddy_local/betting_buddy_local.db'
# team_dict = pickle.load(open('/Users/martymcflynn/Projects/gamble_project/docs/team_dict.p', "rb"))[0]
inp_year = input('Enter Year: ')

# Import game information:
file = '/Users/martymcflynn/Documents/Football_Documents/game_logs/' + str(inp_year) + '/' + str(inp_year) + '_player_offense.csv'
df_game = pd.read_csv(file, index_col=0)

count = 0
for index, row in df_game.iterrows():
    # Initialize variables
    opponent_id = 0
    row_dict = {
        'player_id': 0,
        'game_id': 0,
        'team_id': 0,
        'opp_id': 0,
        'pass_att': 0,
        'pass_comp': 0,
        'pass_yards': 0,
        'pass_td': 0,
        'pass_longest': 0,
        'ints': 0,
        'sacks': 0,
        'rush_att': 0,
        'rush_yards': 0,
        'rush_td': 0,
        'rush_longest': 0,
        'targets': 0,
        'rec': 0,
        'rec_yards': 0,
        'rec_td': 0,
        'rec_longest': 0,
        'fumbles': 0,}

    player = row['Player'].split()
    if len(player) <= 2:
        last_name = player[1]
        first_name = player [0]
    else:
        last_name = player[1] + ' ' + player[2]
        first_name = player[0]
    print(first_name + ' ' + last_name)
    year = row['Year']
    week = row['Week']
    team_abbr = row['Team']

    # Connect to the local DB:
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Get the player_id from the player table:
    c.execute("""SELECT id, last_name, first_name, position
                             FROM player
                             WHERE last_name=?
                                and first_name=?""",
              ([last_name, first_name]))
    try:
        player_id = list(c.fetchone())[0]
        # print(player_id)
        row_dict['player_id'] = player_id
    except TypeError:
        continue
    # Get the home_team_id and away_team_id from games:
    c.execute("""SELECT id
                             FROM team
                             WHERE name=?""",
              ([team_abbr]))

    team_id = list(c.fetchone())[0]
    # print(team_id)
    row_dict['team_id'] = team_id
    # print(year)

    # # Get the home_team_id and away_team_id from games:
    c.execute("""SELECT id, home_team_id, away_team_id, home_score, away_score
                             FROM games
                             WHERE (away_team_id=? OR home_team_id=?)
                             and week=?
                             and year=?""",
              ([team_id, team_id, week, year]))
    results = list(c.fetchone())
    game_id = results[0]
    home_id = results[1]
    away_id = results[2]
    if team_id == home_id:
        opponent_id = away_id
    else:
        opponent_id = home_id

    row_dict['game_id'] = game_id
    row_dict['opp_id'] = opponent_id
    row_dict['pass_comp'] = row['Cmp']
    row_dict['pass_att'] = row['Att']
    row_dict['pass_yards'] = row['PYds']
    row_dict['pass_td'] = row['TD']
    row_dict['ints'] = row['Int']
    row_dict['sacks'] = row['Sk']
    row_dict['pass_longest'] = row['Lng']
    row_dict['rush_att'] = row['RusAtt']
    row_dict['rush_yards'] = row['RusYds']
    row_dict['rush_td'] = row['RusTD']
    row_dict['rush_longest'] = row['RusLng']
    row_dict['targets'] = row['Tgt']
    row_dict['rec'] = row['Rec']
    row_dict['rec_yards'] = row['RecYds']
    row_dict['rec_td'] = row['RecTD']
    row_dict['rec_longest'] = row['RecLng']
    row_dict['fumbles'] = row['Fmb']

    count += 1
    print(row_dict)
    # add_player_games(row_dict)
        # results = list(c.fetchone())[0]

# print(count)