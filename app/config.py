import os

DB_NAME = 'database.db'
class Config():
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevelopmentConfig(Config):
    # SQLALCHEMY_DATABASE_URI = 'mysql://DtBEsm4DXK:' + str(os.getenv('databasePassword', default=None)) + '@remotemysql.com:3306/DtBEsm4DXK'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}'
    DEBUG = True
    SECRET_KEY = os.getenv('secretKey', default=None)
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = os.getenv('securityPasswordSalt', default=None)
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_UNAUTHORIZED_VIEW = None
