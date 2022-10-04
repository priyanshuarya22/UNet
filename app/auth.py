from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/', method=['POST'])
def login():
    username =  request.form.get('username')
    password = request.form.get('password')

    return render_template('index.html')


