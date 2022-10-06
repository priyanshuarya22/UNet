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
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = os.getenv('securityPasswordSalt', default=None)
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_UNAUTHORIZED_VIEW = None
