from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello Puliya!'


if __name__ == '__main__':
    from argparse import ArgumentParser

    app.run()
