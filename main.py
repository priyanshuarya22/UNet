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
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore)
    create_database(app)

    return app


def create_database(app):
    if not path.exists('app/' + DB_NAME):
        db.create_all(app=app)


app = create_app()

from app.controllers import *

if __name__ == '__main__':
    app.run(debug=True)
