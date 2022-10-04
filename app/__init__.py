from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
from main import arg

db = SQLAlchemy()
key = arg


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://DtBEsm4DXK:' + key['databasePassword'] + '@remotemysql.com:3306' \
                                                                                              '/DtBEsm4DXK '
    db.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
