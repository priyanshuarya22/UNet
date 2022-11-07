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
    def wrapper(*args, **kwargs):
        if session.get('username', None) is None:
            return redirect("/401")
        return func(*args, **kwargs)

    return wrapper


def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get('role', None) != role:
                return redirect("/403")
            return func(*args, **kwargs)

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

@app.route('/admin', methods=['GET'])
@login_required
@role_required('admin')
def admin():
    firstName = session['firstName']
    notices = firebaseDb.child('noticeBoard').get()
    rawNoticeList = notices.val()
    if rawNoticeList is None:
        return render_template('admin_dash.html', firstName=firstName, empty=True)
    noticeList = []
    for i, j in rawNoticeList.items():
        k = json.loads(j)
        k['key'] = i
        noticeList.append(k)
    noticeList.reverse()
    return render_template('admin_dash.html', firstName=firstName, noticeList=noticeList)


@app.route('/notice', methods=['GET'])
@login_required
@role_required('admin')
def notice():
    firstName = session['firstName']
    return render_template('create_notice.html', firstName=firstName)


@app.route('/notice/create', methods=['POST'])
@login_required
@role_required('admin')
def create_notice():
    firstName = session['firstName']
    title = request.form.get('title')
    description = request.form.get('description')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    data = {
        "title": title,
        "description": description,
        "creation_date_time": dt_string,
        "updated_date_time": None
    }
    firebaseDb.child('noticeBoard').push(json.dumps(data))
    return render_template('notice_success.html', task='Created', firstName=firstName)


@app.route('/notice/edit/<string:key>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_notice(key):
    firstName = session['firstName']
    rawData1 = firebaseDb.child('noticeBoard').child(key).get()
    rawData2 = rawData1.val()
    data = json.loads(rawData2)
    data['key'] = key
    if request.method == 'GET':
        return render_template('edit_notice.html', firstName=firstName, notice=data)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        newData = {
            "title": title,
            "description": description,
            "creation_date_time": data['creation_date_time'],
            "updated_date_time": dt_string
        }
        firebaseDb.child('noticeBoard').child(key).set(json.dumps(newData))
        return render_template('notice_success.html', task='Edited', firstName=firstName)


@app.route('/notice/delete/<string:key>', methods=['GET'])
@login_required
@role_required('admin')
def deleteNotice(key):
    firebaseDb.child('noticeBoard').child(key).remove()
    firstName = session['firstName']
    return render_template('notice_success.html', task='Deleted', firstName=firstName)


@app.route('/user', methods=['GET'])
@login_required
@role_required('admin')
def user():
    firstName = session['firstName']
    return render_template('user.html', firstName=firstName)


@app.route('/user/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def addUser():
    firstName = session['firstName']
    if request.method == 'GET':
        return render_template('add_user.html', firstName=firstName)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        pno = request.form.get('pno')
        email = request.form.get('email')
        role = request.form.get('role')
        print(role)
        roleObj = Role.query.filter_by(name=role).first()
        bytePwd = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashedPwd = bcrypt.hashpw(bytePwd, salt)
        user = User(username=username, password=hashedPwd, firstName=firstname, lastName=lastname, pno=pno, email=email)
        db.session.add(user)
        db.session.commit()
        userRole = UserRole(user_id=user.id, role_id=roleObj.id)
        db.session.add(userRole)
        db.session.commit()
        return render_template('user_success.html', task='Created', firstName=firstName)


@app.route('/user/modify', methods=['POST'])
@login_required
@role_required('admin')
def modifyUser():
    firstName = session['firstName']
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    if user is None:
        return render_template('user.html', firstName=firstName, error='Invalid Username!')
    userRole = UserRole.query.filter_by(user_id=user.id).first()
    role = Role.query.filter_by(id=userRole.role_id).first()
    return render_template('modify_user.html', user=user, firstName=firstName, role=role.name)


@app.route('/user/edit/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def editUser(user_id):
    firstName = session['firstName']
    username = request.form.get('username')
    firstname = request.form.get('firstName')
    lastname = request.form.get('lastName')
    pno = request.form.get('pno')
    email = request.form.get('email')
    role = request.form.get('role')
    user = User.query.filter_by(id=user_id).first()
    if user.username != username:
        check = User.query.filter_by(username=username).first()
        if check is not None:
            return redirect('') # work to be done here
    user.username = username
    user.firstName = firstname
    user.lastName = lastname
    user.pno = pno
    user.email = email
    roleObj = Role.query.filter_by(name=role).first()
    userRole = UserRole.query.filter_by(user_id=user_id).first()
    userRole.role_id = roleObj.id
    db.session.commit()
    return render_template('user_success.html', task="Edited", firstName=firstName)


# ----------------- Teacher --------------------


@app.route('/teacher', methods=['GET'])
@login_required
@role_required('teacher')
def teacher_dash():
    firstName = session['firstName']
    notices = firebaseDb.child('noticeBoard').get()
    rawNoticeList = notices.val()
    if rawNoticeList is None:
        return render_template('teacher_dash.html', firstName=firstName, empty=True)
    noticeList = []
    for i in rawNoticeList.values():
        j = json.loads(i)
        noticeList.append(j)
    noticeList.reverse()
    return render_template('teacher_dash.html', firstName=firstName, noticeList=noticeList)


#
#
# @app.route('/course_teacher', methods=['POST', 'GET'])
# @login_required
# @role_required('teacher')
# def teacher_course():
#     if request.method == 'GET':
#         return render_template('teacher_course_view.html')
#
#     if request.method == 'POST':
#         user_id = session['userId']
#         file = request.files['file']
#         file.os.path.join(app.config['Upload_folder'], secure_filename(file.filename))
#         return render_template('teacher_course_view.html')


# ----------------- Student --------------------

@app.route('/student', methods=['GET'])
@login_required
@role_required('student')
def student_dash():
    firstName = session['firstName']
    notices = firebaseDb.child('noticeBoard').get()
    rawNoticeList = notices.val()
    if rawNoticeList is None:
        return render_template('admin_dash.html', firstName=firstName, empty=True)
    noticeList = []
    for i in rawNoticeList.values():
        j = json.loads(i)
        noticeList.append(j)
    noticeList.reverse()
    return render_template('student_dash.html', firstName=firstName, noticeList=noticeList)


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


@app.route('/student/course', methods=['GET'])
@login_required
@role_required('student')
def student_course():
    if request.method == 'GET':
        user_id = session['userId']
        firstName = session['firstName']
        enrollments = Enrollment.query.filter_by(student_id=user_id).all()
        courseList = []
        for enrollment in enrollments:
            course = Course.query.filter_by(id=enrollment.course_id).first()
            courseList.append(course)
        return render_template('student_course_view.html', courseList, firstName=firstName)


# ----------------- Course ---------------------


# ----------------- Warden ---------------------
@app.route('/warden', methods=['GET'])
@login_required
@role_required('warden')
def warden():
    if request.method == 'GET':
        user_id = session['userId']
        firstName = session['firstname']
        leaveList = Leave.query.filter_by(status='Pending').all()

        return render_template('warden.html', firstName=firstName, leaveList=leaveList)


@app.route('/warden/accept/<int:leave_id>', methods=['GET'])
@login_required
@role_required('warden')
def leave_accept(leave_id):
    target_leave = Leave.query.filter_by(id=leave_id).first()
    target_leave.status = 'Accepted'
    db.session.commit()

    return redirect('/warden')


@app.route('/warden/reject/<int:leave_id>', methods=['GET'])
@login_required
@role_required('warden')
def leave_reject(leave_id):
    target_leave = Leave.query.filter_by(id=leave_id).first()
    target_leave.status = 'Rejected'
    db.session.commit()

    return redirect('/warden')
