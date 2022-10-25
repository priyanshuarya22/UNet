import os
from functools import wraps

from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app.database import db
from app.models import *
from flask import render_template, request, redirect, session
from main import app, firebaseDb
from flask_session import Session
import bcrypt
import json
from datetime import datetime


# ------------ Decorators ---------------
def login_required(func):
    @wraps(func)
    def wrapper():
        if session.get('username', None) is None:
            return redirect("/401")
        return func()

    return wrapper


def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get('role', None) != role:
                return redirect("/403")
            return func()

        return wrapper

    return decorator


# ------------- Miscellaneous ---------------

@app.route('/403', methods=['GET'])
def no_permission():
    return render_template('403.html')


@app.route('/401', methods=['GET'])
def not_logged_in():
    return render_template('401.html')


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')


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
        if user is None:
            return render_template('login.html', error='Username does not exist!')
        byteCheckPwt = str(user.password).encode('utf-8')
        check = bcrypt.checkpw(bytePwt, byteCheckPwt)
        if check:
            session['username'] = user.username
            userRole = UserRole.query.filter_by(user_id=user.id).first()
            role = Role.query.filter_by(id=userRole.role_id).first()
            session['role'] = role.name
            session['userId'] = user.id
            session['firstName'] = user.firstName
            return redirect('/redirect')
        else:
            return render_template('login.html', error='Username or Password Incorrect!')


@app.route('/redirect', methods=['GET'])
def redirector():
    role = session.get('role', None)
    if role is None:
        return redirect('/')
    elif role == 'admin':
        return redirect('/admin')
    elif role == 'teacher':
        return redirect('/teacher')
    elif role == 'student':
        return redirect('/student')
    elif role == 'warden':
        return redirect('/warden')
    else:
        return 404


# ----------------- Admin ----------------------


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        return render_template('test.html')
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        data = {
            "title": title,
            "description": desc,
            "date_time": dt_string
        }
        firebaseDb.child('noticeBoard').push(json.dumps(data))
        return render_template('test.html')


# ----------------- Teacher --------------------


@app.route('/teacher', methods=['GET'])
@login_required
@role_required('teacher')
def teacher_dash():
    firstName = session['firstName']
    return render_template('teacher_dash.html', firstName=firstName)
    # user_id = session['userId']
    # instructors = Instructor.query.filter_by(teacher_id=user_id).all()
    # courseList = []
    # for instructor in instructors:
    #     course = Course.query.filter_by(id=instructors.course_id).all()
    #     courseList.append(course)
    # return render_template('teacher_dash.html', user_id=user_id, courseList=courseList)


@app.route('/course_teacher', methods=['POST', 'GET'])
@login_required
@role_required('teacher')
def teacher_course():
    if request.method == 'GET':
        return render_template('teacher_course_view.html')

    if request.method == 'POST':
        user_id = session['userId']
        file = request.files['file']
        file.os.path.join(app.config['Upload_folder'], secure_filename(file.filename))
        return render_template('teacher_course_view.html')


# ----------------- Student --------------------

@app.route('/student', methods=['GET'])
@login_required
@role_required('student')
def student_dash():
    firstName = session['firstName']
    notices = firebaseDb.child('noticeBoard').get()
    rawNoticeList = notices.val()
    noticeList = []
    k = 0
    for i in rawNoticeList.values():
        if k == 10:
            break
        k += 1
        j = json.loads(i)
        noticeList.append(j)
    noticeList.reverse()
    return render_template('student_dash.html', firstName=firstName, noticeList=noticeList)
    # if request.method == 'GET':
    #     user_id = session['userId']
    #     enrollments = Enrollment.query.filter_by(student_id=user_id).all()
    #     courseList = []
    #     for enrollment in enrollments:
    #         course = Course.query.filter_by(id=enrollment.course_id).first()
    #         courseList.append(course)
    #     return render_template('student_dash.html', user_id=user_id, courseList=courseList)


@app.route('/leave', methods=['GET', 'POST'])
@login_required
@role_required('student')
def student_leave():
    firstName = session['firstName']
    if request.method == 'GET':
        return render_template('leave.html', firstName=firstName)
    if request.method == 'POST':
        user_id = session['userId']
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        reason = request.form.get('reason')
        new_leave = Leave(from_date=checkout, to_date=checkin, student_id=user_id, reason=reason, status='Pending')
        db.session.add(new_leave)
        db.session.commit()
        return render_template('leave_applied.html', firstName=firstName)


@app.route('/assignment', methods=['GET', 'POST'])
@role_required('student')
def student_assignment():
    if request.method == 'GET':
        user_id = session['id']

        return render_template('assignment.html', user_id=user_id)

# ----------------- Course ---------------------


# ----------------- Warden ---------------------
