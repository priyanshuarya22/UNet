from flask import Blueprint
from flask import Flask
import sys

app = Flask(__name__)
main = Blueprint('main', __name__)
arg = {'secretKey': sys.argv[1], 'databasePassword': sys.argv[2]}

if __name__ == '__main__':
    app.run()
