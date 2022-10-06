from flask import Flask
from os import path
from app import models
from app.database import db
from flask_security import Security, SQLAlchemySessionUserDatastore
from app.config import LocalDevelopmentConfig
from app.models import User, Role

app = None
DB_NAME = 'database.db'


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()
    return app


app = create_app()

from app.controllers import *

if __name__ == '__main__':
    app.run(debug=True)
