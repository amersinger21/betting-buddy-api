from scripts.team_offense import add_team_offense
import pandas as pd

import sqlite3
import pickle

db_file = '/Users/martymcflynn/Projects/betting_buddy_local/betting_buddy_local.db'
team_dict = pickle.load(open('/Users/martymcflynn/Projects/gamble_project/docs/team_dict.p', "rb"))[0]

# Offense Files:
dvoa = '/Users/martymcflynn/Documents/Football_Documents/team_stats/other_team_wb/dvoa_stats.csv'
epa = '/Users/martymcflynn/Documents/Football_Documents/team_stats/other_team_wb/epa_stats.csv'
conversions = '/Users/martymcflynn/Documents/Football_Documents/team_stats/offense/team_conversions.csv'
drives = '/Users/martymcflynn/Documents/Football_Documents/team_stats/offense/drive_results.csv'
scoring = '/Users/martymcflynn/Documents/Football_Documents/team_stats/offense/team_scoring.csv'
passing = '/Users/martymcflynn/Documents/Football_Documents/team_stats/offense/team_passing.csv'
rushing = '/Users/martymcflynn/Documents/Football_Documents/team_stats/offense/team_rushing.csv'




# Get list of teams:
df_team = pd.read_csv(rushing, index_col=0)
tm_lst = list(df_team['Team'].values)
teams = []
for team in tm_lst:
	if team not in teams:
		teams.append(team)
# print(len(teams))


years = list(range(2018, 2024))
for team in teams:
	# Get the team_id:
	conn = sqlite3.connect(db_file)
	c = conn.cursor()

	# Get the player_id from the player table:
	c.execute("""SELECT id, name FROM team
						WHERE name=?""", ([team]))
	team_id = list(c.fetchone())[0]

	for year in years:
		print(year)
		df_epa = pd.read_csv(epa, index_col=0)
		df_epa = df_epa.loc[(df_epa['Team'] == team) & (df_epa['Year'] == year)]
		df_dvoa = pd.read_csv(dvoa, index_col=0)
		df_dvoa = df_dvoa.loc[(df_dvoa['Team'] == team) & (df_dvoa['Year'] == year)]
		df_pass = pd.read_csv(passing, index_col=0)
		df_pass = df_pass.loc[(df_pass['Team'] == team) & (df_pass['Year'] == year)]
		df_rush = pd.read_csv(rushing, index_col=0)
		df_rush = df_rush.loc[(df_rush['Team'] == team) & (df_rush['Year'] == year)]
		df_scoring = pd.read_csv(scoring, index_col=0)
		df_scoring = df_scoring.loc[(df_scoring['Team'] == team) & (df_scoring['Year'] == year)]
		df_drives = pd.read_csv(drives, index_col=0)
		df_drives = df_drives.loc[(df_drives['Team'] == team) & (df_drives['Year'] == year)]
		df_conversion = pd.read_csv(conversions, index_col=0)
		df_conversion = df_conversion.loc[(df_conversion['Team'] == team) & (df_conversion['Year'] == year)]

		row_dict = {
			'team_id': 0,
			'year': 0,
			'games': 0,
			'off_dvoa': 0,
			'off_epa': 0,
			'dropback_epa': 0,
			'dropback_sr': 0,
			'rush_epa': 0,
			'rush_sr': 0,
			'pass_att': 0,
			'pass_comp': 0,
			'pass_yards': 0,
			'pass_td': 0,
			'int_thrown': 0,
			'pass_yards_att': 0,
			'pass_yards_per_game': 0,
			'sacks_taken': 0,
			'rush_att': 0,
			'rush_yards': 0,
			'rush_td': 0,
			'rush_yards_per_att': 0,
			'rush_yards_per_game': 0,
			'fumbles_lost': 0,
			'points_scored': 0,
			'points_scored_per_game': 0,
			'off_rz_plays': 0,
			'off_rz_td': 0,
			'total_drives': 0,
			'total_plays': 0,
			'scoring_percentage': 0,
			'to_percentage': 0,
			'avg_drive_play': 0,
			'avg_drive_points': 0,
			'avg_drive_yards': 0}

		row_dict['team_id'] = team_id
		for index, row in df_dvoa.iterrows():
			row_dict['off_dvoa'] = row['Offense DVOA Rank']
		for index, row in df_epa.iterrows():
			row_dict['off_epa'] = row['EPA Rank']
			row_dict['dropback_epa'] = row['Dropback EPA Rank']
			row_dict['dropback_sr'] = row['Dropback SR Rank']
			row_dict['rush_epa'] = row['Rush EPA Rank']
			row_dict['rush_sr'] = row['Rush SR Rank']
		for index, row in df_pass.iterrows():
			# print(row)
			row_dict['year'] = row['Year']
			row_dict['games'] = row['G']
			row_dict['pass_att'] = row['Att']
			row_dict['pass_comp'] = row['Cmp']
			row_dict['pass_yards'] = row['Yds']
			row_dict['pass_td'] = row['TD']
			row_dict['pass_yards_att'] = row['Y/A']
			row_dict['pass_yards_per_game'] = row['Y/G']
			row_dict['int_thrown'] = row['Int']
			row_dict['sacks_taken'] = row['Sk']
		for index, row in df_rush.iterrows():
			row_dict['rush_att'] = row['Att']
			row_dict['rush_yards'] = row['Yds']
			row_dict['rush_td'] = row['TD']
			row_dict['rush_yards_per_att'] = row['Y/A']
			row_dict['rush_yards_per_game'] = row['Y/G']
			row_dict['fumbles_lost'] = row['Fmb']
		for index, row in df_scoring.iterrows():
			row_dict['points_scored'] = row['Pts']
			row_dict['points_scored_per_game'] = row['Pts/G']
		for index, row in df_drives.iterrows():
			row_dict['total_drives'] = row['#Dr']
			row_dict['total_plays'] = row['Plays']
			row_dict['scoring_percentage'] = row['Sc%']
			row_dict['to_percentage'] = row['TO%']
			row_dict['avg_drive_play'] = row['AvgPlays']
			row_dict['avg_drive_yards'] = row['Yds']
			row_dict['avg_drive_points'] = row['Pts']
		for index, row in df_conversion.iterrows():
			row_dict['off_rz_plays'] = row['RZAtt']
			row_dict['off_rz_td'] = row['RZTD']
		print(row_dict)
		# print(len(row_dict))
		print(add_team_offense(row_dict))

# print(years)
#
#
# # x = '''team_id, year, games, off_dvoa, off_epa, dropback_epa, dropback_sr, rush_epa, rush_sr, pass_att, pass_comp, pass_yards,
# #               pass_td, int_thrown, pass_yards_att, pass_yards_per_game, sacks_taken, rush_att, rush_yards, rush_td, rush_yards_per_att,
# #               rush_yards_per_game, fumbles_lost, points_scored, points_scored_per_game, off_rz_plays, off_rz_td, total_drives, total_plays,
# #               scoring_percentage, to_percentage, avg_drive_play, avg_drive_points, avg_drive_yards'''
# x = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s'
# x = x.split()
#
# print(len(x))