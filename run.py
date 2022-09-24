from flask import Flask
import sys

app = Flask(__name__)
arg = sys.argv[1]


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello Puliya!'


if __name__ == '__main__':
    app.run()
