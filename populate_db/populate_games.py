from scripts.games import add_game
import pandas as pd

import sqlite3
import pickle

db_file = '/Users/martymcflynn/Projects/betting_buddy_local/betting_buddy_local.db'
team_dict = pickle.load(open('/Users/martymcflynn/Projects/gamble_project/docs/team_dict.p', "rb"))[0]
inp_year = input('Enter Year: ')
# Import game information:
df_game = pd.read_csv('/Users/martymcflynn/Documents/Football_Documents/season_results/' + str(inp_year) + '_game_info.csv', index_col=0)
# df_game = df_game.loc[df_game['Week'] ]


for index, row in df_game.iterrows():
    row_dict = {
        'home_team_id': 0,
        'away_team_id': 0,
        'home_score': 0,
        'away_score': 0,
        'week': 0,
        'year': 0,
        'weather_id': 0,
        'vegas_line': 0,
        'vegas_line_result': '',
        'margin_of_victory': 0,
        'over_under': 0,
        'over_under_result': 0}

    home_name = row['Home Team']
    away_name = row['Away Team']

    # GET THE HOME TEAMS TEAM_ID
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # GET THE HOME TEAMS TEAM_ID
    c.execute("""SELECT id, name
                             FROM team
                             WHERE name=?""",
              ([home_name]))
    home_id = list(c.fetchone())[0]

    # GET THE AWAY TEAMS TEAM_ID
    c.execute("""SELECT id, name
                             FROM team
                             WHERE name=?""",
              [away_name])
    away_id = list(c.fetchone())[0]
    # GET THE FOREIGN KEY FROM THE TEAM TABLE
    row_dict['home_team_id'] = home_id
    row_dict['away_team_id'] = away_id
    row_dict['home_score'] = int(row['Home Score'])
    row_dict['away_score'] = int(row['Away Score'])
    row_dict['week'] = int(row['Week'])
    row_dict['year'] = int(row['Year'])

    # REWRITE OF THE VEGAS LINE
    line = row['Vegas Line'].split()
    if len(line) == 3:
        vegas_winner = team_dict[line[0] + ' ' + line[1]]
        points = line[2]
        spread = vegas_winner + ' ' + points
    else:
        try:
            vegas_winner = team_dict[line[0] + ' ' + line[1] + ' ' + line[2]]
            points_str = line[3]
            points = points_str[1:]
            spread = vegas_winner + ' ' + points
        except IndexError:
            vegas_winner = 'Pick Em'
            spread = vegas_winner
    row_dict['vegas_line'] = spread

    # CALCULATE IF SPREAD WAS MISSED
    if row['Home Score'] >= row['Away Score']:
        win_score = row['Home Score']
        loss_score = row['Away Score']
        win_team = row['Home Team']
    else:
        win_score = row['Away Score']
        loss_score = row['Home Score']
        win_team = row['Away Team']
    margin_of_victory = win_score - loss_score
    row_dict['margin_of_victory'] = int(margin_of_victory)

    if vegas_winner == win_team and float(margin_of_victory) > float(points):
        row_dict['vegas_line_result'] = 'Y'
    else:
        row_dict['vegas_line_result'] = 'N'

    # CALCULATE THE IF OVER_UNDER HIT
    row_dict['over_under'] = float(row['Over/Under'].split()[0])
    over_under_points = float(row['Over/Under'].split()[0])
    total_points = float(row['Home Score']) + float(row['Away Score'])
    if total_points > over_under_points:
        row_dict['over_under_result'] = 'Over'
    else:
        row_dict['over_under_result'] = 'Under'

    print(row_dict)
    print(add_game(row_dict))

