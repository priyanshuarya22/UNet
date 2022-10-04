from flask import Blueprint, redirect
from flask import Flask
import sys
from app import create_app

app = create_app()
arg = {'secretKey': sys.argv[1], 'databasePassword': sys.argv[2]}


if __name__ == '__main__':
    app.run(debug=True)
