from flask import Flask
import os

from . import db

log_path = os.getenv("LOG_PATH")

# Non-Pushing Script
# def create_app():
#     app = Flask(__name__)
#     app.app_context().push()
#
#     from .weathers import weather
#     from .nfl_routes import nfl
#     from .player_route import player
#     from .teams import teams
#     from .home import home
#     from .nba_routes import nba
#     from .mlb_routes import mlb
#     from .download_routes import docs
#
#     app.register_blueprint(weather, url_prefix='/api')
#     app.register_blueprint(nfl, url_prefix='/api')
#     app.register_blueprint(player, url_prefix='/api')
#     app.register_blueprint(teams, url_prefix='/api')
#     app.register_blueprint(home, url_prefix='/api')
#     app.register_blueprint(nba, url_prefix='/api')
#     app.register_blueprint(mlb, url_prefix='/api')
#     app.register_blueprint(docs, url_prefix='/api')
#
#     return app


# Pushing Script
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
    # from .download_routes import docs

    app.register_blueprint(weather, url_prefix='/api')
    app.register_blueprint(nfl, url_prefix='/api')
    app.register_blueprint(player, url_prefix='/api')
    app.register_blueprint(teams, url_prefix='/api')
    app.register_blueprint(home, url_prefix='/api')
    app.register_blueprint(nba, url_prefix='/api')
    app.register_blueprint(mlb, url_prefix='/api')
    # app.register_blueprint(docs, url_prefix='/api')

    return app
