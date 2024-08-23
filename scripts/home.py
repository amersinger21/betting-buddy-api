from .db import create_connection
from flask import Blueprint, request

home = Blueprint("home", __name__)

@home.route("/api")
def homepage():
    return "Welcome to The Betting Buddy API - visit the main site to search data!"

