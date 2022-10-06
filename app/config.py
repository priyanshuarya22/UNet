import os

user = 'DtBEsm4DXK'
password = str(os.getenv('databasePassword', default=None))
host = 'remotemysql.com'
port = 3306
database = 'DtBEsm4DXK'


class Config():
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(
        user, password, host, port, database
    )
    DEBUG = True
    SECRET_KEY = os.getenv('secretKey', default=None)
