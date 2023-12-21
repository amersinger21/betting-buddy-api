from flask import Flask

from . import db

def create_app():
    app = Flask(__name__)
    app.app_context().push()

    from .weathers import weather
    from .players import player
    from .player_games import player_stats
    from .teams import team
    from .sports import sport
    from .games import games
    from .rz_stats import rz_stats
    from .team_offense import team_offense
    from .team_defense import team_defense

    app.register_blueprint(sport, url_prefix='/')
    app.register_blueprint(team, url_prefix='/')
    app.register_blueprint(weather, url_prefix='/')
    app.register_blueprint(player, url_prefix='/')
    app.register_blueprint(games, url_prefix='/')
    app.register_blueprint(rz_stats, url_prefix='/')
    app.register_blueprint(team_offense, url_prefix='/')
    app.register_blueprint(team_defense, url_prefix='/')
    app.register_blueprint(player_stats, url_prefix='/')

    return app
