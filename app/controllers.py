import os
from werkzeug.security import generate_password_hash
from app.database import db
from app.models import *
from flask import render_template, request, redirect, session
from main import app
from flask_session import Session
import bcrypt


# ------------ Decorators ---------------
def login_required(func):
    def wrapper():
        if session.get('username', None) is None:
            return redirect("/")
        return func()

    return wrapper


# -------------- Login ----------------------

@app.route('/', methods=['GET', 'POST'])
def login():
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
            session['username'] = user.username
            userRole = UserRole.query.filter_by(user_id=user.id).first()
            role = Role.query.filter_by(id=userRole.role_id).first()
            session['role'] = role.name
            session['id'] = user.id
            if role.name == 'admin':
                return redirect('/admin')
            elif role.name == 'teacher':
                return redirect('/teacher')
            elif role.name == 'student':
                return redirect('/student')
            elif role.name == 'warden':
                return redirect('/warden')
            else:
                return 404
        else:
            return render_template('login.html', error='Username or Password Incorrect!')


# ----------------- Admin ----------------------


# ----------------- Teacher --------------------


# ----------------- Student --------------------

@app.route('/student', methods=['GET'])
def student_dash():
    if request.method == 'GET':
        user_id = session['id']
        enrollments = Enrollment.query.filter_by(student_id=user_id).all()
        courseList = []
        for enrollment in enrollments:
            course = Course.query.filter_by(id=enrollment.course_id).first()
            courseList.append(course)
        return render_template('student_dash.html', user_id=user_id, courseList=courseList)


@app.route('/leave', methods=['GET', 'POST'])
def student_leave():
    if request.method == 'GET':
        return render_template('leave.html')

    if request.method == 'POST':
        user_id = session['id']
        return render_template('leave.html', user_id=user_id)



# ----------------- Course ---------------------


# ----------------- Warden ---------------------
