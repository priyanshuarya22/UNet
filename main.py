from flask import Flask
import os
from app import models
from app.database import db
from app.config import LocalDevelopmentConfig
from app.models import User, Role
import pyrebase

app = None
DB_NAME = 'database.db'

config = {
    "apiKey": str(os.getenv('apiKey', default=None)),
    "authDomain": str(os.getenv('authDomain', default=None)),
    "databaseURL": str(os.getenv('databaseURL', default=None)),
    "projectId": str(os.getenv('projectId', default=None)),
    "storageBucket": str(os.getenv('storageBucket', default=None)),
    "messagingSenderId": str(os.getenv('messagingSenderId', default=None))
}


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.app_context().push()
    return app


app = create_app()
firebase = pyrebase.initialize_app(config)
firebaseDb = firebase.database()

from app.controllers import *

if __name__ == '__main__':
    app.run()
