from .db import create_connection
from flask import Blueprint

team_defense = Blueprint("team_defense", __name__)

@team_defense.route('/team_defense', methods=['POST'])
def add_team_defense(json_dict):
    team_id = json_dict['team_id']
    year = json_dict['year']
    games = json_dict['games']
    def_dvoa = json_dict['def_dvoa']
    def_epa = json_dict['def_epa']
    def_dropback_epa = json_dict['def_dropback_epa']
    def_dropback_sr = json_dict['def_dropback_sr']
    def_rush_epa = json_dict['def_rush_epa']
    def_rush_sr = json_dict['def_rush_sr']
    pass_att_faced = json_dict['pass_att_faced']
    pass_comp_allowed = json_dict['pass_comp_allowed']
    pass_yards_allowed = json_dict['pass_yards_allowed']
    pass_td_allowed = json_dict['pass_td_allowed']
    allowed_pyards_per_att = json_dict['allowed_pyards_per_att']
    allowed_pyards_per_game = json_dict['allowed_pyards_per_game']
    qb_hits = json_dict['qb_hits']
    qb_sacks = json_dict['qb_sacks']
    ints = json_dict['ints']
    rush_att_faced = json_dict['rush_att_faced']
    rush_yards_allowed = json_dict['rush_yards_allowed']
    rush_td_allowed = json_dict['rush_td_allowed']
    allowed_ryards_per_att = json_dict['allowed_ryards_per_att']
    allowed_ryards_per_game = json_dict['allowed_ryards_per_game']
    rec_allowed = json_dict['rec_allowed']
    rec_td_allowed = json_dict['rec_td_allowed']
    points_allowed = json_dict['points_allowed']
    points_per_game_allowed = json_dict['points_per_game_allowed']
    rz_att_faced = json_dict['rz_att_faced']
    rz_td_allowed = json_dict['rz_td_allowed']
    rz_td_allowed_percentage = json_dict['rz_td_allowed_percentage']
    drives_faced = json_dict['drives_faced']
    plays_faced = json_dict['plays_faced']
    score_against_percentage = json_dict['score_against_percentage']
    def_to_percentage = json_dict['def_to_percentage']
    plays_faced_per_drive = json_dict['plays_faced_per_drive']
    yards_allowed_per_drive = json_dict['yards_allowed_per_drive']
    points_allowed_per_drive = json_dict['points_allowed_per_drive']
    TE_targets = json_dict['TE_targets']
    TE_rec = json_dict['TE_rec']
    TE_yards = json_dict['TE_yards']
    TE_td = json_dict['TE_td']
    WR_targets = json_dict['WR_targets']
    WR_rec = json_dict['WR_rec']
    WR_yards = json_dict['WR_yards']
    WR_td = json_dict['WR_td']
    RB_targets = json_dict['RB_targets']
    RB_rec = json_dict['RB_rec']
    RB_rec_yards = json_dict['RB_rec_yards']
    RB_rec_td = json_dict['RB_rec_td']
    RB_att = json_dict['RB_att']
    RB_rush_yards = json_dict['RB_rush_yards']
    RB_rush_td = json_dict['RB_rush_td']
    QB_completions = json_dict['QB_completions']
    QB_att = json_dict['QB_att']
    QB_yards = json_dict['QB_yards']
    QB_rush_att = json_dict['QB_rush_att']
    QB_rush_yards = json_dict['QB_rush_yards']
    QB_rush_td = json_dict['QB_rush_td']


    values = (team_id, year, games, def_dvoa, def_epa, def_dropback_epa, def_dropback_sr, def_rush_epa, def_rush_sr,
    pass_comp_allowed, pass_att_faced, pass_yards_allowed, pass_td_allowed, allowed_pyards_per_att, allowed_pyards_per_game,
    qb_hits, qb_sacks, ints, rush_att_faced, rush_yards_allowed, rush_td_allowed, allowed_ryards_per_att, allowed_ryards_per_game,
    rec_allowed, rec_td_allowed, points_allowed, points_per_game_allowed,  rz_att_faced, rz_td_allowed, rz_td_allowed_percentage,
    drives_faced, plays_faced, score_against_percentage, def_to_percentage, plays_faced_per_drive, yards_allowed_per_drive,
    points_allowed_per_drive, TE_targets, TE_rec, TE_yards, TE_td, WR_targets, WR_rec, WR_yards, WR_td, RB_targets, RB_rec,
    RB_rec_yards, RB_rec_td, RB_att, RB_rush_yards, RB_rush_td, QB_completions, QB_att, QB_yards, QB_rush_att, QB_rush_yards, QB_rush_td)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO fb_def_stats (team_id, year, games, def_dvoa, def_epa, def_dropback_epa, def_dropback_sr, def_rush_epa, def_rush_sr,
    pass_comp_allowed, pass_att_faced, pass_yards_allowed, pass_td_allowed, allowed_pyards_per_att, allowed_pyards_per_game,
    qb_hits, qb_sacks, ints, rush_att_faced, rush_yards_allowed, rush_td_allowed, allowed_ryards_per_att, allowed_ryards_per_game,
    rec_allowed, rec_td_allowed, points_allowed, points_per_game_allowed,  rz_att_faced, rz_td_allowed, rz_td_allowed_percentage,
    drives_faced, plays_faced, score_against_percentage, def_to_percentage, plays_faced_per_drive, yards_allowed_per_drive,
    points_allowed_per_drive, TE_targets, TE_rec, TE_yards, TE_td, WR_targets, WR_rec, WR_yards, WR_td, RB_targets, RB_rec,
    RB_rec_yards, RB_rec_td, RB_att, RB_rush_yards, RB_rush_td, QB_completions, QB_att, QB_yards, QB_rush_att, QB_rush_yards, QB_rush_td) VALUES 
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))
    connection.commit()
    print(f"Team {year}  defensive stats has been added to fb_team_off table.")


    result = {'team_id': team_id, 'year': year, 'games': games, 'def_dvoa': def_dvoa, 'def_epa': def_epa, 'def_dropback_epa': def_dropback_epa,
              'def_dropback_sr': def_dropback_sr, 'def_rush_epa': def_rush_epa, 'def_rush_sr': def_rush_sr, 'pass_att_faced': pass_att_faced,
              'pass_comp_allowed': pass_comp_allowed, 'pass_yards_allowed': pass_yards_allowed, 'pass_td_allowed': pass_td_allowed,
              'allowed_pyards_per_att': allowed_pyards_per_att, 'allowed_pyards_per_game': allowed_pyards_per_game, 'qb_hits': qb_hits, 'qb_sacks': qb_sacks,
              'rush_att_faced': rush_att_faced, 'rush_yards_allowed': rush_yards_allowed, 'rush_td_allowed': rush_td_allowed, 'allowed_ryards_per_att': allowed_ryards_per_att,
              'allowed_ryards_per_game': allowed_ryards_per_game, 'rec_allowed': rec_allowed, 'rec_td_allowed': rec_td_allowed,
              'points_allowed': points_allowed, 'points_per_game_allowed': points_per_game_allowed,  'rz_att_faced': rz_att_faced,
              'rz_td_allowed': rz_td_allowed, 'rz_td_allowed_percentage': rz_td_allowed_percentage, 'drives_faced': drives_faced,
              'plays_faced': plays_faced, 'score_against_percentage': score_against_percentage, 'def_to_percentage': def_to_percentage,
              'plays_faced_per_drive': plays_faced_per_drive, 'yards_allowed_per_drive': yards_allowed_per_drive, 'points_allowed_per_drive': points_allowed_per_drive,
              'TE_targets': TE_targets, 'TE_rec': TE_rec, 'TE_yards': TE_yards, 'TE_td': TE_td, 'WR_targets': WR_targets, 'WR_rec': WR_rec,
              'WR_yards': WR_yards, 'WR_td': WR_td, 'RB_targets': RB_targets, 'RB_rec': RB_rec, 'RB_rec_yards': RB_rec_yards, 'RB_rec_td': RB_rec_td,
              'RB_att': RB_att, 'RB_rush_yards': RB_rush_yards, 'RB_rush_td': RB_rush_td, 'QB_completions': QB_completions, 'QB_att': QB_att, 'QB_yards': QB_yards,
              'QB_rush_att': QB_rush_att, 'QB_rush_yards': QB_rush_yards, 'QB_rush_td': QB_rush_td}

    return result