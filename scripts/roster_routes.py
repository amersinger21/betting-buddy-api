from .db import create_connection
from flask import Blueprint, request, jsonify
import pandas as pd

roster = Blueprint("roster", __name__)

# nfl_team_dict = {'ARI': 1, 'ATL': 2, 'BAL': 3, 'BUF': 4, 'CAR': 5, 'CHI': 6, 'CIN': 7, 'CLE': 8, 'DAL': 9, 'DEN': 10,
#                  'DET': 11, 'GB': 12, 'HOU': 13, 'IND': 14, 'JAX': 15, 'KC': 16, 'LAC': 17, 'LAR': 18, 'LV': 19,
#                  'MIA': 20, 'MIN': 21, 'NE': 22, 'NO': 23, 'NYG': 24, 'NYJ': 25, 'PHI': 26, 'PIT': 27, 'SEA': 28,
#                  'SF': 29, 'TB': 30, 'TEN': 31, 'WAS': 32}

@roster.route('/roster', methods=['POST'])
def player_position():
    file = request.files['player_position']

    # Read CSV data
    df = pd.read_csv(file)

    for ind, row in df.iterrows():
        connection = create_connection()
        cursor = connection.cursor()

        values = [row['player_id'], row['position']]

        # execute sql query inserting into table
        cursor.execute(
            "INSERT INTO positions (player_id, position) VALUES (%s, %s)",
            (values))

        connection.commit()
        # print(f"{row['first_name']} {row['last_name']} has been added to player tabel.")

    return f"roster table has been updated"
