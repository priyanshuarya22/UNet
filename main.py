from flask import Flask
from app.database import db
from flask_security import Security, SQLAlchemySessionUserDatastore
from app.models import User, Role
from app.config import LocalDevelopmentConfig

app = None


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore)
    return app


app = create_app()

from app.controllers import *

if __name__ == '__main__':
    app.run()
