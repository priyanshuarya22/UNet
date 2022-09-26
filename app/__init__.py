from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
from run import arg

DB_NAME = "DtBEsm4DXK"
key = arg


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = key