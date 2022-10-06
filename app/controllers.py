import os
from werkzeug.security import generate_password_hash
from app.database import db
from app.models import *
from main import app
from flask import render_template, request, redirect, url_for, flash
import bcrypt


def login_required(func):
    global currentUser

    def wrapper():
        if currentUser is None:
            return redirect("/login")
        return func()

    return wrapper


@app.route('/', methods=['GET'])
@login_required
def index():
    global currentUser
    return render_template('index.html', user=currentUser.username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global currentUser
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        bytePwt = password.encode('utf-8')
        byteCheckPwt = str(user.password).encode('utf-8')
        check = bcrypt.checkpw(bytePwt, byteCheckPwt)
        if check:
            currentUser = user
            return redirect("/")
        else:
            print(user)
            return redirect("/login")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global currentUser
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        role = request.form.get('role')
        pno = request.form.get('pno')
        bytePwd = password.encode('utf-8')
        mySalt = bcrypt.gensalt()
        hashPassword = bcrypt.hashpw(bytePwd, mySalt)
        user = User(username=username, password=hashPassword, email=email, firstName=firstName, lastName=lastName,
                    pno=pno)
        db.session.add(user)
        roleObj = Role.query.filter_by(name=role).first()
        userRole = UserRole(user_id=user.id, role_id=roleObj.id)
        db.session.add(userRole)
        db.session.commit()
        currentUser = user
        return redirect("/")


currentUser = None
