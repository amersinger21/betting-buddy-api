from dotenv import load_dotenv

load_dotenv()
import os
import pymysql

from flask import current_app, g

def create_connection():
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        passwd=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        autocommit=True,
        ssl={
            "ca": "/etc/ssl/cert.pem"
        }
    )

    return connection

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        # close the database
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)