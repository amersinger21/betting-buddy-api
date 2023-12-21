from scripts.team_defense import add_team_defense
import pandas as pd
import os

import sqlite3
import pickle

db_file = '/Users/martymcflynn/Projects/betting_buddy_local/betting_buddy_local.db'
team_dict = pickle.load(open('/Users/martymcflynn/Projects/gamble_project/docs/team_dict.p', "rb"))[0]

# Offense Files:
dvoa = '/Users/martymcflynn/Documents/Football_Documents/team_stats/other_team_wb/dvoa_stats.csv'
epa = '/Users/martymcflynn/Documents/Football_Documents/team_stats/other_team_wb/epa_stats.csv'
conversions = '/Users/martymcflynn/Documents/Football_Documents/team_stats/defense/team_conversions.csv'
drives = '/Users/martymcflynn/Documents/Football_Documents/team_stats/defense/drive_results.csv'
scoring = '/Users/martymcflynn/Documents/Football_Documents/team_stats/defense/scoring_defense.csv'
passing = '/Users/martymcflynn/Documents/Football_Documents/team_stats/defense/pass_defense.csv'
rushing = '/Users/martymcflynn/Documents/Football_Documents/team_stats/defense/rush_defense.csv'
qb_split = '/Users/martymcflynn/Documents/Football_Documents/defense_splits/qb_defense_splits.csv'
rb_split = '/Users/martymcflynn/Documents/Football_Documents/defense_splits/rb_defense_splits.csv'
wr_split = '/Users/martymcflynn/Documents/Football_Documents/defense_splits/wr_defense_splits.csv'
te_split = '/Users/martymcflynn/Documents/Football_Documents/defense_splits/te_defense_splits.csv'

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
		df_qb_split = pd.read_csv(qb_split, index_col=0)
		df_qb_split = df_qb_split.loc[(df_qb_split['Team'] == team) & (df_qb_split['Year'] == year)]
		df_rb_split = pd.read_csv(rb_split, index_col=0)
		df_rb_split = df_rb_split.loc[(df_rb_split['Team'] == team) & (df_rb_split['Year'] == year)]
		df_wr_split = pd.read_csv(wr_split, index_col=0)
		df_wr_split = df_wr_split.loc[(df_wr_split['Team'] == team) & (df_wr_split['Year'] == year)]
		df_te_split = pd.read_csv(te_split, index_col=0)
		df_te_split = df_te_split.loc[(df_te_split['Team'] == team) & (df_te_split['Year'] == year)]

		# row_dict = {}
		row_dict = {
			'team_id': 0,
			'year': 0,
			'games': 0,
			'def_dvoa': 0,
			'def_epa': 0,
			'def_dropback_epa': 0,
			'def_dropback_sr': 0,
			'def_rush_epa': 0,
			'def_rush_sr': 0,
			'pass_comp_allowed': 0,
			'pass_att_faced': 0,
			'pass_yards_allowed': 0,
			'pass_td_allowed': 0,
			'allowed_pyards_per_att': 0,
			'allowed_pyards_per_game': 0,
			'qb_hits': 0,
			'qb_sacks': 0,
			'ints': 0,
			'rush_att_faced': 0,
			'rush_yards_allowed': 0,
			'rush_td_allowed': 0,
			'allowed_ryards_per_att': 0,
			'allowed_ryards_per_game': 0,
			'rec_allowed': 0,
			'rec_td_allowed': 0,
			'points_allowed': 0,
			'points_per_game_allowed': 0,
			'rz_att_faced': 0,
			'rz_td_allowed': 0,
			'rz_td_allowed_percentage': 0,
			'drives_faced': 0,
			'plays_faced': 0,
			'score_against_percentage': 0,
			'def_to_percentage': 0,
			'plays_faced_per_drive': 0,
            'yards_allowed_per_drive': 0,
            'points_allowed_per_drive': 0,
			'TE_targets': 0,
			'TE_rec': 0,
			'TE_yards': 0,
			'TE_td': 0,
			'WR_targets': 0,
			'WR_rec': 0,
			'WR_yards': 0,
			'WR_td': 0,
			'RB_targets': 0,
			'RB_rec': 0,
			'RB_rec_yards': 0,
			'RB_rec_td': 0,
			'RB_att': 0,
			'RB_rush_yards': 0,
			'RB_rush_td': 0,
			'QB_completions': 0,
			'QB_att': 0,
			'QB_yards': 0,
			'QB_rush_att': 0,
			'QB_rush_yards': 0,
			'QB_rush_td': 0
		}

		row_dict['team_id'] = team_id
		for index, row in df_dvoa.iterrows():
			row_dict['def_dvoa'] = row['Defense DVOA Rank']
		for index, row in df_epa.iterrows():
			# print(row)
			row_dict['def_epa'] = row['EPA Rank']
			row_dict['def_dropback_epa'] = row['Dropback EPA Rank']
			row_dict['def_dropback_sr'] = row['Dropback SR Rank']
			row_dict['def_rush_epa'] = row['Rush EPA Rank']
			row_dict['def_rush_sr'] = row['Rush SR Rank']
		for index, row in df_pass.iterrows():
			row_dict['year'] = row['Year']
			row_dict['games'] = row['G']
			row_dict['pass_att_faced'] = row['Att']
			row_dict['pass_comp_allowed'] = row['Cmp']
			row_dict['pass_yards_allowed'] = row['Yds']
			row_dict['pass_td_allowed'] = row['TD']
			row_dict['allowed_pyards_per_att'] = row['Y/A']
			row_dict['allowed_pyards_per_game'] = row['Y/G']
			row_dict['qb_hits'] = row['QBHits']
			row_dict['qb_sacks'] = row['Sk']
			row_dict['ints'] = row['Int']
			row_dict['rec_allowed'] = row['Cmp']
			row_dict['rec_td_allowed'] = row['TD']
		for index, row in df_rush.iterrows():
			row_dict['rush_att_faced'] = row['Att']
			row_dict['rush_yards_allowed'] = row['Yds']
			row_dict['rush_td_allowed'] = row['TD']
			row_dict['allowed_ryards_per_att'] = row['Y/A']
			row_dict['allowed_ryards_per_game'] = row['Y/G']
		for index, row in df_scoring.iterrows():
			row_dict['points_allowed'] = row['Pts']
			row_dict['points_per_game_allowed'] = row['Pts/G']
		for index, row in df_drives.iterrows():
			row_dict['drives_faced'] = row['#Dr']
			row_dict['plays_faced'] = row['Plays']
			row_dict['score_against_percentage'] = row['Sc%']
			row_dict['def_to_percentage'] = row['TO%']
			row_dict['plays_faced_per_drive'] = row['AvgPlays']
			row_dict['yards_allowed_per_drive'] = row['Yds']
			row_dict['points_allowed_per_drive'] = row['Pts']
		for index, row in df_conversion.iterrows():
			row_dict['rz_att_faced'] = row['RZAtt']
			row_dict['rz_td_allowed'] = row['RZTD']
			row_dict['rz_td_allowed_percentage'] = row['RZPct']
		for index, row in df_te_split.iterrows():
			row_dict['TE_targets'] = row['Tgt']
			row_dict['TE_rec'] = row['Rec']
			row_dict['TE_yards'] = row['Yds']
			row_dict['TE_td'] = row['TD']
		for index, row in df_wr_split.iterrows():
			row_dict['WR_targets'] = row['Tgt']
			row_dict['WR_rec'] = row['Rec']
			row_dict['WR_rec'] = row['Yds']
			row_dict['WR_td'] = row['TD']
		for index, row in df_rb_split.iterrows():
			row_dict['RB_targets'] = row['Tgt']
			row_dict['RB_rec'] = row['Rec']
			row_dict['RB_rec_yards'] = row['RecYds']
			row_dict['RB_rec_td'] = row['RecTd']
			row_dict['RB_att'] = row['Att']
			row_dict['RB_rush_yards'] = row['Yds']
			row_dict['RB_rush_td'] = row['TD']
		for index, row in df_qb_split.iterrows():
			row_dict['QB_completions'] = row['Cmp']
			row_dict['QB_att'] = row['Att']
			row_dict['QB_yards'] = row['Yds']
			row_dict['QB_rush_att'] = row['RusAtt']
			row_dict['QB_rush_yards'] = row['RusYds']
			row_dict['QB_rush_td'] = row['RusTD']
		print(row_dict)
		# add_team_defense(row_dict)