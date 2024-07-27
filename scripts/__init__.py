from flask import Flask

from . import db

def create_app():
    app = Flask(__name__)
    app.app_context().push()

    from .weathers import weather
    from .nfl_routes import nfl
    from .player_route import player
    from .teams import teams
    from .home import home
    from .nba_routes import nba
    from .mlb_routes import mlb

    app.register_blueprint(weather, url_prefix='/api')
    app.register_blueprint(nfl, url_prefix='/api')
    app.register_blueprint(player, url_prefix='/api')
    app.register_blueprint(teams, url_prefix='/api')
    app.register_blueprint(home, url_prefix='/api')
    app.register_blueprint(nba, url_prefix='/api')
    app.register_blueprint(mlb, url_prefix='/api')

    return app
