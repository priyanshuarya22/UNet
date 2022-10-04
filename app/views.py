from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db, auth
import json

views = Blueprint('views', __name__)

@views.route('/', methodS=['GET'])
def index():
    return redirect(url_for(auth.login))

