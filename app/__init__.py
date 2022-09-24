from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_NAME = "DtBEsm4DXK"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = key


