from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/',methods=['GET'])
def login():
    return render_template('index.html')
@auth.route('/', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password,password):
        flash('Username or password incorrect')
        return redirect('index.html')
    role_user = Role_user.query.filter_by(user_id=user.id).first()
    role = Role.query.filter_by(id=role_user.role_id).first()

    if role.name == 'admin':
        import main
        return redirect(url_for(main.admin_dash))


    return render_template('index.html')
