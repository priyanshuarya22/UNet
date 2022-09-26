from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methodS=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:

