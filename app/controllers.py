import os
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app.database import db
from app.models import *
from flask import render_template, request, redirect, session
from main import app, firebaseDb
from flask_session import Session
import bcrypt
import json


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
            session['userId'] = user.id
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


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        return render_template('test.html')
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        data = {
            "title": title,
            "description": desc
        }
        firebaseDb.child('noticeBoard').push(json.dumps(data))
        return render_template('test.html')


# ----------------- Teacher --------------------


@login_required
@app.route('/teacher', methods=['GET'])
def teacher_dash():
    if request.method == 'GET':
        user_id = session['userId']
        instructors = Instructor.query.filter_by(teacher_id=user_id).all()
        courseList = []
        for instructor in instructors:
            course = Course.query.filter_by(id=instructors.course_id).all()
            courseList.append(course)
        return render_template('teacher_dash.html', user_id=user_id, courseList=courseList)


@login_required
@app.route('/course_teacher', methods=['POST', 'GET'])
def teacher_course():
    if request.method == 'GET':
        return render_template('teacher_course_view.html')

    if request.method == 'POST':
        user_id = session['userId']
        file = request.files['file']
        file.os.path.join(app.config['Upload_folder'], secure_filename(file.filename))
        return render_template('teacher_course_view.html')


# ----------------- Student --------------------

@login_required
@app.route('/student', methods=['GET'])
def student_dash():
    if request.method == 'GET':
        user_id = session['userId']
        enrollments = Enrollment.query.filter_by(student_id=user_id).all()
        courseList = []
        for enrollment in enrollments:
            course = Course.query.filter_by(id=enrollment.course_id).first()
            courseList.append(course)
        return render_template('student_dash.html', user_id=user_id, courseList=courseList)


@login_required
@app.route('/leave', methods=['GET', 'POST'])
def student_leave():
    if request.method == 'GET':
        return render_template('leave.html')

    if request.method == 'POST':
        user_id = session['userId']
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        reason = request.form.get('reason')

        new_leave = Leave(from_date=checkout, to_date=checkin, student_id=user_id, reason=reason, status='Pending')
        db.session.add(new_leave)
        db.session.commit()

        return render_template('leave_applied.html', user_id=user_id)


@app.route('/assignment', methods=['GET', 'POST'])
def student_assignment():
    if request.method == 'GET':
        user_id = session['id']

        return render_template('assignment.html', user_id=user_id)

# ----------------- Course ---------------------


# ----------------- Warden ---------------------
