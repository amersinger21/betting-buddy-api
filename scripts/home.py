from .db import create_connection
from flask import Blueprint, request

home = Blueprint("home", __name__)

@home.route("/")
def homepage():
    return "This would be a home page"