from .db import create_connection
from flask import jsonify, request, Blueprint

rz_stats = Blueprint("rz_stats", __name__)

@rz_stats.route('/rz_stat', methods=['POST'])
def add_rz_stat(json_dict):
    player_id = json_dict['player_id']
    team_id = json_dict['team_id']
    year = json_dict['year']
    rz_20_pass_att = json_dict['rz_20_pass_att']
    rz_20_pass_yard = json_dict['rz_20_pass_yards']
    rz_20_pass_td = json_dict['rz_20_pass_td']
    rz_20_pass_int = json_dict['rz_20_pass_int']
    rz_20_pass_comp_percentage = json_dict['rz_20_comp_percentage']
    rz_10_pass_att = json_dict['rz_10_pass_att']
    rz_10_pass_yard = json_dict['rz_10_pass_yards']
    rz_10_pass_td = json_dict['rz_10_pass_td']
    rz_10_pass_int = json_dict['rz_10_pass_int']
    rz_10_comp_percentage = json_dict['rz_10_comp_percentage']
    rz_20_targets = json_dict['rz_20_targets']
    rz_20_receptions = json_dict['rz_20_receptions']
    rz_20_rec_yards = json_dict['rz_20_rec_yards']
    rz_20_catch_percentage = json_dict['rz_20_catch_percentage']
    rz_20_rec_td = json_dict['rz_20_rec_td']
    rz_20_target_percentage = json_dict['rz_20_target_percentage']
    rz_10_targets = json_dict['rz_10_targets']
    rz_10_receptions = json_dict['rz_10_receptions']
    rz_10_rec_yards = json_dict['rz_10_rec_yards']
    rz_10_catch_percentage = json_dict['rz_10_catch_percentage']
    rz_10_rec_td = json_dict['rz_10_rec_td']
    rz_10_target_percentage = json_dict['rz_10_target_percentage']
    rz_20_rush_att = json_dict['rz_20_rush_att']
    rz_20_rush_yards = json_dict['rz_20_rush_yards']
    rz_20_rush_td = json_dict['rz_20_rush_td']
    rz_20_rush_percentage = json_dict['rz_20_rush_percentage']
    rz_10_rush_att = json_dict['rz_10_rush_att']
    rz_10_rush_yards = json_dict['rz_10_rush_yards']
    rz_10_rush_td = json_dict['rz_10_rush_td']
    rz_10_rush_percentage = json_dict['rz_10_rush_percentage']
    rz_5_rush_att = json_dict['rz_5_rush_att']
    rz_5_rush_yards = json_dict['rz_5_rush_yards']
    rz_5_rush_td = json_dict['rz_5_rush_td']
    rz_5_rush_percentage = json_dict['rz_5_rush_percentage']

    values = (player_id, team_id, year, rz_20_pass_att, rz_20_pass_yard, rz_20_pass_td, rz_20_pass_int, rz_20_pass_comp_percentage,
              rz_10_pass_att, rz_10_pass_yard, rz_10_pass_td, rz_10_pass_int, rz_10_comp_percentage, rz_20_targets, rz_20_receptions,
              rz_20_rec_yards, rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions,
              rz_10_rec_yards, rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_td,
              rz_20_rush_yards, rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_td, rz_10_rush_yards, rz_10_rush_percentage,
              rz_5_rush_att, rz_5_rush_td, rz_5_rush_yards, rz_5_rush_percentage)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO fb_red_zone (player_id, team_id, year, rz_20_pass_att, rz_20_pass_yards, rz_20_pass_td, rz_20_pass_int, rz_20_comp_percentage,
              rz_10_pass_att, rz_10_pass_yards, rz_10_pass_td, rz_10_pass_int, rz_10_comp_percentage, rz_20_targets, rz_20_receptions,
              rz_20_rec_yards, rz_20_catch_percentage, rz_20_rec_td, rz_20_target_percentage, rz_10_targets, rz_10_receptions,
              rz_10_rec_yards, rz_10_catch_percentage, rz_10_rec_td, rz_10_target_percentage, rz_20_rush_att, rz_20_rush_td,
              rz_20_rush_yards, rz_20_rush_percentage, rz_10_rush_att, rz_10_rush_td, rz_10_rush_yards, rz_10_rush_percentage,
              rz_5_rush_att, rz_5_rush_td, rz_5_rush_yards, rz_5_rush_percentage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (values))
    connection.commit()
    print(f"Game has been added to games tabel.")


    result = {'player_id':player_id, 'team_id': team_id, 'year': year, 'rz_20_pass_att': rz_20_pass_att, 'rz_20_pass_yard': rz_20_pass_yard,
              'rz_20_pass_td': rz_20_pass_td, 'rz_20_pass_int': rz_20_pass_int, 'rz_20_pass_comp_percentage': rz_20_pass_comp_percentage,
              'rz_10_pass_att': rz_10_pass_att, 'rz_10_pass_yard': rz_10_pass_yard, 'rz_10_pass_td': rz_10_pass_td, 'rz_10_pass_int': rz_10_pass_int,
              'rz_10_comp_percentage': rz_10_comp_percentage, 'rz_20_targets': rz_10_comp_percentage, 'rz_20_receptions': rz_20_receptions,
              'rz_20_rec_yards': rz_20_rec_yards, 'rz_20_catch_percentage': rz_20_catch_percentage, 'rz_20_rec_td': rz_20_rec_td, 'rz_20_target_percentage': rz_20_target_percentage,
              'rz_10_targets': rz_10_targets, 'rz_10_receptions': rz_10_targets, 'rz_10_rec_yards': rz_10_rec_yards, 'rz_10_catch_percentage': rz_10_catch_percentage,
              'rz_10_rec_td': rz_10_rec_td, 'rz_10_target_percentage': rz_10_target_percentage, 'rz_20_rush_att': rz_10_target_percentage, 'rz_20_rush_td': rz_20_rush_td,
              'rz_20_rush_yards': rz_20_rush_yards, 'rz_20_rush_percentage': rz_20_rush_percentage, 'rz_10_rush_att': rz_10_rush_att,
              'rz_10_rush_td': rz_10_rush_td, 'rz_10_rush_yards': rz_10_rush_yards, 'rz_10_rush_percentage': rz_10_rush_percentage,
              'rz_5_rush_att': rz_5_rush_att, 'rz_5_rush_td': rz_5_rush_att, 'rz_5_rush_yards': rz_5_rush_yards, 'rz_5_rush_percentage': rz_5_rush_percentage}

    return result

