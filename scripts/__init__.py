from flask import Flask

from . import db

def create_app():
    app = Flask(__name__)
    app.app_context().push()

    from .weathers import weather
    from .players import players
    from .player import player
    from .teams import teams
    from .games import games
    from .rz_stats import rz_stats
    from .team import team

    app.register_blueprint(weather, url_prefix='/')
    app.register_blueprint(players, url_prefix='/')
    app.register_blueprint(player, url_prefix='/')
    app.register_blueprint(teams, url_prefix='/')
    app.register_blueprint(games, url_prefix='/')
    app.register_blueprint(rz_stats, url_prefix='/')
    app.register_blueprint(team, url_prefix='/')

    return app
