import datetime
from datetime import datetime, timedelta
import time, os

# Get date
def nba_get_game_date():
    n_days_ago = 1
    today = datetime.now()
    n_days_ago = today - timedelta(days=n_days_ago)
    game_day = str(n_days_ago)[:10].split('-')
    game_day = ''.join(game_day)
    return game_day